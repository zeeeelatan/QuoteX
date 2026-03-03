"""
中国城市分级表路由
提供增删改查及 Excel 导入接口
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import pandas as pd

from app.schemas.china_city_tier import (
    ChinaCityTierCreate,
    ChinaCityTierUpdate,
    ChinaCityTierOut
)
from app.models.china_city_tier import ChinaCityTier
from app.database import get_db

router = APIRouter(prefix="/china-city-tier", tags=["中国城市分级表"])


def _safe_str(v) -> Optional[str]:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None


def _safe_int(v) -> Optional[int]:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


@router.get("/", response_model=List[ChinaCityTierOut])
def list_china_city_tier(
    search: Optional[str] = None,
    city_tier: Optional[str] = None,
    province: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取中国城市分级列表，支持搜索和筛选"""
    query = db.query(ChinaCityTier)

    if search:
        query = query.filter(
            (ChinaCityTier.city_name.contains(search)) |
            (ChinaCityTier.province.contains(search)) |
            (ChinaCityTier.tier_code.contains(search)) |
            (ChinaCityTier.city_tier.contains(search))
        )
    if city_tier:
        query = query.filter(ChinaCityTier.city_tier == city_tier)
    if province:
        query = query.filter(ChinaCityTier.province == province)

    return query.order_by(ChinaCityTier.seq_no, ChinaCityTier.id).all()


@router.get("/{record_id}", response_model=ChinaCityTierOut)
def get_china_city_tier(record_id: int, db: Session = Depends(get_db)):
    """获取单条记录"""
    record = db.query(ChinaCityTier).filter(ChinaCityTier.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="数据不存在")
    return record


@router.post("/", response_model=ChinaCityTierOut)
def create_china_city_tier(record: ChinaCityTierCreate, db: Session = Depends(get_db)):
    """创建中国城市分级记录"""
    db_record = ChinaCityTier(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def _row_val(row, name: str, idx: int):
    """按列名或列索引取值"""
    if name in row.index:
        v = row[name]
    elif idx < len(row):
        v = row.iloc[idx]
    else:
        return None
    if name in ("序号",):
        return _safe_int(v)
    return _safe_str(v)


@router.post("/import-excel")
def import_excel(file: UploadFile, db: Session = Depends(get_db)):
    """从 Excel 导入中国城市分级表（首行为表头：序号、城市等级、城市等级代码、城市名称、所属省份、行政级别、是否省会、GDP万亿城市、物流枢纽等级、备注）"""
    try:
        content = file.file.read()
        df = pd.read_excel(io.BytesIO(content), header=0)
        records = []
        for idx, row in df.iterrows():
            city_name = _row_val(row, "城市名称", 3)
            if not city_name:
                continue
            records.append({
                "seq_no": _row_val(row, "序号", 0),
                "city_tier": _row_val(row, "城市等级", 1),
                "tier_code": _row_val(row, "城市等级代码", 2),
                "city_name": city_name,
                "province": _row_val(row, "所属省份", 4),
                "admin_level": _row_val(row, "行政级别", 5),
                "is_provincial_capital": _row_val(row, "是否省会", 6),
                "is_gdp_trillion": _row_val(row, "GDP万亿城市", 7),
                "logistics_hub_level": _row_val(row, "物流枢纽等级", 8),
                "remarks": _row_val(row, "备注", 9),
            })
        db.query(ChinaCityTier).delete()
        for r in records:
            db.add(ChinaCityTier(**r))
        db.commit()
        return {"message": f"成功导入 {len(records)} 条数据", "count": len(records)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")


@router.put("/{record_id}", response_model=ChinaCityTierOut)
def update_china_city_tier(
    record_id: int,
    record: ChinaCityTierUpdate,
    db: Session = Depends(get_db)
):
    """更新中国城市分级记录"""
    db_record = db.query(ChinaCityTier).filter(ChinaCityTier.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="数据不存在")
    update_data = record.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/{record_id}")
def delete_china_city_tier(record_id: int, db: Session = Depends(get_db)):
    """删除中国城市分级记录"""
    db_record = db.query(ChinaCityTier).filter(ChinaCityTier.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="数据不存在")
    db.delete(db_record)
    db.commit()
    return {"ok": True}


@router.delete("/clear")
def clear_china_city_tier(db: Session = Depends(get_db)):
    """清空所有中国城市分级数据"""
    try:
        db.query(ChinaCityTier).delete()
        db.commit()
        return {"message": "所有数据已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
