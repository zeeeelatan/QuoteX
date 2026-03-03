"""
叠加单价数据路由
提供叠加单价数据的增删改查接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.schemas.superimposed_price import (
    SuperimposedPriceCreate,
    SuperimposedPriceUpdate,
    SuperimposedPriceOut
)
from app.models.superimposed_price import SuperimposedPrice
from app.database import get_db

router = APIRouter(prefix="/superimposed-price", tags=["叠加单价数据管理"])


@router.get("/", response_model=List[SuperimposedPriceOut])
def list_superimposed_prices(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取叠加单价列表，支持搜索"""
    query = db.query(SuperimposedPrice)

    if search:
        query = query.filter(
            (SuperimposedPrice.price_description.contains(search)) |
            (SuperimposedPrice.charging_standard.contains(search))
        )

    return query.order_by(SuperimposedPrice.id).all()


@router.get("/{price_id}", response_model=SuperimposedPriceOut)
def get_superimposed_price(price_id: int, db: Session = Depends(get_db)):
    """获取单条叠加单价数据"""
    price = db.query(SuperimposedPrice).filter(SuperimposedPrice.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="叠加单价数据不存在")
    return price


@router.post("/", response_model=SuperimposedPriceOut)
def create_superimposed_price(price: SuperimposedPriceCreate, db: Session = Depends(get_db)):
    """创建叠加单价数据"""
    # 将适用产品列表转换为JSON字符串
    applicable_products_str = None
    if price.applicable_products:
        applicable_products_str = json.dumps(price.applicable_products, ensure_ascii=False)

    db_price = SuperimposedPrice(
        price_description=price.price_description,
        charging_standard=price.charging_standard,
        applicable_products=applicable_products_str,
        remarks=price.remarks
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price


@router.post("/batch-create")
def batch_create_superimposed_prices(data: dict, db: Session = Depends(get_db)):
    """批量创建叠加单价数据"""
    try:
        records = data.get("records", [])
        created = []
        for record in records:
            # 将适用产品列表转换为JSON字符串
            applicable_products_str = None
            if record.get("applicable_products"):
                applicable_products_str = json.dumps(record["applicable_products"], ensure_ascii=False)

            db_price = SuperimposedPrice(
                price_description=record["price_description"],
                charging_standard=record["charging_standard"],
                applicable_products=applicable_products_str,
                remarks=record.get("remarks")
            )
            db.add(db_price)
            created.append(db_price)
        db.commit()
        for item in created:
            db.refresh(item)
        return {"message": f"成功创建 {len(created)} 条数据", "count": len(created)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{price_id}", response_model=SuperimposedPriceOut)
def update_superimposed_price(
    price_id: int,
    price: SuperimposedPriceUpdate,
    db: Session = Depends(get_db)
):
    """更新叠加单价数据"""
    db_price = db.query(SuperimposedPrice).filter(SuperimposedPrice.id == price_id).first()
    if not db_price:
        raise HTTPException(status_code=404, detail="叠加单价数据不存在")

    if price.price_description is not None:
        db_price.price_description = price.price_description
    if price.charging_standard is not None:
        db_price.charging_standard = price.charging_standard
    if price.applicable_products is not None:
        applicable_products_str = json.dumps(price.applicable_products, ensure_ascii=False) if price.applicable_products else None
        db_price.applicable_products = applicable_products_str
    if price.remarks is not None:
        db_price.remarks = price.remarks

    db.commit()
    db.refresh(db_price)
    return db_price


@router.delete("/{price_id}")
def delete_superimposed_price(price_id: int, db: Session = Depends(get_db)):
    """删除叠加单价数据"""
    db_price = db.query(SuperimposedPrice).filter(SuperimposedPrice.id == price_id).first()
    if not db_price:
        raise HTTPException(status_code=404, detail="叠加单价数据不存在")

    db.delete(db_price)
    db.commit()
    return {"ok": True}


@router.delete("/clear")
def clear_superimposed_prices(db: Session = Depends(get_db)):
    """清空所有叠加单价数据"""
    try:
        db.query(SuperimposedPrice).delete()
        db.commit()
        return {"message": "所有叠加单价数据已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
