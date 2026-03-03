"""
手动匹配覆盖的 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ManualMatchingOverrideBase(BaseModel):
    """手动匹配覆盖基础 Schema"""
    original_manufacturer: Optional[str] = Field('', description="原始厂商（可为空）")
    original_model: str = Field(..., description="原始型号（必填）")
    matched_manufacturer: str = Field(..., description="匹配后厂商")
    matched_model_number: str = Field(..., description="匹配后型号")
    device_price: Optional[float] = Field(None, description="设备价格")
    primary_category: Optional[str] = Field(None, description="一级分类")
    secondary_category: Optional[str] = Field(None, description="二级分类")
    tertiary_category: Optional[str] = Field(None, description="三级分类")
    device_category: Optional[str] = Field(None, description="设备分类")
    data_source: str = Field("datacenter", description="数据来源: datacenter/office")
    notes: Optional[str] = Field(None, description="备注")

    @field_validator('original_model')
    @classmethod
    def validate_original_model(cls, v: str) -> str:
        """验证原始型号不能为空"""
        if not v or not v.strip():
            raise ValueError('原始型号不能为空')
        return v.strip()


class ManualMatchingOverrideCreate(ManualMatchingOverrideBase):
    """创建手动匹配覆盖"""
    pass


class ManualMatchingOverrideUpdate(BaseModel):
    """更新手动匹配覆盖"""
    is_confirmed: Optional[bool] = Field(None, description="是否已确认")
    notes: Optional[str] = Field(None, description="备注")


class ManualMatchingOverrideResponse(ManualMatchingOverrideBase):
    """手动匹配覆盖响应"""
    id: int
    is_confirmed: bool
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ManualMatchingOverrideList(BaseModel):
    """手动匹配覆盖列表项"""
    id: int
    original_manufacturer: str
    original_model: str
    matched_manufacturer: str
    matched_model_number: str
    device_price: Optional[float] = None
    primary_category: Optional[str] = None
    secondary_category: Optional[str] = None
    tertiary_category: Optional[str] = None
    device_category: Optional[str] = None
    data_source: str
    is_confirmed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ManualMatchRecord(BaseModel):
    """单条手动匹配记录（用于批量提交）"""
    original_manufacturer: Optional[str] = ''  # 原始厂商（可为空）
    original_model: str  # 原始型号（必填）
    matched_manufacturer: str
    matched_model_number: str
    device_price: Optional[float] = None
    primary_category: Optional[str] = None
    secondary_category: Optional[str] = None
    tertiary_category: Optional[str] = None
    device_category: Optional[str] = None
    data_source: str = "datacenter"

    @field_validator('original_model')
    @classmethod
    def validate_original_model(cls, v: str) -> str:
        """验证原始型号不能为空"""
        if not v or not v.strip():
            raise ValueError('原始型号不能为空')
        return v.strip()
