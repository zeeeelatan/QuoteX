"""
城市社保基准数据路由
提供城市社保基准数据的增删改查接口
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import pandas as pd
import re
from io import BytesIO

from app.schemas.city_social_insurance import (
    CitySocialInsuranceCreate,
    CitySocialInsuranceUpdate,
    CitySocialInsuranceOut
)
from app.models.city_social_insurance import CitySocialInsurance
from app.database import get_db

router = APIRouter(prefix="/city-social-insurance", tags=["城市社保基准数据管理"])


def _city_variants(city_name: str) -> list[str]:
    city = (city_name or "").strip()
    if not city:
        return []
    variants = {city}
    if city.endswith("市"):
        variants.add(city[:-1])
    else:
        variants.add(f"{city}市")
    return list(variants)


def _nullable_number(value, default=None):
    if pd.isna(value) or value == "":
        return default
    if isinstance(value, str):
        text = value.strip()
        if not text or text in {"-", "—", "–"}:
            return default
        text = text.replace(",", "")
        if text.endswith("%"):
            return float(text[:-1]) / 100
        return float(text)
    return float(value)


def _nullable_int(value, default=None):
    number = _nullable_number(value, default)
    if number is None:
        return default
    return int(round(number))


def _parse_fund_rate_range(value) -> tuple[Optional[float], Optional[float], Optional[float]]:
    if pd.isna(value):
        return None, None, None
    if isinstance(value, (int, float)):
        rate = float(value)
        return rate, rate, rate

    text = str(value).strip()
    if not text or text in {"-", "—", "–"}:
        return None, None, None

    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    if not numbers:
        return None, None, None

    rates = [float(item) / 100 for item in numbers]
    if len(rates) == 1:
        return rates[0], rates[0], rates[0]
    return rates[0], rates[-1], rates[0]


def _city_alias(city: str) -> Optional[str]:
    city = (city or "").strip()
    if city.endswith("市") and len(city) > 1:
        return city[:-1]
    return None


def _parse_2025_workbook(file_bytes: bytes) -> list[dict]:
    df = pd.read_excel(BytesIO(file_bytes), sheet_name="各城市社保比例", header=None)
    records = []

    for idx, row in df.iterrows():
        if idx < 2:
            continue

        province = row[0] if pd.notna(row[0]) else None
        city = row[1] if pd.notna(row[1]) else None
        if not province or not city:
            continue

        province = str(province).strip()
        city = str(city).strip()
        if province.startswith("*") or city.startswith("*"):
            continue

        fund_rate_min, fund_rate_max, fund_default_rate = _parse_fund_rate_range(row[15])
        fund_lower_limit = _nullable_int(row[16])
        fund_upper_limit = _nullable_int(row[17])
        corp_fund_rate = fund_default_rate

        record_data = {
            "province": province,
            "city": city,
            "city_alias": _city_alias(city),
            "upper_limit": _nullable_int(row[14], 0),
            "lower_limit": _nullable_int(row[13], 0),
            "calc_base": _nullable_int(row[13], 0),
            "injury_base": None,
            "corp_pension_rate": _nullable_number(row[2]),
            "corp_medical_rate": _nullable_number(row[4]),
            "corp_injury_rate": _nullable_number(row[8]),
            "corp_maternity_rate": _nullable_number(row[9], 0),
            "corp_unemployment_rate": _nullable_number(row[6]),
            "corp_disability_rate": _nullable_number(row[11]),
            "corp_fund_rate": corp_fund_rate,
            "indiv_pension_rate": _nullable_number(row[3]),
            "indiv_medical_rate": _nullable_number(row[5]),
            "indiv_injury_rate": 0,
            "indiv_maternity_rate": 0,
            "indiv_unemployment_rate": _nullable_number(row[7]),
            "indiv_fund_rate": corp_fund_rate,
            "fund_lower_limit": fund_lower_limit,
            "fund_upper_limit": fund_upper_limit,
            "fund_rate_min": fund_rate_min,
            "fund_rate_max": fund_rate_max,
            "fund_default_rate": fund_default_rate,
            "is_active": True,
            "remarks": str(row[19]).strip() if pd.notna(row[19]) else None,
        }
        records.append(record_data)

    return records


def _parse_legacy_workbook(file_bytes: bytes) -> list[dict]:
    df = pd.read_excel(BytesIO(file_bytes), header=None)
    records = []

    for idx, row in df.iterrows():
        if idx < 3:
            continue

        province = row[0] if pd.notna(row[0]) else None
        city = row[1] if pd.notna(row[1]) else None
        if not province or not city:
            continue

        corp_fund_rate = _nullable_number(row[13])
        indiv_fund_rate = _nullable_number(row[19])
        record_data = {
            "province": str(province).strip(),
            "city": str(city).strip(),
            "city_alias": _city_alias(str(city)),
            "upper_limit": _nullable_int(row[2], 0),
            "lower_limit": _nullable_int(row[3], 0),
            "calc_base": _nullable_int(row[4], 0),
            "injury_base": _nullable_int(row[5]),
            "corp_pension_rate": _nullable_number(row[6]),
            "corp_medical_rate": _nullable_number(row[7]),
            "corp_injury_rate": _nullable_number(row[8]),
            "corp_maternity_rate": _nullable_number(row[9]),
            "corp_unemployment_rate": _nullable_number(row[10]),
            "corp_disability_rate": _nullable_number(row[11]),
            "corp_fund_rate": corp_fund_rate,
            "indiv_pension_rate": _nullable_number(row[14]),
            "indiv_medical_rate": _nullable_number(row[15]),
            "indiv_injury_rate": _nullable_number(row[16]),
            "indiv_maternity_rate": _nullable_number(row[17]),
            "indiv_unemployment_rate": _nullable_number(row[18]),
            "indiv_fund_rate": indiv_fund_rate,
            "fund_lower_limit": _nullable_int(row[3], 0),
            "fund_upper_limit": _nullable_int(row[2], 0),
            "fund_rate_min": corp_fund_rate,
            "fund_rate_max": corp_fund_rate,
            "fund_default_rate": corp_fund_rate,
            "is_active": True
        }
        records.append(record_data)

    return records


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
        variants = _city_variants(city)
        query = query.filter(
            or_(
                CitySocialInsurance.city.in_(variants),
                CitySocialInsurance.city_alias.in_(variants),
            )
        )

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


@router.get("/city/{city_name}", response_model=CitySocialInsuranceOut)
def get_by_city_name(city_name: str, db: Session = Depends(get_db)):
    """根据城市名称获取社保基准数据"""
    variants = _city_variants(city_name)
    record = db.query(CitySocialInsurance).filter(
        or_(
            CitySocialInsurance.city.in_(variants),
            CitySocialInsurance.city_alias.in_(variants),
        )
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"城市 {city_name} 的社保数据不存在")
    return record


@router.get("/{record_id}", response_model=CitySocialInsuranceOut)
def get_city_social_insurance(record_id: int, db: Session = Depends(get_db)):
    """获取单条城市社保基准数据"""
    record = db.query(CitySocialInsurance).filter(CitySocialInsurance.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="数据不存在")
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
        file_bytes = file.file.read()
        try:
            records = _parse_2025_workbook(file_bytes)
        except ValueError:
            records = _parse_legacy_workbook(file_bytes)

        if not records:
            raise HTTPException(status_code=400, detail="未识别到可导入的城市社保数据")

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
