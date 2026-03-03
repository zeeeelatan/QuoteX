from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PricingParameterBase(BaseModel):
    parameter_category: str = Field(..., description="调价参数项")
    parameter_value: str = Field(..., description="调价参数值")
    applicable_products: Optional[str] = Field(None, description="适用产品")
    coefficient: float = Field(..., description="系数值")


class PricingParameterCreate(PricingParameterBase):
    pass


class PricingParameterUpdate(BaseModel):
    parameter_category: Optional[str] = None
    parameter_value: Optional[str] = None
    applicable_products: Optional[str] = None
    coefficient: Optional[float] = None


class PricingParameterOut(PricingParameterBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
