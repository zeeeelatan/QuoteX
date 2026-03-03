from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class OfficeDeviceInventoryBase(BaseModel):
    """办公设备库存基础模型"""
    manufacturer: Optional[str] = Field(None, description="厂商")
    model_number: Optional[str] = Field(None, description="设备型号")
    primary_category: Optional[str] = Field(None, description="一级分类")
    secondary_category: Optional[str] = Field(None, description="二级分类")
    tertiary_category: Optional[str] = Field(None, description="三级分类")
    business_scenario: Optional[str] = Field(None, description="业务场景")
    remarks: Optional[str] = Field(None, description="备注")
    device_grade: Optional[str] = Field(None, description="设备档次")
    device_series: Optional[str] = Field(None, description="设备系列")
    device_price: Optional[Decimal] = Field(None, description="整机价格")


class OfficeDeviceInventoryCreate(OfficeDeviceInventoryBase):
    """创建办公设备"""
    pass


class OfficeDeviceInventoryUpdate(OfficeDeviceInventoryBase):
    """更新办公设备"""
    pass


class OfficeDeviceInventoryOut(OfficeDeviceInventoryBase):
    """办公设备输出模型"""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class OfficeDeviceInventoryListResponse(BaseModel):
    """办公设备列表响应"""
    data: list[OfficeDeviceInventoryOut]
    total: int
