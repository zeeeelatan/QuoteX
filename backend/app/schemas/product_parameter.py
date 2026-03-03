from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# 基础费率 Schema
class BaseRateBase(BaseModel):
    level_code: str = Field(..., description="级别代码，如 gold, silver, bronze")
    level_name: str = Field(..., description="级别名称")
    level_desc: Optional[str] = Field(None, description="级别描述")
    rate_value: float = Field(..., description="费率值 (百分比，如18.5表示18.5%)")
    trend_value: Optional[float] = Field(None, description="趋势值 (百分比，如1.2表示+1.2%)")


class BaseRateCreate(BaseRateBase):
    pass


class BaseRateUpdate(BaseModel):
    level_code: Optional[str] = None
    level_name: Optional[str] = None
    level_desc: Optional[str] = None
    rate_value: Optional[float] = None
    trend_value: Optional[float] = None


class BaseRateOut(BaseRateBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# SLA配置 Schema (调节系数配置)
class SLAConfigBase(BaseModel):
    coefficient_name: str = Field(..., description="系数名称")
    description: Optional[str] = Field(None, description="描述")
    coefficient: float = Field(..., description="成本系数")


class SLAConfigCreate(SLAConfigBase):
    pass


class SLAConfigUpdate(BaseModel):
    coefficient_name: Optional[str] = None
    description: Optional[str] = None
    coefficient: Optional[float] = None


class SLAConfigOut(BaseModel):
    id: int
    coefficient_name: Optional[str] = None
    description: Optional[str] = None
    coefficient: float
    # 保留旧字段以兼容前端
    sla_name: Optional[str] = None
    sla_name_cn: Optional[str] = None
    response_time: Optional[str] = None
    repair_time: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 硬件折旧 Schema
class HardwareDepreciationBase(BaseModel):
    device_type: str = Field(..., description="设备类型")
    rate_value: float = Field(..., description="年折旧率 (百分比，如2.5表示2.5%)")


class HardwareDepreciationCreate(HardwareDepreciationBase):
    pass


class HardwareDepreciationUpdate(BaseModel):
    device_type: Optional[str] = None
    rate_value: Optional[float] = None


class HardwareDepreciationOut(HardwareDepreciationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 区域调节 Schema
class RegionalAdjustmentBase(BaseModel):
    region_code: str = Field(..., description="区域代码")
    region_name: str = Field(..., description="区域名称")
    coefficient: float = Field(..., description="调节系数")


class RegionalAdjustmentCreate(RegionalAdjustmentBase):
    pass


class RegionalAdjustmentUpdate(BaseModel):
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    coefficient: Optional[float] = None


class RegionalAdjustmentOut(RegionalAdjustmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 组合输出 - 用于一次性获取所有配置
class ProductParametersOut(BaseModel):
    base_rates: list[BaseRateOut]
    sla_configs: list[SLAConfigOut]
    hardware_depreciations: list[HardwareDepreciationOut]
    regional_adjustments: list[RegionalAdjustmentOut]
