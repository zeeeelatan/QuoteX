from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, func as sa_func
from typing import List, Optional, Tuple
import pandas as pd
from io import BytesIO
import os
import json
from decimal import Decimal
from pydantic import BaseModel

from ..database import get_db, engine
from ..schemas.service_level import ServiceLevelCreate, ServiceLevelResponse
from ..templates.service_level_template import create_service_level_template

# 直接导入ServiceLevel模型
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from ..database import Base


class ServiceLevel(Base):
    __tablename__ = "service_level"

    id = Column(Integer, primary_key=True, index=True)
    level_code = Column(String, nullable=False)        # 服务等级
    response_time = Column(String, nullable=False)     # SLA 组合
    definition = Column(Text, nullable=True)           # 释义
    aliases = Column(JSONB, nullable=True, server_default="[]")  # 别名 JSON 数组
    coefficient = Column(Numeric(10, 2), nullable=False)  # 服务级别系数值
    applicable_products = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# 自动 ALTER：第一次启动时若旧表缺 definition / aliases，自动补齐
def _ensure_columns():
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE service_level ADD COLUMN IF NOT EXISTS definition TEXT"))
            conn.execute(text("ALTER TABLE service_level ADD COLUMN IF NOT EXISTS aliases JSONB DEFAULT '[]'::jsonb"))
    except Exception:
        # 表可能尚未创建（首次启动），create_all 之后再做也无所谓
        pass


_ensure_columns()


router = APIRouter(
    prefix="/service-level",
    tags=["service_level"]
)


# 兼容旧版前端的Schema
class ServiceLevelLegacyCreate(BaseModel):
    service_level: str
    response_time: str
    coefficient: float
    applicable_products: Optional[str] = None


class ServiceLevelImport(BaseModel):
    data: List[ServiceLevelLegacyCreate]


@router.get("/", response_model=List[ServiceLevelResponse])
def list_service_levels(db: Session = Depends(get_db)):
    """获取所有服务级别"""
    return db.query(ServiceLevel).order_by(ServiceLevel.id.asc()).all()


# 兼容旧版前端的响应格式
class ServiceLevelLegacyResponse(BaseModel):
    id: int
    service_level: str
    response_time: str
    coefficient: float
    applicable_products: Optional[str] = None
    definition: Optional[str] = None
    aliases: List[str] = []

    class Config:
        from_attributes = True


@router.get("/legacy/", response_model=List[ServiceLevelLegacyResponse])
def list_service_levels_legacy(db: Session = Depends(get_db)):
    """获取所有服务级别 - 兼容旧版前端（使用service_level字段名）"""
    levels = db.query(ServiceLevel).order_by(ServiceLevel.id.asc()).all()
    return [
        {
            "id": lvl.id,
            "service_level": lvl.level_code,
            "response_time": lvl.response_time,
            "coefficient": float(lvl.coefficient),
            "applicable_products": lvl.applicable_products,
            "definition": lvl.definition,
            "aliases": lvl.aliases or [],
        }
        for lvl in levels
    ]


# ============ SLA 别名解析 ============

def _normalize_sla(s: str) -> str:
    """把 SLA 字符串归一化用于比对：去空白、统一大小写、把全/半角分隔统一成 *"""
    if not s:
        return ""
    s = str(s).strip().upper()
    for ch in ("×", "X", "·"):
        s = s.replace(ch, "*")
    s = s.replace(" ", "").replace("－", "-")
    return s


def resolve_sla(db: Session, raw: str) -> Optional[ServiceLevel]:
    """把任意写法的 SLA 字符串解析到 service_level 行；不命中返回 None。

    两遍扫描：先在所有行的 response_time（主写法）里找；找不到再到
    aliases 里找。避免别名跨行污染时把请求误导到错误的行。
    """
    if not raw:
        return None
    target = _normalize_sla(raw)
    # 按 id 升序确保命中确定性：当多个行的别名同时包含某个写法时，
    # 较早录入（id 小）的行优先（一般是更"主"的等级行）
    rows = db.query(ServiceLevel).order_by(ServiceLevel.id.asc()).all()
    # 第一遍：主写法
    for lvl in rows:
        if _normalize_sla(lvl.response_time) == target:
            return lvl
    # 第二遍：别名
    for lvl in rows:
        for alias in (lvl.aliases or []):
            if _normalize_sla(alias) == target:
                return lvl
    return None


