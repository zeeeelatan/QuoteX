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
from ..schemas.service_level import ServiceLevelCreate, ServiceLevelResponse
from ..templates.service_level_template import create_service_level_template

# 直接导入ServiceLevel模型
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from ..database import Base

class ServiceLevel(Base):
    __tablename__ = "service_level"

    id = Column(Integer, primary_key=True, index=True)
    level_code = Column(String, nullable=False)  # 服务级别
    response_time = Column(String, nullable=False)  # 响应时效
    coefficient = Column(Numeric(10, 2), nullable=False)  # 服务级别系数值
    applicable_products = Column(String, nullable=True)  # 适用产品，JSON字符串存储产品名称数组
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

router = APIRouter(
    prefix="/service-level",
    tags=["service_level"]
)

# 兼容旧版前端的Schema
class ServiceLevelLegacyCreate(BaseModel):
    service_level: str
    response_time: str
    coefficient: float
    applicable_products: Optional[str] = None  # 适用产品，JSON字符串

class ServiceLevelImport(BaseModel):
    data: List[ServiceLevelLegacyCreate]

@router.get("/", response_model=List[ServiceLevelResponse])
def list_service_levels(db: Session = Depends(get_db)):
    """获取所有服务级别"""
    return db.query(ServiceLevel).all()


# 兼容旧版前端的响应格式
class ServiceLevelLegacyResponse(BaseModel):
    id: int
    service_level: str
    response_time: str
    coefficient: float
    applicable_products: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/legacy/", response_model=List[ServiceLevelLegacyResponse])
def list_service_levels_legacy(db: Session = Depends(get_db)):
    """获取所有服务级别 - 兼容旧版前端（使用service_level字段名）"""
    levels = db.query(ServiceLevel).all()
    return [
        {
            "id": lvl.id,
            "service_level": lvl.level_code,
            "response_time": lvl.response_time,
            "coefficient": float(lvl.coefficient),
            "applicable_products": lvl.applicable_products
        }
        for lvl in levels
    ]

@router.post("/", response_model=ServiceLevelResponse)
def create_service_level(service_level: ServiceLevelCreate, db: Session = Depends(get_db)):
    db_service_level = ServiceLevel(**service_level.dict())
    db.add(db_service_level)
    db.commit()
    db.refresh(db_service_level)
    return db_service_level

@router.put("/{service_level_id}", response_model=ServiceLevelResponse)
def update_service_level(service_level_id: int, service_level: ServiceLevelCreate, db: Session = Depends(get_db)):
    db_service_level = db.query(ServiceLevel).filter(ServiceLevel.id == service_level_id).first()
    if not db_service_level:
        raise HTTPException(status_code=404, detail="服务级别不存在")
    for k, v in service_level.dict().items():
        setattr(db_service_level, k, v)
    db.commit()
    db.refresh(db_service_level)
    return db_service_level

@router.delete("/{service_level_id}")
def delete_service_level(service_level_id: int, db: Session = Depends(get_db)):
    db_service_level = db.query(ServiceLevel).filter(ServiceLevel.id == service_level_id).first()
    if not db_service_level:
        raise HTTPException(status_code=404, detail="服务级别不存在")
    db.delete(db_service_level)
    db.commit()
    return {"ok": True}

@router.get("/template")
async def download_template():
    """下载服务级别导入模板"""
    template_path = "service_level_template.xlsx"
    
    # 如果模板文件不存在，创建它
    if not os.path.exists(template_path):
        create_service_level_template()
    
    return FileResponse(
        template_path,
        filename="服务级别导入模板.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.post("/import")
def import_service_levels(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """从Excel文件导入服务级别"""
    try:
        contents = file.file.read()
        df = pd.read_excel(BytesIO(contents))

        success_count = 0
        error_rows = []

        for idx, row in df.iterrows():
            try:
                level_code = str(row.get('服务级别', '')).strip()
                response_time = str(row.get('响应时效', '')).strip()
                coefficient = row.get('服务级别系数值', 0)

                if not level_code or not response_time:
                    raise ValueError('服务级别和响应时效不能为空')

                if not isinstance(coefficient, (int, float)) or coefficient <= 0:
                    raise ValueError('服务级别系数值必须是大于0的数字')

                # 查找是否已存在
                service_level = db.query(ServiceLevel).filter_by(level_code=level_code).first()

                if service_level:
                    service_level.response_time = response_time
                    service_level.coefficient = coefficient
                else:
                    service_level = ServiceLevel(
                        level_code=level_code,
                        response_time=response_time,
                        coefficient=coefficient
                    )
                    db.add(service_level)

                success_count += 1
            except Exception as e:
                error_rows.append(f"第{idx+2}行: {str(e)}")

        db.commit()

        if error_rows:
            return {"message": f"部分数据导入成功，共导入{success_count}条数据", "errors": error_rows}
        return {"message": f"导入成功，共导入{success_count}条数据"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        file.file.close()


@router.post("/import-json")
def import_service_levels_json(import_data: ServiceLevelImport, db: Session = Depends(get_db)):
    """从JSON数据导入服务级别 - 兼容旧版前端"""
    try:
        success_count = 0
        for item in import_data.data:
            # 查找是否已存在
            service_level = db.query(ServiceLevel).filter_by(level_code=item.service_level).first()

            if service_level:
                service_level.response_time = item.response_time
                service_level.coefficient = item.coefficient
                service_level.applicable_products = item.applicable_products
            else:
                service_level = ServiceLevel(
                    level_code=item.service_level,
                    response_time=item.response_time,
                    coefficient=item.coefficient,
                    applicable_products=item.applicable_products
                )
                db.add(service_level)
            success_count += 1

        db.commit()
        return {"message": f"导入成功，共导入{success_count}条数据"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/clear")
def clear_service_levels(db: Session = Depends(get_db)):
    """清空所有服务级别"""
    try:
        db.query(ServiceLevel).delete()
        db.commit()
        return {"message": "所有服务级别已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) 