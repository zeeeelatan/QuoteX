"""
派单服务数据路由
提供派单服务数据的增删改查接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.dispatch_service import (
    DispatchServiceCreate,
    DispatchServiceUpdate,
    DispatchServiceOut
)
from app.models.dispatch_service import DispatchService
from app.database import get_db

router = APIRouter(prefix="/dispatch-service", tags=["派单服务数据管理"])


@router.get("/", response_model=List[DispatchServiceOut])
def list_dispatch_services(
    service_type: Optional[str] = None,
    unit_hours: Optional[str] = None,
    city_tier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取派单服务列表，支持筛选"""
    query = db.query(DispatchService)

    if service_type:
        query = query.filter(DispatchService.service_type == service_type)
    if unit_hours:
        query = query.filter(DispatchService.unit_hours == unit_hours)
    if city_tier:
        query = query.filter(DispatchService.city_tier == city_tier)

    return query.order_by(
        DispatchService.unit_hours,
        DispatchService.time_window,
        DispatchService.service_type,
        DispatchService.city_tier
    ).all()


@router.get("/options/service-types")
def get_service_types(db: Session = Depends(get_db)):
    """获取所有服务类型"""
    types = db.query(DispatchService.service_type).distinct().all()
    return {"service_types": [t[0] for t in types]}


@router.get("/options/unit-hours")
def get_unit_hours(db: Session = Depends(get_db)):
    """获取所有单位工时"""
    hours = db.query(DispatchService.unit_hours).distinct().all()
    return {"unit_hours": [h[0] for h in hours]}


@router.get("/options/time-windows")
def get_time_windows(db: Session = Depends(get_db)):
    """获取所有时间窗口"""
    windows = db.query(DispatchService.time_window).distinct().all()
    return {"time_windows": [w[0] for w in windows]}


@router.get("/options/response-times")
def get_response_times(db: Session = Depends(get_db)):
    """获取所有响应时效"""
    times = db.query(DispatchService.response_time).distinct().all()
    return {"response_times": [t[0] for t in times]}


@router.get("/options/city-tiers")
def get_city_tiers(db: Session = Depends(get_db)):
    """获取所有城市等级"""
    tiers = db.query(DispatchService.city_tier).distinct().all()
    return {"city_tiers": [t[0] for t in tiers]}


@router.get("/{service_id}", response_model=DispatchServiceOut)
def get_dispatch_service(service_id: int, db: Session = Depends(get_db)):
    """获取单条派单服务数据"""
    service = db.query(DispatchService).filter(DispatchService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="派单服务数据不存在")
    return service


@router.post("/", response_model=DispatchServiceOut)
def create_dispatch_service(service: DispatchServiceCreate, db: Session = Depends(get_db)):
    """创建派单服务数据"""
    db_service = DispatchService(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.post("/batch-create")
def batch_create_dispatch_services(data: dict, db: Session = Depends(get_db)):
    """批量创建派单服务数据"""
    try:
        records = data.get("records", [])
        created = []
        for record in records:
            db_service = DispatchService(**record)
            db.add(db_service)
            created.append(db_service)
        db.commit()
        for item in created:
            db.refresh(item)
        return {"message": f"成功创建 {len(created)} 条数据", "count": len(created)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{service_id}", response_model=DispatchServiceOut)
def update_dispatch_service(
    service_id: int,
    service: DispatchServiceUpdate,
    db: Session = Depends(get_db)
):
    """更新派单服务数据"""
    db_service = db.query(DispatchService).filter(DispatchService.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="派单服务数据不存在")

    for k, v in service.model_dump(exclude_unset=True).items():
        setattr(db_service, k, v)

    db.commit()
    db.refresh(db_service)
    return db_service


@router.delete("/{service_id}")
def delete_dispatch_service(service_id: int, db: Session = Depends(get_db)):
    """删除派单服务数据"""
    db_service = db.query(DispatchService).filter(DispatchService.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="派单服务数据不存在")

    db.delete(db_service)
    db.commit()
    return {"ok": True}


@router.delete("/clear")
def clear_dispatch_services(db: Session = Depends(get_db)):
    """清空所有派单服务数据"""
    try:
        db.query(DispatchService).delete()
        db.commit()
        return {"message": "所有派单服务数据已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
