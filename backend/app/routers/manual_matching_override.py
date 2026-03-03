"""
手动匹配覆盖 API 路由
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from pydantic import BaseModel

from app.database import get_db
from app.models.manual_matching_override import ManualMatchingOverride
from app.schemas.manual_matching_override import (
    ManualMatchingOverrideCreate,
    ManualMatchingOverrideUpdate,
    ManualMatchingOverrideResponse,
    ManualMatchingOverrideList,
    ManualMatchRecord
)

router = APIRouter(prefix="/manual-matching-override", tags=["手动匹配覆盖"])


# 新增 Schema：确认冲突检查响应
class ConflictCheckResponse(BaseModel):
    has_conflict: bool  # 是否有冲突
    conflict_type: Optional[str] = None  # 冲突类型: "empty_model", "duplicate"
    existing_record: Optional[Dict[str, Any]] = None  # 冲突的现有记录


# 新增 Schema：带覆盖选项的确认请求
class ConfirmWithOverrideRequest(BaseModel):
    override: bool = False  # 是否覆盖现有数据


@router.post("/", response_model=ManualMatchingOverrideResponse)
def create_manual_override(
    data: ManualMatchingOverrideCreate,
    db: Session = Depends(get_db)
):
    """
    创建单条手动匹配覆盖记录
    """
    # 检查是否已存在相同的原始厂商+型号组合
    existing = db.query(ManualMatchingOverride).filter(
        and_(
            ManualMatchingOverride.original_manufacturer == data.original_manufacturer,
            ManualMatchingOverride.original_model == data.original_model
        )
    ).first()

    if existing:
        # 如果存在，更新匹配结果
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    # 创建新记录
    db_data = ManualMatchingOverride(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


@router.post("/batch", response_model=List[ManualMatchingOverrideResponse])
def create_manual_overrides_batch(
    records: List[ManualMatchRecord],
    db: Session = Depends(get_db)
):
    """
    批量创建手动匹配覆盖记录
    用于智能匹配页面提交手动调整结果
    """
    results = []
    for record in records:
        # 检查是否已存在
        existing = db.query(ManualMatchingOverride).filter(
            and_(
                ManualMatchingOverride.original_manufacturer == record.original_manufacturer,
                ManualMatchingOverride.original_model == record.original_model
            )
        ).first()

        if existing:
            # 更新现有记录
            for key, value in record.model_dump(exclude_unset=True).items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            results.append(existing)
        else:
            # 创建新记录
            db_data = ManualMatchingOverride(**record.model_dump())
            db.add(db_data)
            db.commit()
            db.refresh(db_data)
            results.append(db_data)

    return results


@router.get("/", response_model=List[ManualMatchingOverrideList])
def get_manual_overrides(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_confirmed: Optional[bool] = Query(None, description="筛选确认状态"),
    search: Optional[str] = Query(None, description="搜索原始厂商或型号"),
    db: Session = Depends(get_db)
):
    """
    获取手动匹配覆盖列表
    """
    query = db.query(ManualMatchingOverride)

    # 筛选确认状态
    if is_confirmed is not None:
        query = query.filter(ManualMatchingOverride.is_confirmed == is_confirmed)

    # 搜索
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                ManualMatchingOverride.original_manufacturer.ilike(search_pattern),
                ManualMatchingOverride.original_model.ilike(search_pattern),
                ManualMatchingOverride.matched_model_number.ilike(search_pattern)
            )
        )

    # 排序：未确认的在前，然后按创建时间倒序
    query = query.order_by(
        ManualMatchingOverride.is_confirmed.asc(),
        ManualMatchingOverride.created_at.desc()
    )

    results = query.offset(skip).limit(limit).all()
    return results


@router.get("/count")
def get_manual_overrides_count(
    is_confirmed: Optional[bool] = Query(None, description="筛选确认状态"),
    db: Session = Depends(get_db)
):
    """
    获取手动匹配覆盖记录数量
    """
    query = db.query(ManualMatchingOverride)

    if is_confirmed is not None:
        query = query.filter(ManualMatchingOverride.is_confirmed == is_confirmed)

    count = query.count()
    return {"total": count}


@router.get("/{override_id}", response_model=ManualMatchingOverrideResponse)
def get_manual_override(
    override_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单条手动匹配覆盖记录
    """
    db_data = db.query(ManualMatchingOverride).filter(
        ManualMatchingOverride.id == override_id
    ).first()

    if not db_data:
        raise HTTPException(status_code=404, detail="记录不存在")

    return db_data


@router.put("/{override_id}", response_model=ManualMatchingOverrideResponse)
def update_manual_override(
    override_id: int,
    data: ManualMatchingOverrideUpdate,
    db: Session = Depends(get_db)
):
    """
    更新手动匹配覆盖记录
    """
    db_data = db.query(ManualMatchingOverride).filter(
        ManualMatchingOverride.id == override_id
    ).first()

    if not db_data:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 如果确认状态从 False 变为 True，设置确认时间
    if data.is_confirmed is True and db_data.is_confirmed is False:
        db_data.confirmed_at = datetime.utcnow()

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_data, key, value)

    db.commit()
    db.refresh(db_data)
    return db_data


