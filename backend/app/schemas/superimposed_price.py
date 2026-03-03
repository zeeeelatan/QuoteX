"""
叠加单价数据 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class SuperimposedPriceBase(BaseModel):
    """叠加单价基础字段"""
    price_description: str = Field(..., description="单价说明")
    charging_standard: str = Field(..., description="收费标准")
    applicable_products: Optional[List[str]] = Field(None, description="适用产品列表")
    remarks: Optional[str] = Field(None, description="备注")


class SuperimposedPriceCreate(BaseModel):
    """创建叠加单价数据"""
    price_description: str
    charging_standard: str
    applicable_products: Optional[List[str]] = None
    remarks: Optional[str] = None


class SuperimposedPriceUpdate(BaseModel):
    """更新叠加单价数据（所有字段可选）"""
    price_description: Optional[str] = None
    charging_standard: Optional[str] = None
    applicable_products: Optional[List[str]] = None
    remarks: Optional[str] = None


class SuperimposedPriceOut(BaseModel):
    """叠加单价数据输出"""
    id: int
    price_description: str
    charging_standard: str
    applicable_products: Optional[str] = None  # 存储为JSON字符串
    remarks: Optional[str] = None

    class Config:
        from_attributes = True
