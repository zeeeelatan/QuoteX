from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# 服务人员 Schema
class ServicePersonnelBase(BaseModel):
    personnel_type: str = Field(..., description="服务人员类型，如 桌面运维工程师")
    skill_description: Optional[str] = Field(None, description="技能描述")
    skill_level: str = Field(..., description="能力级别：专家、高级、中级、初级")
    service_mode: str = Field(..., description="服务模式：远程、现场")
    daily_rate: float = Field(..., description="人天单价")
    tags: Optional[str] = Field(None, description="特长标签，多个标签用逗号分隔")


class ServicePersonnelCreate(ServicePersonnelBase):
    pass


class ServicePersonnelUpdate(BaseModel):
    personnel_type: Optional[str] = None
    skill_description: Optional[str] = None
    skill_level: Optional[str] = None
    service_mode: Optional[str] = None
    daily_rate: Optional[float] = None
    tags: Optional[str] = None


class ServicePersonnelOut(ServicePersonnelBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
