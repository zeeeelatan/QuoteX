from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SingleServiceBase(BaseModel):
    business_type: str = Field(..., description="业务类型")
    service_name: str = Field(..., description="服务名称")
    service_detail: str = Field(..., description="服务细项")
    device_type: str = Field(..., description="设备类型")
    device_level: str = Field(..., description="设备/服务级别")
    engineer_capability: str = Field(..., description="工程师能力标签")
    quantity: float = Field(..., description="数量")
    on_site_fee: float = Field(..., description="上门费用")
    base_hours: float = Field(..., description="基准工时数")
    base_hourly_rate: float = Field(..., description="基准工时费")
    unit: str = Field(..., description="单位")
    standard_quote: float = Field(..., description="标准报价")
    emergency_response: Optional[float] = Field(None, description="紧急响应系数")
    special_time_period: Optional[float] = Field(None, description="特殊时间段系数")
    tier1_city: Optional[float] = Field(None, description="一线城市系数")
    other_city: Optional[float] = Field(None, description="其他城市系数")
    remarks: Optional[str] = Field(None, description="备注")
    applicable_cities: Optional[str] = Field(None, description="适用城市")
    batch_demand: Optional[float] = Field(None, description="批量需求系数")


class SingleServiceCreate(SingleServiceBase):
    pass


class SingleServiceUpdate(BaseModel):
    business_type: Optional[str] = None
    service_name: Optional[str] = None
    service_detail: Optional[str] = None
    device_type: Optional[str] = None
    device_level: Optional[str] = None
    engineer_capability: Optional[str] = None
    quantity: Optional[float] = None
    on_site_fee: Optional[float] = None
    base_hours: Optional[float] = None
    base_hourly_rate: Optional[float] = None
    unit: Optional[str] = None
    standard_quote: Optional[float] = None
    emergency_response: Optional[float] = None
    special_time_period: Optional[float] = None
    tier1_city: Optional[float] = None
    other_city: Optional[float] = None
    remarks: Optional[str] = None
    applicable_cities: Optional[str] = None
    batch_demand: Optional[float] = None


class SingleServiceOut(SingleServiceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