class ResolveResponse(BaseModel):
    matched: bool
    service_level: Optional[ServiceLevelLegacyResponse] = None
    candidates: List[str] = []  # 该等级在系统内所有可用的 SLA 写法（含 response_time + aliases）


@router.get("/resolve", response_model=ResolveResponse)
def resolve_sla_endpoint(sla: str = Query(..., description="任意写法的 SLA 字符串"),
                          db: Session = Depends(get_db)):
    lvl = resolve_sla(db, sla)
    if not lvl:
        return ResolveResponse(matched=False)
    candidates = [lvl.response_time] + [a for a in (lvl.aliases or []) if a and a != lvl.response_time]
    return ResolveResponse(
        matched=True,
        service_level={
            "id": lvl.id,
            "service_level": lvl.level_code,
            "response_time": lvl.response_time,
            "coefficient": float(lvl.coefficient),
            "applicable_products": lvl.applicable_products,
            "definition": lvl.definition,
            "aliases": lvl.aliases or [],
        },
        candidates=candidates,
    )


# ============ CRUD ============

@router.post("/", response_model=ServiceLevelResponse)
def create_service_level(payload: ServiceLevelCreate, db: Session = Depends(get_db)):
    obj = ServiceLevel(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{service_level_id}", response_model=ServiceLevelResponse)
def update_service_level(service_level_id: int, payload: ServiceLevelCreate,
                          db: Session = Depends(get_db)):
    obj = db.query(ServiceLevel).filter(ServiceLevel.id == service_level_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="服务级别不存在")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{service_level_id}")
def delete_service_level(service_level_id: int, db: Session = Depends(get_db)):
    obj = db.query(ServiceLevel).filter(ServiceLevel.id == service_level_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="服务级别不存在")
    db.delete(obj)
    db.commit()
    return {"ok": True}


@router.get("/template")
async def download_template():
    """下载服务级别导入模板"""
    template_path = "service_level_template.xlsx"
    if not os.path.exists(template_path):
        create_service_level_template()
    return FileResponse(
        template_path,
        filename="服务级别导入模板.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.post("/import")
def import_service_levels(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """从Excel文件导入服务级别（兼容旧字段；新字段释义/别名留空）"""
    try:
        contents = file.file.read()
        df = pd.read_excel(BytesIO(contents))

        success_count = 0
        error_rows = []

        for idx, row in df.iterrows():
            try:
                level_code = str(row.get('服务等级') or row.get('服务级别') or '').strip()
                response_time = str(row.get('SLA 组合') or row.get('SLA组合') or row.get('响应时效') or '').strip()
                coefficient = row.get('服务级别系数值', 0)
                definition = row.get('释义')
                aliases_raw = row.get('别名')
                aliases: List[str] = []
                if isinstance(aliases_raw, str) and aliases_raw.strip():
                    normalized = aliases_raw.replace('；', ';').replace('，', ',').replace(';', ',')
                    aliases = [a.strip() for a in normalized.split(',') if a.strip()]

                if not level_code or not response_time:
                    raise ValueError('服务等级和 SLA 组合不能为空')
                if not isinstance(coefficient, (int, float)) or coefficient <= 0:
                    raise ValueError('服务级别系数值必须是大于0的数字')

                obj = db.query(ServiceLevel).filter_by(response_time=response_time).first()
                if obj:
                    obj.level_code = level_code
                    obj.coefficient = coefficient
                    if definition is not None and str(definition).strip():
                        obj.definition = str(definition).strip()
                    if aliases:
                        obj.aliases = aliases
                else:
                    db.add(ServiceLevel(
                        level_code=level_code,
                        response_time=response_time,
                        coefficient=coefficient,
                        definition=str(definition).strip() if definition is not None else None,
                        aliases=aliases or [],
                    ))
                success_count += 1
            except Exception as e:
                error_rows.append(f"第{idx + 2}行: {str(e)}")

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
            obj = db.query(ServiceLevel).filter_by(level_code=item.service_level).first()
            if obj:
                obj.response_time = item.response_time
                obj.coefficient = item.coefficient
                obj.applicable_products = item.applicable_products
            else:
                obj = ServiceLevel(
                    level_code=item.service_level,
                    response_time=item.response_time,
                    coefficient=item.coefficient,
                    applicable_products=item.applicable_products,
                )
                db.add(obj)
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
