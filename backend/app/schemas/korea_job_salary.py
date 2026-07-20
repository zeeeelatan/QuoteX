from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class KoreaJobSalaryBase(BaseModel):
    city: str = Field(..., min_length=1, max_length=50)
    position_name: str = Field(..., min_length=1, max_length=128)
    monthly_salary_krw: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class KoreaJobSalaryCreate(KoreaJobSalaryBase):
    pass


class KoreaJobSalaryUpdate(BaseModel):
    city: Optional[str] = Field(None, min_length=1, max_length=50)
    position_name: Optional[str] = Field(None, min_length=1, max_length=128)
    monthly_salary_krw: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class KoreaJobSalaryOut(KoreaJobSalaryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
