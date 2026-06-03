from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List, Optional
from datetime import datetime

class ServiceLevelBase(BaseModel):
    level_code: str                                    # 服务等级
    response_time: str                                 # SLA 组合
    definition: Optional[str] = None                   # 释义
    aliases: List[str] = Field(default_factory=list)   # 别名列表
    coefficient: Decimal
    applicable_products: Optional[str] = None

class ServiceLevelCreate(ServiceLevelBase):
    pass

class ServiceLevelResponse(ServiceLevelBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
