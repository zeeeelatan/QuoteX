from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.single_service import (
    SingleServiceCreate,
    SingleServiceUpdate,
    SingleServiceOut
)
from app.models.single_service import SingleService
from app.database import get_db

router = APIRouter(prefix="/single-service", tags=["单次服务数据管理"])


@router.get("/", response_model=List[SingleServiceOut])
def list_single_services(
    business_type: Optional[str] = None,
    service_name: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取单次服务列表，支持筛选和搜索"""
    query = db.query(SingleService)

    if business_type:
        query = query.filter(SingleService.business_type == business_type)
    if service_name:
        query = query.filter(SingleService.service_name == service_name)
    if search:
        query = query.filter(
            (SingleService.business_type.contains(search)) |
            (SingleService.service_name.contains(search)) |
            (SingleService.service_detail.contains(search)) |
            (SingleService.device_type.contains(search))
        )

    return query.order_by(SingleService.id).all()


@router.get("/{service_id}", response_model=SingleServiceOut)
def get_single_service(service_id: int, db: Session = Depends(get_db)):
    """获取单个单次服务详情"""
    service = db.query(SingleService).filter(SingleService.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="单次服务不存在")
    return service


@router.post("/", response_model=SingleServiceOut)
def create_single_service(service: SingleServiceCreate, db: Session = Depends(get_db)):
    """创建单次服务"""
    db_service = SingleService(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.put("/{service_id}", response_model=SingleServiceOut)
def update_single_service(
    service_id: int,
    service: SingleServiceUpdate,
    db: Session = Depends(get_db)
):
    """更新单次服务"""
    db_service = db.query(SingleService).filter(SingleService.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="单次服务不存在")

    for k, v in service.dict(exclude_unset=True).items():
        setattr(db_service, k, v)

    db.commit()
    db.refresh(db_service)
    return db_service


@router.delete("/{service_id}")
def delete_single_service(service_id: int, db: Session = Depends(get_db)):
    """删除单次服务"""
    db_service = db.query(SingleService).filter(SingleService.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="单次服务不存在")

    db.delete(db_service)
    db.commit()
    return {"ok": True}


@router.delete("/clear")
def clear_single_services(db: Session = Depends(get_db)):
    """清空所有单次服务数据"""
    try:
        db.query(SingleService).delete()
        db.commit()
        return {"message": "所有单次服务数据已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/business-types/list")
def get_business_types(db: Session = Depends(get_db)):
    """获取所有业务类型列表"""
    types = db.query(SingleService.business_type).distinct().all()
    return {"business_types": [t[0] for t in types]}


@router.get("/service-names/list")
def get_service_names(db: Session = Depends(get_db)):
    """获取所有服务名称列表"""
    names = db.query(SingleService.service_name).distinct().all()
    return {"service_names": [n[0] for n in names]}
