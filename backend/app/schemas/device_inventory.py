from pydantic import BaseModel, Field
from typing import Optional, Any
from decimal import Decimal


class DeviceInventoryBase(BaseModel):
    """设备库存基础模型"""
    manufacturer: Optional[str] = Field(None, description="厂商（原始文本，兼容过渡期）")
    manufacturer_id: Optional[int] = Field(None, description="品牌字典ID")
    manufacturer_name: Optional[str] = Field(None, description="标准品牌名称（冗余）")
    model_number: Optional[str] = Field(None, description="设备型号")
    primary_category: Optional[str] = Field(None, description="一级分类")
    secondary_category: Optional[str] = Field(None, description="二级分类")
    tertiary_category: Optional[str] = Field(None, description="三级分类")
    business_scenario: Optional[str] = Field(None, description="业务场景")
    remarks: Optional[str] = Field(None, description="备注")
    device_grade: Optional[str] = Field(None, description="设备档次")
    device_series: Optional[str] = Field(None, description="设备系列")
    device_price: Optional[Decimal] = Field(None, description="整机价格")
    rack_height_u: Optional[int] = Field(None, description="机架高度(U)（过渡期兼容）")
    type_attributes: Optional[dict[str, Any]] = Field(default_factory=dict, description="类型级扩展字段")
    custom_attributes: Optional[dict[str, Any]] = Field(default_factory=dict, description="实例级扩展字段")


class DeviceInventoryCreate(DeviceInventoryBase):
    """创建设备"""
    pass


class DeviceInventoryUpdate(DeviceInventoryBase):
    """更新设备"""
    pass


class DeviceInventoryOut(DeviceInventoryBase):
    """设备输出模型"""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class DeviceInventoryListResponse(BaseModel):
    """设备列表响应"""
    data: list[DeviceInventoryOut]
    total: int
