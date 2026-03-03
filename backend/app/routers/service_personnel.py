from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.service_personnel import (
    ServicePersonnelCreate,
    ServicePersonnelUpdate,
    ServicePersonnelOut
)
from app.models.service_personnel import ServicePersonnel
from app.database import get_db

router = APIRouter(prefix="/service_personnel", tags=["服务人员数据管理"])


@router.get("/", response_model=List[ServicePersonnelOut])
def list_service_personnel(
    personnel_type: Optional[str] = None,
    skill_level: Optional[str] = None,
    service_mode: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取服务人员列表，支持筛选和搜索"""
    query = db.query(ServicePersonnel)

    if personnel_type:
        query = query.filter(ServicePersonnel.personnel_type == personnel_type)
    if skill_level:
        query = query.filter(ServicePersonnel.skill_level == skill_level)
    if service_mode:
        query = query.filter(ServicePersonnel.service_mode == service_mode)
    if search:
        query = query.filter(
            (ServicePersonnel.personnel_type.contains(search)) |
            (ServicePersonnel.skill_description.contains(search)) |
            (ServicePersonnel.tags.contains(search))
        )

    return query.order_by(ServicePersonnel.personnel_type, ServicePersonnel.skill_level).all()


@router.get("/{personnel_id}", response_model=ServicePersonnelOut)
def get_service_personnel(personnel_id: int, db: Session = Depends(get_db)):
    """获取单个服务人员详情"""
    personnel = db.query(ServicePersonnel).filter(ServicePersonnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="服务人员不存在")
    return personnel


@router.post("/", response_model=ServicePersonnelOut)
def create_service_personnel(personnel: ServicePersonnelCreate, db: Session = Depends(get_db)):
    """创建服务人员"""
    db_personnel = ServicePersonnel(**personnel.dict())
    db.add(db_personnel)
    db.commit()
    db.refresh(db_personnel)
    return db_personnel


@router.put("/{personnel_id}", response_model=ServicePersonnelOut)
def update_service_personnel(
    personnel_id: int,
    personnel: ServicePersonnelUpdate,
    db: Session = Depends(get_db)
):
    """更新服务人员"""
    db_personnel = db.query(ServicePersonnel).filter(ServicePersonnel.id == personnel_id).first()
    if not db_personnel:
        raise HTTPException(status_code=404, detail="服务人员不存在")

    for k, v in personnel.dict(exclude_unset=True).items():
        setattr(db_personnel, k, v)

    db.commit()
    db.refresh(db_personnel)
    return db_personnel


@router.delete("/{personnel_id}")
def delete_service_personnel(personnel_id: int, db: Session = Depends(get_db)):
    """删除服务人员"""
    db_personnel = db.query(ServicePersonnel).filter(ServicePersonnel.id == personnel_id).first()
    if not db_personnel:
        raise HTTPException(status_code=404, detail="服务人员不存在")

    db.delete(db_personnel)
    db.commit()
    return {"ok": True}


@router.get("/types/list")
def get_personnel_types(db: Session = Depends(get_db)):
    """获取所有服务人员类型列表"""
    types = db.query(ServicePersonnel.personnel_type).distinct().all()
    return {"types": [t[0] for t in types]}


@router.get("/levels/list")
def get_skill_levels(db: Session = Depends(get_db)):
    """获取所有能力级别列表"""
    levels = db.query(ServicePersonnel.skill_level).distinct().order_by(ServicePersonnel.skill_level).all()
    return {"levels": [l[0] for l in levels]}


@router.post("/import")
def import_service_personnel(file_path: str, db: Session = Depends(get_db)):
    """从Excel导入服务人员数据"""
    import pandas as pd

    df = pd.read_excel(file_path)

    created_count = 0
    for _, row in df.iterrows():
        # 检查是否已存在相同记录
        existing = db.query(ServicePersonnel).filter(
            ServicePersonnel.personnel_type == row['服务人员类型'],
            ServicePersonnel.skill_level == row['工程师能力级别'],
            ServicePersonnel.service_mode == row['服务模式']
        ).first()

        if not existing:
            db_personnel = ServicePersonnel(
                personnel_type=row['服务人员类型'],
                skill_description=row.get('技能描述') if pd.notna(row.get('技能描述')) else None,
                skill_level=row['工程师能力级别'],
                service_mode=row['服务模式'],
                daily_rate=float(row['人天单价']),
                tags=row.get('标签') if pd.notna(row.get('标签')) else '人天'
            )
            db.add(db_personnel)
            created_count += 1

    db.commit()
    return {"message": f"成功导入 {created_count} 条记录", "created_count": created_count}
