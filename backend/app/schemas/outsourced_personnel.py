from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OutsourcedPersonnelBase(BaseModel):
    position: str = Field(..., description="岗位")
    level: str = Field(..., description="级别")
    subtype: Optional[str] = Field(None, description="子类型（A/B）")
    education: str = Field(..., description="学历要求")
    language_requirement: str = Field(..., description="语言要求")
    work_experience: Optional[str] = Field(None, description="工作经验要求")
    general_ability: Optional[str] = Field(None, description="通用能力要求")
    technical_skill: Optional[str] = Field(None, description="专业技术要求")
    tier1_city_salary: Optional[float] = Field(None, description="一线城市参考月工资")


class OutsourcedPersonnelCreate(OutsourcedPersonnelBase):
    pass


class OutsourcedPersonnelUpdate(BaseModel):
    position: Optional[str] = None
    level: Optional[str] = None
    subtype: Optional[str] = None
    education: Optional[str] = None
    language_requirement: Optional[str] = None
    work_experience: Optional[str] = None
    general_ability: Optional[str] = None
    technical_skill: Optional[str] = None
    tier1_city_salary: Optional[float] = None


class OutsourcedPersonnelOut(OutsourcedPersonnelBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
