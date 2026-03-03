"""
城市社保基准数据路由
提供城市社保基准数据的增删改查接口
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd

from app.schemas.city_social_insurance import (
    CitySocialInsuranceCreate,
    CitySocialInsuranceUpdate,
    CitySocialInsuranceOut
)
from app.models.city_social_insurance import CitySocialInsurance
from app.database import get_db

router = APIRouter(prefix="/city-social-insurance", tags=["城市社保基准数据管理"])


@router.get("/", response_model=List[CitySocialInsuranceOut])
def list_city_social_insurance(
    search: Optional[str] = None,
    province: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取城市社保基准列表，支持搜索和筛选"""
    query = db.query(CitySocialInsurance)

    if search:
        query = query.filter(
            (CitySocialInsurance.city.contains(search)) |
            (CitySocialInsurance.province.contains(search)) |
            (CitySocialInsurance.city_alias.contains(search))
        )

    if province:
        query = query.filter(CitySocialInsurance.province == province)

    if city:
        query = query.filter(CitySocialInsurance.city == city)

    return query.order_by(CitySocialInsurance.province, CitySocialInsurance.city).all()


@router.get("/provinces", response_model=List[str])
def get_provinces(db: Session = Depends(get_db)):
    """获取所有省份列表"""
    provinces = db.query(CitySocialInsurance.province).distinct().all()
    return [p[0] for p in provinces]


@router.get("/cities", response_model=List[str])
def get_cities(province: Optional[str] = None, db: Session = Depends(get_db)):
    """获取所有城市列表"""
    query = db.query(CitySocialInsurance.city).distinct()
    if province:
        # 使用 join 或者子查询获取对应省份的城市
        query = query.filter(CitySocialInsurance.province == province)
    cities = query.all()
    return [c[0] for c in cities]


@router.get("/{record_id}", response_model=CitySocialInsuranceOut)
def get_city_social_insurance(record_id: int, db: Session = Depends(get_db)):
    """获取单条城市社保基准数据"""
    record = db.query(CitySocialInsurance).filter(CitySocialInsurance.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="数据不存在")
    return record


@router.get("/city/{city_name}", response_model=CitySocialInsuranceOut)
def get_by_city_name(city_name: str, db: Session = Depends(get_db)):
    """根据城市名称获取社保基准数据"""
    record = db.query(CitySocialInsurance).filter(
        (CitySocialInsurance.city == city_name) | (CitySocialInsurance.city_alias == city_name)
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"城市 {city_name} 的社保数据不存在")
    return record


@router.post("/", response_model=CitySocialInsuranceOut)
def create_city_social_insurance(record: CitySocialInsuranceCreate, db: Session = Depends(get_db)):
    """创建城市社保基准数据"""
    db_record = CitySocialInsurance(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.post("/batch-create")
def batch_create_city_social_insurance(data: dict, db: Session = Depends(get_db)):
    """批量创建城市社保基准数据"""
    try:
        records = data.get("records", [])
        created = []
        for record_data in records:
            db_record = CitySocialInsurance(**record_data)
            db.add(db_record)
            created.append(db_record)
        db.commit()
        for item in created:
            db.refresh(item)
        return {"message": f"成功创建 {len(created)} 条数据", "count": len(created)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import-excel")
def import_excel(file: UploadFile, db: Session = Depends(get_db)):
    """导入Excel文件"""
    try:
        # Read Excel file
        df = pd.read_excel(file.file.read(), header=None)

        # Parse data (skip first 3 header rows)
        records = []
        for idx, row in df.iterrows():
            if idx < 3:  # Skip header rows
                continue

            province = row[0] if pd.notna(row[0]) else None
            city = row[1] if pd.notna(row[1]) else None

            if not province or not city:
                continue

            record_data = {
                "province": str(province),
                "city": str(city),
                "city_alias": str(city) if city != row[1] else None,
                "upper_limit": int(row[2]) if pd.notna(row[2]) else 0,
                "lower_limit": int(row[3]) if pd.notna(row[3]) else 0,
                "calc_base": int(row[4]) if pd.notna(row[4]) else 0,
                "injury_base": int(row[5]) if pd.notna(row[5]) else None,
                "corp_pension_rate": float(row[6]) if pd.notna(row[6]) else None,
                "corp_medical_rate": float(row[7]) if pd.notna(row[7]) else None,
                "corp_injury_rate": float(row[8]) if pd.notna(row[8]) else None,
                "corp_maternity_rate": float(row[9]) if pd.notna(row[9]) else None,
                "corp_unemployment_rate": float(row[10]) if pd.notna(row[10]) else None,
                "corp_disability_rate": float(row[11]) if pd.notna(row[11]) else None,
                "corp_fund_rate": float(row[13]) if pd.notna(row[13]) else None,
                "indiv_pension_rate": float(row[14]) if pd.notna(row[14]) else None,
                "indiv_medical_rate": float(row[15]) if pd.notna(row[15]) else None,
                "indiv_injury_rate": float(row[16]) if pd.notna(row[16]) else None,
                "indiv_maternity_rate": float(row[17]) if pd.notna(row[17]) else None,
                "indiv_unemployment_rate": float(row[18]) if pd.notna(row[18]) else None,
                "indiv_fund_rate": float(row[19]) if pd.notna(row[19]) else None,
                "is_active": True
            }
            records.append(record_data)

        # Clear existing data
        db.query(CitySocialInsurance).delete()

        # Insert new data
        for record_data in records:
            db_record = CitySocialInsurance(**record_data)
            db.add(db_record)

        db.commit()
        return {"message": f"成功导入 {len(records)} 条数据", "count": len(records)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")


@router.put("/{record_id}", response_model=CitySocialInsuranceOut)
def update_city_social_insurance(
    record_id: int,
    record: CitySocialInsuranceUpdate,
    db: Session = Depends(get_db)
):
    """更新城市社保基准数据"""
    db_record = db.query(CitySocialInsurance).filter(CitySocialInsurance.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="数据不存在")

    update_data = record.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)

    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/{record_id}")
def delete_city_social_insurance(record_id: int, db: Session = Depends(get_db)):
    """删除城市社保基准数据"""
    db_record = db.query(CitySocialInsurance).filter(CitySocialInsurance.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="数据不存在")

    db.delete(db_record)
    db.commit()
    return {"ok": True}


@router.delete("/clear")
def clear_city_social_insurance(db: Session = Depends(get_db)):
    """清空所有城市社保基准数据"""
    try:
        db.query(CitySocialInsurance).delete()
        db.commit()
        return {"message": "所有城市社保基准数据已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
