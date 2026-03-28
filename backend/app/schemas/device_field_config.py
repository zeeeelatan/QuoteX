from pydantic import BaseModel, Field
from typing import Optional, Any


class DeviceFieldConfigBase(BaseModel):
    device_type: Optional[str] = Field(None, description="设备类型(一级分类)，NULL表示全局通用")
    field_key: str = Field(..., description="字段标识")
    field_label: str = Field(..., description="字段显示名")
    field_type: str = Field("string", description="字段类型: string/number/enum/boolean")
    required: bool = Field(False, description="是否必填")
    enum_options: Optional[list[Any]] = Field(None, description="枚举选项列表")
    default_value: Optional[str] = Field(None, description="默认值")
    display_order: int = Field(0, description="显示排序")
    scope: str = Field("type", description="作用域: type(类型级)/instance(实例级)")


class DeviceFieldConfigCreate(DeviceFieldConfigBase):
    pass


class DeviceFieldConfigUpdate(BaseModel):
    device_type: Optional[str] = None
    field_key: Optional[str] = None
    field_label: Optional[str] = None
    field_type: Optional[str] = None
    required: Optional[bool] = None
    enum_options: Optional[list[Any]] = None
    default_value: Optional[str] = None
    display_order: Optional[int] = None
    scope: Optional[str] = None


class DeviceFieldConfigOut(DeviceFieldConfigBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class DeviceFieldConfigListResponse(BaseModel):
    data: list[DeviceFieldConfigOut]
    total: int
