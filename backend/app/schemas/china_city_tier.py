"""
中国城市分级表 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional


class ChinaCityTierBase(BaseModel):
    """中国城市分级基础字段"""
    seq_no: Optional[int] = Field(None, description="序号")
    city_tier: Optional[str] = Field(None, description="城市等级")
    tier_code: Optional[str] = Field(None, description="城市等级代码")
    city_name: str = Field(..., description="城市名称")
    province: Optional[str] = Field(None, description="所属省份")
    admin_level: Optional[str] = Field(None, description="行政级别")
    is_provincial_capital: Optional[str] = Field(None, description="是否省会")
    is_gdp_trillion: Optional[str] = Field(None, description="GDP万亿城市")
    logistics_hub_level: Optional[str] = Field(None, description="物流枢纽等级")
    remarks: Optional[str] = Field(None, description="备注")


class ChinaCityTierCreate(ChinaCityTierBase):
    """创建中国城市分级"""
    pass


class ChinaCityTierUpdate(BaseModel):
    """更新中国城市分级（所有字段可选）"""
    seq_no: Optional[int] = None
    city_tier: Optional[str] = None
    tier_code: Optional[str] = None
    city_name: Optional[str] = None
    province: Optional[str] = None
    admin_level: Optional[str] = None
    is_provincial_capital: Optional[str] = None
    is_gdp_trillion: Optional[str] = None
    logistics_hub_level: Optional[str] = None
    remarks: Optional[str] = None


class ChinaCityTierOut(ChinaCityTierBase):
    """中国城市分级输出"""
    id: int

    class Config:
        from_attributes = True
