from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.maintenance_rate import MaintenanceRateCreate, MaintenanceRateUpdate, MaintenanceRateOut
from app.models.maintenance_rate import MaintenanceRate
from app.database import get_db

router = APIRouter(prefix="/maintenance_rates", tags=["维保费率"])

@router.get("/", response_model=List[MaintenanceRateOut])
def list_rates(db: Session = Depends(get_db)):
    return db.query(MaintenanceRate).all()

@router.post("/", response_model=MaintenanceRateOut)
def create_rate(rate: MaintenanceRateCreate, db: Session = Depends(get_db)):
    db_rate = MaintenanceRate(**rate.dict())
    db_rate.rate = float(rate.rate) / 100  # 百分比转小数
    db.add(db_rate)
    db.commit()
    db.refresh(db_rate)
    return db_rate

@router.put("/{rate_id}", response_model=MaintenanceRateOut)
def update_rate(rate_id: int, rate: MaintenanceRateUpdate, db: Session = Depends(get_db)):
    db_rate = db.query(MaintenanceRate).filter(MaintenanceRate.id == rate_id).first()
    if not db_rate:
        raise HTTPException(status_code=404, detail="费率不存在")
    for k, v in rate.dict().items():
        if k == 'rate':
            setattr(db_rate, k, float(v) / 100)
        else:
            setattr(db_rate, k, v)
    db.commit()
    db.refresh(db_rate)
    return db_rate

@router.delete("/clear")
def clear_all_rates(db: Session = Depends(get_db)):
    db.query(MaintenanceRate).delete()
    db.commit()
    return {"ok": True, "message": "所有费率已清空"}

@router.delete("/{rate_id}")
def delete_rate(rate_id: int, db: Session = Depends(get_db)):
    db_rate = db.query(MaintenanceRate).filter(MaintenanceRate.id == rate_id).first()
    if not db_rate:
        raise HTTPException(status_code=404, detail="费率不存在")
    db.delete(db_rate)
    db.commit()
    return {"ok": True}

@router.post("/import")
def import_rates(request: Request, db: Session = Depends(get_db)):
    import asyncio
    data = asyncio.run(request.json()) if hasattr(request, 'json') else request.json()
    items = data.get('data', [])
    if not items:
        raise HTTPException(status_code=400, detail="上传数据为空")
    success_count = 0
    error_rows = []
    def parse_rate(val):
        if val is None or str(val).strip() == '':
            raise ValueError('维保费率(%)不能为空')
        val = str(val).strip()
        try:
            rate = float(val)
            if rate <= 0:
                raise ValueError('维保费率(%)不能为0或负数')
            return rate / 100
        except Exception:
            raise ValueError(f'维保费率(%)格式错误，错误值：{val}')
    for idx, row in enumerate(items, 1):
        try:
            primary = row.get('一级分类') or row.get('primary_category')
            secondary = row.get('二级分类') or row.get('secondary_category')
            tertiary = row.get('三级分类') or row.get('tertiary_category')
            rate_raw = row.get('维保费率(%)') or row.get('rate')
            remark = row.get('备注') or row.get('remark', '')
            if not (primary and secondary and tertiary):
                raise ValueError('分类字段不能为空')
            rate = parse_rate(rate_raw)
            obj = db.query(MaintenanceRate).filter_by(
                primary_category=primary,
                secondary_category=secondary,
                tertiary_category=tertiary
            ).first()
            if obj:
                obj.rate = rate
                obj.remark = remark
            else:
                obj = MaintenanceRate(
                    primary_category=primary,
                    secondary_category=secondary,
                    tertiary_category=tertiary,
                    rate=rate,
                    remark=remark
                )
                db.add(obj)
            success_count += 1
        except Exception as e:
            error_rows.append(f"第{idx}行: {e}")
    db.commit()
    if error_rows:
        raise HTTPException(status_code=400, detail="部分数据导入失败: " + "; ".join(error_rows))
    return {"message": f"导入成功，共导入{success_count}条数据"} 