from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.outsourced_personnel import (
    OutsourcedPersonnelCreate,
    OutsourcedPersonnelUpdate,
    OutsourcedPersonnelOut
)
from app.models.outsourced_personnel import OutsourcedPersonnel
from app.database import get_db

router = APIRouter(prefix="/outsourced-personnel", tags=["外包人员岗位及薪资管理"])


@router.get("/", response_model=List[OutsourcedPersonnelOut])
def list_outsourced_personnel(
    position: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取外包人员列表，支持筛选和搜索"""
    query = db.query(OutsourcedPersonnel)

    if position:
        query = query.filter(OutsourcedPersonnel.position == position)
    if level:
        query = query.filter(OutsourcedPersonnel.level == level)
    if search:
        query = query.filter(
            (OutsourcedPersonnel.position.contains(search)) |
            (OutsourcedPersonnel.level.contains(search)) |
            (OutsourcedPersonnel.general_ability.contains(search)) |
            (OutsourcedPersonnel.technical_skill.contains(search))
        )

    return query.order_by(OutsourcedPersonnel.id).all()


@router.get("/positions/list")
def get_positions(db: Session = Depends(get_db)):
    """获取所有岗位列表"""
    positions = db.query(OutsourcedPersonnel.position).distinct().all()
    return {"positions": [p[0] for p in positions]}


@router.get("/levels/list")
def get_levels(db: Session = Depends(get_db)):
    """获取所有级别列表"""
    levels = db.query(OutsourcedPersonnel.level).distinct().all()
    return {"levels": [l[0] for l in levels]}


@router.get("/{personnel_id}", response_model=OutsourcedPersonnelOut)
def get_outsourced_personnel(personnel_id: int, db: Session = Depends(get_db)):
    """获取单个外包人员详情"""
    personnel = db.query(OutsourcedPersonnel).filter(OutsourcedPersonnel.id == personnel_id).first()
    if not personnel:
        raise HTTPException(status_code=404, detail="外包人员数据不存在")
    return personnel


@router.post("/", response_model=OutsourcedPersonnelOut)
def create_outsourced_personnel(personnel: OutsourcedPersonnelCreate, db: Session = Depends(get_db)):
    """创建外包人员数据"""
    db_personnel = OutsourcedPersonnel(**personnel.dict())
    db.add(db_personnel)
    db.commit()
    db.refresh(db_personnel)
    return db_personnel


@router.put("/{personnel_id}", response_model=OutsourcedPersonnelOut)
def update_outsourced_personnel(
    personnel_id: int,
    personnel: OutsourcedPersonnelUpdate,
    db: Session = Depends(get_db)
):
    """更新外包人员数据"""
    db_personnel = db.query(OutsourcedPersonnel).filter(OutsourcedPersonnel.id == personnel_id).first()
    if not db_personnel:
        raise HTTPException(status_code=404, detail="外包人员数据不存在")

    for k, v in personnel.dict(exclude_unset=True).items():
        setattr(db_personnel, k, v)

    db.commit()
    db.refresh(db_personnel)
    return db_personnel


@router.delete("/{personnel_id}")
def delete_outsourced_personnel(personnel_id: int, db: Session = Depends(get_db)):
    """删除外包人员数据"""
    db_personnel = db.query(OutsourcedPersonnel).filter(OutsourcedPersonnel.id == personnel_id).first()
    if not db_personnel:
        raise HTTPException(status_code=404, detail="外包人员数据不存在")

    db.delete(db_personnel)
    db.commit()
    return {"ok": True}


@router.delete("/clear")
def clear_outsourced_personnel(db: Session = Depends(get_db)):
    """清空所有外包人员数据"""
    try:
        db.query(OutsourcedPersonnel).delete()
        db.commit()
        return {"message": "所有外包人员数据已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch-create")
def batch_create_outsourced_personnel(data: dict, db: Session = Depends(get_db)):
    """批量创建外包人员数据"""
    try:
        records = data.get("records", [])
        created = []
        for record in records:
            db_personnel = OutsourcedPersonnel(**record)
            db.add(db_personnel)
            created.append(db_personnel)
        db.commit()
        for item in created:
            db.refresh(item)
        return {"message": f"成功创建 {len(created)} 条数据", "count": len(created)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import")
def import_outsourced_personnel(file_path: str, db: Session = Depends(get_db)):
    """从Excel导入外包人员数据"""
    import pandas as pd

    try:
        df = pd.read_excel(file_path)

        # 清空现有数据
        db.query(OutsourcedPersonnel).delete()

        # 填充空值（forward fill 用于岗位和级别）
        df['岗位'].fillna(method='ffill', inplace=True)
        df['级别'].fillna(method='ffill', inplace=True)

        imported_count = 0
        for _, row in df.iterrows():
            # 跳过完全空的行
            if pd.isna(row['岗位']) and pd.isna(row['级别']):
                continue

            personnel = OutsourcedPersonnel(
                position=row['岗位'] if pd.notna(row['岗位']) else '',
                level=row['级别'] if pd.notna(row['级别']) else '',
                subtype=str(row['Unnamed: 2']) if pd.notna(row['Unnamed: 2']) else None,
                education=row['学历'] if pd.notna(row['学历']) else '',
                language_requirement=row['语言要求'] if pd.notna(row['语言要求']) else '',
                work_experience=row['工作经验'] if pd.notna(row['工作经验']) else None,
                general_ability=row['通用能力要求'] if pd.notna(row['通用能力要求']) else None,
                technical_skill=row['专业技术要求'] if pd.notna(row['专业技术要求']) else None,
                tier1_city_salary=float(row['一线城市\n参考月工资']) if pd.notna(row['一线城市\n参考月工资']) else None
            )
            db.add(personnel)
            imported_count += 1

        db.commit()
        return {"message": f"成功导入 {imported_count} 条数据"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")
