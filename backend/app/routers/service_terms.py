from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

# Service Term 数据库模型
class ServiceTerm(Base):
    __tablename__ = "service_term"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # 条款名称
    products = Column(String(500), nullable=True)  # 适用产品（JSON字符串数组）
    content = Column(Text, nullable=True)  # 具体内容（HTML格式）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic Schemas
class ServiceTermBase(BaseModel):
    name: str
    products: List[str] = []
    content: str = ""

class ServiceTermCreate(ServiceTermBase):
    pass

class ServiceTermUpdate(ServiceTermBase):
    pass

class ServiceTermResponse(BaseModel):
    id: int
    name: str
    products: List[str]
    content: str
    last_modified: str
    created_at: str

    class Config:
        from_attributes = True

router = APIRouter(
    prefix="/service-terms",
    tags=["service_terms"]
)

@router.get("/", response_model=List[ServiceTermResponse])
def list_service_terms(db: Session = Depends(get_db)):
    """获取所有服务条款"""
    terms = db.query(ServiceTerm).order_by(ServiceTerm.updated_at.desc()).all()
    result = []
    for term in terms:
        # 解析 products JSON 字符串
        products = []
        if term.products:
            import json
            try:
                products = json.loads(term.products)
            except:
                products = term.products.split(',') if term.products else []

        result.append({
            "id": term.id,
            "name": term.name,
            "products": products,
            "content": term.content or "",
            "last_modified": term.updated_at.strftime("%Y-%m-%d") if term.updated_at else "",
            "created_at": term.created_at.strftime("%Y-%m-%d") if term.created_at else ""
        })
    return result


@router.get("/{term_id}", response_model=ServiceTermResponse)
def get_service_term(term_id: int, db: Session = Depends(get_db)):
    """获取单个服务条款"""
    term = db.query(ServiceTerm).filter(ServiceTerm.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="服务条款不存在")

    # 解析 products JSON 字符串
    products = []
    if term.products:
        import json
        try:
            products = json.loads(term.products)
        except:
            products = term.products.split(',') if term.products else []

    return {
        "id": term.id,
        "name": term.name,
        "products": products,
        "content": term.content or "",
        "last_modified": term.updated_at.strftime("%Y-%m-%d") if term.updated_at else "",
        "created_at": term.created_at.strftime("%Y-%m-%d") if term.created_at else ""
    }


@router.post("/", response_model=ServiceTermResponse)
def create_service_term(term: ServiceTermCreate, db: Session = Depends(get_db)):
    """创建服务条款"""
    import json
    db_term = ServiceTerm(
        name=term.name,
        products=json.dumps(term.products) if term.products else None,
        content=term.content
    )
    db.add(db_term)
    db.commit()
    db.refresh(db_term)

    return {
        "id": db_term.id,
        "name": db_term.name,
        "products": term.products,
        "content": db_term.content or "",
        "last_modified": db_term.updated_at.strftime("%Y-%m-%d") if db_term.updated_at else "",
        "created_at": db_term.created_at.strftime("%Y-%m-%d") if db_term.created_at else ""
    }


@router.put("/{term_id}", response_model=ServiceTermResponse)
def update_service_term(term_id: int, term: ServiceTermUpdate, db: Session = Depends(get_db)):
    """更新服务条款"""
    db_term = db.query(ServiceTerm).filter(ServiceTerm.id == term_id).first()
    if not db_term:
        raise HTTPException(status_code=404, detail="服务条款不存在")

    import json
    db_term.name = term.name
    db_term.products = json.dumps(term.products) if term.products else None
    db_term.content = term.content

    db.commit()
    db.refresh(db_term)

    return {
        "id": db_term.id,
        "name": db_term.name,
        "products": term.products,
        "content": db_term.content or "",
        "last_modified": db_term.updated_at.strftime("%Y-%m-%d") if db_term.updated_at else "",
        "created_at": db_term.created_at.strftime("%Y-%m-%d") if db_term.created_at else ""
    }


@router.delete("/{term_id}")
def delete_service_term(term_id: int, db: Session = Depends(get_db)):
    """删除服务条款"""
    db_term = db.query(ServiceTerm).filter(ServiceTerm.id == term_id).first()
    if not db_term:
        raise HTTPException(status_code=404, detail="服务条款不存在")
    db.delete(db_term)
    db.commit()
    return {"ok": True}
