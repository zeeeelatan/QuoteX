"""
机房搬迁车型数据路由
提供机房搬迁车型数据的增删改查及 Excel 导入
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io

from app.database import get_db
from app.models.relocation_vehicle import RelocationVehicle
from app.schemas.relocation_vehicle import (
    RelocationVehicleCreate,
    RelocationVehicleUpdate,
    RelocationVehicleOut,
)

router = APIRouter(prefix="/relocation-vehicle", tags=["机房搬迁车型数据"])

# Excel 列名 -> 模型字段
EXCEL_COLUMN_MAP = {
    "序号": "seq_no",
    "车型分类": "vehicle_category",
    "车型名称": "vehicle_name",
    "车厢长度(m)": "length_m",
    "车厢宽度(m)": "width_m",
    "车厢高度(m)": "height_m",
    "容积(m³)": "volume_m3",
    "载重量(吨)": "load_ton",
    "可装1U服务器(台)": "server_1u",
    "可装2U服务器(台)": "server_2u",
    "可装机柜(个)": "rack_count",
    "适用场景": "scenario",
    "运输距离建议": "distance_advice",
    "是否需特殊驾照": "license_required",
    "市区限行情况": "city_restrict",
    "地库限高通过": "basement_limit",
    "参考起步价(元)": "start_price",
    "参考公里价(元/km)": "km_price",
    "备注": "remark",
}


def _to_float(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


def _to_str(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    return s if s else None


def _to_int(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    try:
        return int(float(x))
    except (ValueError, TypeError):
        return None


@router.get("/", response_model=List[RelocationVehicleOut])
def list_relocation_vehicles(
    vehicle_category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取机房搬迁车型列表，支持按车型分类筛选"""
    query = db.query(RelocationVehicle).order_by(RelocationVehicle.seq_no, RelocationVehicle.id)
    if vehicle_category:
        query = query.filter(RelocationVehicle.vehicle_category == vehicle_category)
    return query.all()


@router.get("/{vehicle_id}", response_model=RelocationVehicleOut)
def get_relocation_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """获取单条机房搬迁车型数据"""
    row = db.query(RelocationVehicle).filter(RelocationVehicle.id == vehicle_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="机房搬迁车型数据不存在")
    return row


@router.post("/", response_model=RelocationVehicleOut)
def create_relocation_vehicle(data: RelocationVehicleCreate, db: Session = Depends(get_db)):
    """创建机房搬迁车型数据"""
    db_row = RelocationVehicle(**data.model_dump(exclude_unset=True))
    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row


@router.put("/{vehicle_id}", response_model=RelocationVehicleOut)
def update_relocation_vehicle(
    vehicle_id: int,
    data: RelocationVehicleUpdate,
    db: Session = Depends(get_db),
):
    """更新机房搬迁车型数据"""
    row = db.query(RelocationVehicle).filter(RelocationVehicle.id == vehicle_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="机房搬迁车型数据不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/clear")
def clear_all(db: Session = Depends(get_db)):
    """清空机房搬迁车型数据"""
    db.query(RelocationVehicle).delete()
    db.commit()
    return {"ok": True, "message": "已清空"}


@router.delete("/{vehicle_id}")
def delete_relocation_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """删除机房搬迁车型数据"""
    row = db.query(RelocationVehicle).filter(RelocationVehicle.id == vehicle_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="机房搬迁车型数据不存在")
    db.delete(row)
    db.commit()
    return {"ok": True, "message": "已删除"}


@router.post("/import")
async def import_from_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """从 Excel 导入机房搬迁车型数据（机房搬迁车型数据大全.xlsx）"""
    if not file.filename or not (file.filename.lower().endswith(".xlsx") or file.filename.lower().endswith(".xls")):
        raise HTTPException(status_code=400, detail="请上传 .xlsx 或 .xls 文件")
    try:
        raw = await file.read()
        df = pd.read_excel(io.BytesIO(raw), sheet_name=0, header=0)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析 Excel 失败: {e}")
    df = df.rename(columns=EXCEL_COLUMN_MAP)
    model_cols = {c.key for c in RelocationVehicle.__table__.columns if c.key != "id"}
    keep = [c for c in df.columns if c in model_cols]
    df = df[[c for c in keep]].copy()
    created = 0
    errors = []
    for idx, row in df.iterrows():
        try:
            rec = {}
            for col in model_cols:
                if col not in df.columns:
                    continue
                val = row.get(col)
                if col in ("length_m", "width_m", "height_m", "volume_m3", "load_ton"):
                    rec[col] = _to_float(val)
                elif col == "seq_no":
                    rec[col] = _to_int(val)
                else:
                    rec[col] = _to_str(val)
            db.add(RelocationVehicle(**rec))
            created += 1
        except Exception as e:
            errors.append(f"第 {idx + 2} 行: {e}")
    db.commit()
    msg = f"成功导入 {created} 条"
    if errors:
        msg += f"；{len(errors)} 行失败"
    return {"ok": True, "message": msg, "count": created, "errors": errors[:10]}
