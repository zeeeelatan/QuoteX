from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
from io import BytesIO
import os
from decimal import Decimal
from pydantic import BaseModel

from ..database import get_db
from ..schemas.pricing_parameter import PricingParameterCreate, PricingParameterOut
from ..models.pricing_parameter import PricingParameter

router = APIRouter(
    prefix="/pricing-parameter",
    tags=["pricing_parameter"]
)

# 兼容前端的数据结构
class PricingParameterLegacyCreate(BaseModel):
    parameter_category: str
    parameter_value: str
    applicable_products: Optional[str] = None
    coefficient: float

class PricingParameterImport(BaseModel):
    data: List[PricingParameterLegacyCreate]


@router.get("/", response_model=List[PricingParameterOut])
def list_pricing_parameters(db: Session = Depends(get_db)):
    """获取所有调价参数"""
    return db.query(PricingParameter).order_by(PricingParameter.id).all()


# 兼容前端的数据结构
class PricingParameterLegacyResponse(BaseModel):
    id: int
    parameter_category: str
    parameter_value: str
    applicable_products: Optional[str] = None
    coefficient: float

    class Config:
        from_attributes = True


@router.get("/legacy/", response_model=List[PricingParameterLegacyResponse])
def list_pricing_parameters_legacy(db: Session = Depends(get_db)):
    """获取所有调价参数 - 兼容前端"""
    params = db.query(PricingParameter).order_by(PricingParameter.id).all()
    return [
        {
            "id": p.id,
            "parameter_category": p.parameter_category,
            "parameter_value": p.parameter_value,
            "applicable_products": p.applicable_products,
            "coefficient": float(p.coefficient)
        }
        for p in params
    ]


@router.post("/", response_model=PricingParameterOut)
def create_pricing_parameter(param: PricingParameterCreate, db: Session = Depends(get_db)):
    """创建调价参数"""
    db_param = PricingParameter(**param.dict())
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    return db_param


@router.put("/{param_id}", response_model=PricingParameterOut)
def update_pricing_parameter(param_id: int, param: PricingParameterCreate, db: Session = Depends(get_db)):
    """更新调价参数"""
    db_param = db.query(PricingParameter).filter(PricingParameter.id == param_id).first()
    if not db_param:
        raise HTTPException(status_code=404, detail="调价参数不存在")
    for k, v in param.dict().items():
        setattr(db_param, k, v)
    db.commit()
    db.refresh(db_param)
    return db_param


@router.delete("/{param_id}")
def delete_pricing_parameter(param_id: int, db: Session = Depends(get_db)):
    """删除调价参数"""
    db_param = db.query(PricingParameter).filter(PricingParameter.id == param_id).first()
    if not db_param:
        raise HTTPException(status_code=404, detail="调价参数不存在")
    db.delete(db_param)
    db.commit()
    return {"ok": True}


@router.delete("/clear")
def clear_pricing_parameters(db: Session = Depends(get_db)):
    """清空所有调价参数"""
    try:
        db.query(PricingParameter).delete()
        db.commit()
        return {"message": "所有调价参数已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import-json")
def import_pricing_parameters_json(import_data: PricingParameterImport, db: Session = Depends(get_db)):
    """从JSON数据导入调价参数"""
    try:
        success_count = 0
        for item in import_data.data:
            param = PricingParameter(
                parameter_category=item.parameter_category,
                parameter_value=item.parameter_value,
                applicable_products=item.applicable_products,
                coefficient=item.coefficient
            )
            db.add(param)
            success_count += 1

        db.commit()
        return {"message": f"导入成功，共导入{success_count}条数据"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# 获取所有参数分类
@router.get("/categories/list")
def get_parameter_categories(db: Session = Depends(get_db)):
    """获取所有调价参数分类列表"""
    categories = db.query(PricingParameter.parameter_category).distinct().all()
    return {"categories": [c[0] for c in categories]}
