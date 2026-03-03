"""
派单服务数据 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional


class DispatchServiceBase(BaseModel):
    """派单服务基础字段"""
    service_type: str = Field(..., description="服务类型")
    unit_hours: str = Field(..., description="单位工时")
    time_window: str = Field(..., description="服务时间窗口")
    response_time: str = Field(..., description="响应时效")
    city_tier: str = Field(..., description="城市等级")
    price: float = Field(..., gt=0, description="服务价格")
    description: Optional[str] = Field(None, description="描述说明")


class DispatchServiceCreate(DispatchServiceBase):
    """创建派单服务数据"""
    pass


class DispatchServiceUpdate(BaseModel):
    """更新派单服务数据（所有字段可选）"""
    service_type: Optional[str] = None
    unit_hours: Optional[str] = None
    time_window: Optional[str] = None
    response_time: Optional[str] = None
    city_tier: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None


class DispatchServiceOut(DispatchServiceBase):
    """派单服务数据输出"""
    id: int

    class Config:
        from_attributes = True
