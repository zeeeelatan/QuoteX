from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from datetime import datetime

class ServiceLevelBase(BaseModel):
    level_code: str
    response_time: str
    coefficient: Decimal
    applicable_products: Optional[str] = None  # 适用产品，JSON字符串

class ServiceLevelCreate(ServiceLevelBase):
    pass

class ServiceLevelResponse(ServiceLevelBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 