@router.get("/{override_id}/confirm-check", response_model=ConflictCheckResponse)
def check_confirm_conflict(
    override_id: int,
    db: Session = Depends(get_db)
):
    """
    确认前检查冲突
    检查：
    1. 原始型号是否为空
    2. 是否存在相同的原始厂商+原始型号组合（已确认的记录）
    """
    db_data = db.query(ManualMatchingOverride).filter(
        ManualMatchingOverride.id == override_id
    ).first()

    if not db_data:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 检查1：原始型号不能为空
    if not db_data.original_model or not db_data.original_model.strip():
        return ConflictCheckResponse(
            has_conflict=True,
            conflict_type="empty_model",
            existing_record=None
        )

    # 检查2：是否存在相同的原始厂商+原始型号组合（排除当前记录，只检查已确认的）
    existing = db.query(ManualMatchingOverride).filter(
        and_(
            ManualMatchingOverride.original_manufacturer == db_data.original_manufacturer,
            ManualMatchingOverride.original_model == db_data.original_model,
            ManualMatchingOverride.id != override_id,
            ManualMatchingOverride.is_confirmed == True  # 只检查已确认的记录
        )
    ).first()

    if existing:
        return ConflictCheckResponse(
            has_conflict=True,
            conflict_type="duplicate",
            existing_record={
                "id": existing.id,
                "original_manufacturer": existing.original_manufacturer,
                "original_model": existing.original_model,
                "matched_manufacturer": existing.matched_manufacturer,
                "matched_model_number": existing.matched_model_number,
                "device_price": existing.device_price
            }
        )

    return ConflictCheckResponse(has_conflict=False)


@router.patch("/{override_id}/confirm", response_model=ManualMatchingOverrideResponse)
def confirm_manual_override(
    override_id: int,
    override: bool = Query(False, description="是否覆盖现有相同数据"),
    db: Session = Depends(get_db)
):
    """
    确认手动匹配覆盖记录
    确认后的记录将作为正式的手动匹配库数据

    参数：
    - override: 如果为 True，会删除现有相同的数据（如果有）
    """
    db_data = db.query(ManualMatchingOverride).filter(
        ManualMatchingOverride.id == override_id
    ).first()

    if not db_data:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 验证：原始型号不能为空
    if not db_data.original_model or not db_data.original_model.strip():
        raise HTTPException(status_code=400, detail="原始型号不能为空")

    # 检查是否存在相同的原始厂商+原始型号组合（已确认的）
    existing = db.query(ManualMatchingOverride).filter(
        and_(
            ManualMatchingOverride.original_manufacturer == db_data.original_manufacturer,
            ManualMatchingOverride.original_model == db_data.original_model,
            ManualMatchingOverride.id != override_id,
            ManualMatchingOverride.is_confirmed == True
        )
    ).first()

    if existing:
        if override:
            # 覆盖：删除现有记录
            db.delete(existing)
            db.commit()
        else:
            # 不覆盖：返回错误，不确认新记录
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "conflict",
                    "message": "存在相同的原始厂商+型号组合",
                    "existing_id": existing.id
                }
            )

    # 确认当前记录
    db_data.is_confirmed = True
    db_data.confirmed_at = datetime.utcnow()
    db.commit()
    db.refresh(db_data)
    return db_data


@router.patch("/batch-confirm", response_model=List[ManualMatchingOverrideResponse])
def confirm_manual_overrides_batch(
    override_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    批量确认手动匹配覆盖记录
    """
    results = []
    for override_id in override_ids:
        db_data = db.query(ManualMatchingOverride).filter(
            ManualMatchingOverride.id == override_id
        ).first()

        if db_data:
            db_data.is_confirmed = True
            db_data.confirmed_at = datetime.utcnow()
            db.commit()
            db.refresh(db_data)
            results.append(db_data)

    return results


@router.delete("/{override_id}")
def delete_manual_override(
    override_id: int,
    db: Session = Depends(get_db)
):
    """
    删除手动匹配覆盖记录
    """
    db_data = db.query(ManualMatchingOverride).filter(
        ManualMatchingOverride.id == override_id
    ).first()

    if not db_data:
        raise HTTPException(status_code=404, detail="记录不存在")

    db.delete(db_data)
    db.commit()
    return {"message": "删除成功"}


@router.post("/check-match")
def check_manual_match(
    original_manufacturer: str,
    original_model: str,
    data_source: str = "datacenter",
    db: Session = Depends(get_db)
):
    """
    检查是否存在手动匹配覆盖记录
    如果存在，返回手动匹配结果
    优先返回已确认的记录
    """
    # 先查找已确认的记录
    confirmed = db.query(ManualMatchingOverride).filter(
        and_(
            ManualMatchingOverride.original_manufacturer == original_manufacturer,
            ManualMatchingOverride.original_model == original_model,
            ManualMatchingOverride.is_confirmed == True
        )
    ).order_by(ManualMatchingOverride.created_at.desc()).first()

    if confirmed:
        return {
            "found": True,
            "data": {
                "matched_model": confirmed.matched_model_number,
                "matched_manufacturer": confirmed.matched_manufacturer,
                "device_price": confirmed.device_price,
                "primary_category": confirmed.primary_category,
                "secondary_category": confirmed.secondary_category,
                "tertiary_category": confirmed.tertiary_category,
                "device_category": confirmed.device_category,
                "match_rate": 100,  # 手动匹配给予最高置信度
                "source": "manual_override"
            }
        }

    # 再查找未确认的记录
    unconfirmed = db.query(ManualMatchingOverride).filter(
        and_(
            ManualMatchingOverride.original_manufacturer == original_manufacturer,
            ManualMatchingOverride.original_model == original_model
        )
    ).order_by(ManualMatchingOverride.created_at.desc()).first()

    if unconfirmed:
        return {
            "found": True,
            "data": {
                "matched_model": unconfirmed.matched_model_number,
                "matched_manufacturer": unconfirmed.matched_manufacturer,
                "device_price": unconfirmed.device_price,
                "primary_category": unconfirmed.primary_category,
                "secondary_category": unconfirmed.secondary_category,
                "tertiary_category": unconfirmed.tertiary_category,
                "device_category": unconfirmed.device_category,
                "match_rate": 100,
                "source": "manual_override_pending"
            }
        }

    return {"found": False}
