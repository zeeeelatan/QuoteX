from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.manufacturer import Manufacturer
from app.schemas.manufacturer import (
    ManufacturerCreate, ManufacturerUpdate, ManufacturerOut, ManufacturerListResponse
)
from app.matching import invalidate_manufacturer_cache

router = APIRouter(prefix="/manufacturers", tags=["品牌管理"])


def manufacturer_to_dict(m: Manufacturer) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "aliases": m.aliases or [],
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }


@router.get("/", response_model=ManufacturerListResponse)
def list_manufacturers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="搜索品牌名称或别名"),
    db: Session = Depends(get_db),
):
    query = db.query(Manufacturer)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Manufacturer.name.ilike(pattern)
            | Manufacturer.aliases.cast(str).ilike(pattern)
        )
    total = query.count()
    items = query.order_by(Manufacturer.name).offset(skip).limit(limit).all()
    return ManufacturerListResponse(
        data=[manufacturer_to_dict(m) for m in items],
        total=total,
    )


@router.get("/all")
def get_all_manufacturers(db: Session = Depends(get_db)):
    """获取所有品牌（不分页，用于下拉选择）"""
    items = db.query(Manufacturer).order_by(Manufacturer.name).all()
    return [manufacturer_to_dict(m) for m in items]


@router.get("/{manufacturer_id}", response_model=ManufacturerOut)
def get_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    m = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="品牌不存在")
    return manufacturer_to_dict(m)


@router.post("/", response_model=ManufacturerOut)
def create_manufacturer(data: ManufacturerCreate, db: Session = Depends(get_db)):
    from sqlalchemy import func
    existing = db.query(Manufacturer).filter(
        func.lower(Manufacturer.name) == data.name.strip().lower()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"品牌 '{data.name}' 已存在（已有: {existing.name}）")
    now = datetime.now()
    m = Manufacturer(
        name=data.name,
        aliases=data.aliases,
        created_at=now,
        updated_at=now,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    invalidate_manufacturer_cache()
    return manufacturer_to_dict(m)


@router.put("/{manufacturer_id}", response_model=ManufacturerOut)
def update_manufacturer(manufacturer_id: int, data: ManufacturerUpdate, db: Session = Depends(get_db)):
    m = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="品牌不存在")
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        from sqlalchemy import func
        dup = db.query(Manufacturer).filter(
            func.lower(Manufacturer.name) == update_data["name"].strip().lower(),
            Manufacturer.id != manufacturer_id,
        ).first()
        if dup:
            raise HTTPException(status_code=400, detail=f"品牌 '{update_data['name']}' 已存在（已有: {dup.name}）")
    for k, v in update_data.items():
        setattr(m, k, v)
    m.updated_at = datetime.now()
    db.commit()
    db.refresh(m)
    invalidate_manufacturer_cache()
    return manufacturer_to_dict(m)


@router.delete("/{manufacturer_id}")
def delete_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    m = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="品牌不存在")
    db.delete(m)
    db.commit()
    invalidate_manufacturer_cache()
    return {"ok": True, "message": "品牌删除成功"}


@router.post("/{manufacturer_id}/aliases")
def add_alias(manufacturer_id: int, alias: str = Query(...), db: Session = Depends(get_db)):
    """给品牌添加一个别名"""
    m = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="品牌不存在")
    aliases = list(m.aliases or [])
    if alias not in aliases:
        aliases.append(alias)
        m.aliases = aliases
        m.updated_at = datetime.now()
        db.commit()
        db.refresh(m)
        invalidate_manufacturer_cache()
    return manufacturer_to_dict(m)


@router.delete("/{manufacturer_id}/aliases")
def remove_alias(manufacturer_id: int, alias: str = Query(...), db: Session = Depends(get_db)):
    """移除品牌的一个别名"""
    m = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="品牌不存在")
    aliases = list(m.aliases or [])
    if alias in aliases:
        aliases.remove(alias)
        m.aliases = aliases
        m.updated_at = datetime.now()
        db.commit()
        db.refresh(m)
        invalidate_manufacturer_cache()
    return manufacturer_to_dict(m)


def resolve_manufacturer(db: Session, raw_name: str) -> Optional[Manufacturer]:
    """根据品牌名或别名查找对应的品牌字典记录。
    匹配逻辑：标准名精确匹配 → 别名包含匹配（不区分大小写）。
    """
    if not raw_name:
        return None
    raw_lower = raw_name.strip().lower()

    # 1. 标准名精确匹配（不区分大小写）
    m = db.query(Manufacturer).filter(
        Manufacturer.name.ilike(raw_lower)
    ).first()
    if m:
        return m

    # 2. 遍历所有品牌的 aliases 做不区分大小写匹配
    all_manufacturers = db.query(Manufacturer).all()
    for mfr in all_manufacturers:
        for alias in (mfr.aliases or []):
            if str(alias).strip().lower() == raw_lower:
                return mfr

    return None
