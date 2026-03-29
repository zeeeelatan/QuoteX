from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.device_field_config import DeviceFieldConfig
from app.schemas.device_field_config import (
    DeviceFieldConfigCreate, DeviceFieldConfigUpdate,
    DeviceFieldConfigOut, DeviceFieldConfigListResponse,
)

router = APIRouter(prefix="/device-field-configs", tags=["字段配置管理"])


def config_to_dict(c: DeviceFieldConfig) -> dict:
    return {
        "id": c.id,
        "device_type": c.device_type,
        "field_key": c.field_key,
        "field_label": c.field_label,
        "field_type": c.field_type,
        "required": c.required,
        "enum_options": c.enum_options,
        "default_value": c.default_value,
        "display_order": c.display_order,
        "scope": c.scope,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


@router.get("/", response_model=DeviceFieldConfigListResponse)
def list_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    device_type: Optional[str] = Query(None, description="按设备类型筛选（精确匹配单个分类）"),
    scope: Optional[str] = Query(None, description="按作用域筛选: type/instance"),
    db: Session = Depends(get_db),
):
    query = db.query(DeviceFieldConfig)
    if device_type is not None:
        # 返回指定类型的字段 + 全局通用字段（device_type IS NULL）
        query = query.filter(
            (DeviceFieldConfig.device_type == device_type)
            | (DeviceFieldConfig.device_type.is_(None))
        )
    if scope:
        query = query.filter(DeviceFieldConfig.scope == scope)
    total = query.count()
    items = (
        query.order_by(DeviceFieldConfig.device_type, DeviceFieldConfig.display_order)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return DeviceFieldConfigListResponse(
        data=[config_to_dict(c) for c in items],
        total=total,
    )


@router.get("/by-categories", response_model=DeviceFieldConfigListResponse)
def list_configs_by_categories(
    primary_category: Optional[str] = Query(None, description="一级分类"),
    secondary_category: Optional[str] = Query(None, description="二级分类"),
    tertiary_category: Optional[str] = Query(None, description="三级分类"),
    scope: Optional[str] = Query(None, description="按作用域筛选: type/instance"),
    db: Session = Depends(get_db),
):
    """根据设备的一/二/三级分类，返回所有匹配的字段配置。

    匹配规则：返回 device_type 匹配任一分类级别的配置 + 全局配置(device_type IS NULL)。
    例如设备分类为 计算/服务器/X86服务器，会返回 device_type 为
    "计算"、"服务器"、"X86服务器" 以及 NULL(全局) 的所有字段配置。
    """
    # 收集所有非空的分类值
    categories = [c for c in [primary_category, secondary_category, tertiary_category] if c]

    query = db.query(DeviceFieldConfig)

    if categories:
        query = query.filter(
            or_(
                DeviceFieldConfig.device_type.in_(categories),
                DeviceFieldConfig.device_type.is_(None),
            )
        )
    else:
        # 没有传分类时，只返回全局配置
        query = query.filter(DeviceFieldConfig.device_type.is_(None))

    if scope:
        query = query.filter(DeviceFieldConfig.scope == scope)

    items = query.order_by(DeviceFieldConfig.device_type, DeviceFieldConfig.display_order).all()

    # 去重：如果多个分类级别命中了同一个 field_key，保留最具体的那个
    seen_keys: dict[str, dict] = {}
    category_priority = {c: i for i, c in enumerate(reversed(categories))} if categories else {}
    # 三级分类优先级最高，全局最低
    for item in items:
        d = config_to_dict(item)
        key = d["field_key"]
        if key not in seen_keys:
            seen_keys[key] = d
        else:
            existing_type = seen_keys[key]["device_type"]
            new_type = d["device_type"]
            existing_priority = category_priority.get(existing_type, -1) if existing_type else -1
            new_priority = category_priority.get(new_type, -1) if new_type else -1
            if new_priority > existing_priority:
                seen_keys[key] = d

    result = sorted(seen_keys.values(), key=lambda x: x.get("display_order", 0))
    return DeviceFieldConfigListResponse(data=result, total=len(result))


@router.get("/device-types")
def get_device_types(db: Session = Depends(get_db)):
    """获取所有已配置字段的设备类型"""
    types = (
        db.query(DeviceFieldConfig.device_type)
        .filter(DeviceFieldConfig.device_type.isnot(None))
        .distinct()
        .all()
    )
    return [t[0] for t in types if t[0]]


@router.get("/{config_id}", response_model=DeviceFieldConfigOut)
def get_config(config_id: int, db: Session = Depends(get_db)):
    c = db.query(DeviceFieldConfig).filter(DeviceFieldConfig.id == config_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="字段配置不存在")
    return config_to_dict(c)


@router.post("/", response_model=DeviceFieldConfigOut)
def create_config(data: DeviceFieldConfigCreate, db: Session = Depends(get_db)):
    # 同一 device_type 下 field_key 不能重复
    existing = db.query(DeviceFieldConfig).filter(
        DeviceFieldConfig.device_type == data.device_type,
        DeviceFieldConfig.field_key == data.field_key,
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"设备类型 '{data.device_type}' 下已存在字段 '{data.field_key}'",
        )
    now = datetime.now()
    c = DeviceFieldConfig(**data.model_dump(), created_at=now, updated_at=now)
    db.add(c)
    db.commit()
    db.refresh(c)
    return config_to_dict(c)


@router.put("/{config_id}", response_model=DeviceFieldConfigOut)
def update_config(config_id: int, data: DeviceFieldConfigUpdate, db: Session = Depends(get_db)):
    c = db.query(DeviceFieldConfig).filter(DeviceFieldConfig.id == config_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="字段配置不存在")
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(c, k, v)
    c.updated_at = datetime.now()
    db.commit()
    db.refresh(c)
    return config_to_dict(c)


@router.delete("/{config_id}")
def delete_config(config_id: int, db: Session = Depends(get_db)):
    c = db.query(DeviceFieldConfig).filter(DeviceFieldConfig.id == config_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="字段配置不存在")
    db.delete(c)
    db.commit()
    return {"ok": True, "message": "字段配置删除成功"}


@router.post("/batch", response_model=list[DeviceFieldConfigOut])
def batch_create_configs(items: list[DeviceFieldConfigCreate], db: Session = Depends(get_db)):
    """批量创建字段配置"""
    now = datetime.now()
    objs = []
    for data in items:
        c = DeviceFieldConfig(**data.model_dump(), created_at=now, updated_at=now)
        db.add(c)
        objs.append(c)
    db.commit()
    for c in objs:
        db.refresh(c)
    return [config_to_dict(c) for c in objs]
