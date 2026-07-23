from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InternationalCountryRuleUpdate(BaseModel):
    exchange_rate_cny: Optional[float] = Field(None, gt=0)
    exchange_rate_date: Optional[date] = None
    eor_rate: Optional[float] = Field(None, ge=0)
    management_rate: Optional[float] = Field(None, ge=0)
    profit_rate: Optional[float] = Field(None, ge=0)
    vat_rate: Optional[float] = Field(None, ge=0)
    local_vat_rate: Optional[float] = Field(None, ge=0)
    local_vat_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class InternationalCountryRuleOut(BaseModel):
    id: int
    country_code: str
    country_name: str
    default_city: str
    currency: str
    currency_symbol: str
    currency_precision: int
    exchange_rate_cny: float
    exchange_rate_date: date
    eor_rate: float
    management_rate: float
    profit_rate: float
    vat_rate: float
    local_vat_rate: float
    local_vat_enabled: bool
    effective_label: str
    employee_profile: str
    parameter_config: List[Dict[str, Any]]
    is_active: bool

    class Config:
        from_attributes = True


class InternationalJobSalaryBase(BaseModel):
    country_code: str = Field(..., min_length=1, max_length=32)
    country_name: str = Field(..., min_length=1, max_length=64)
    region: str = Field("", max_length=128)
    city: str = Field(..., min_length=1, max_length=64)
    currency: str = Field(..., min_length=3, max_length=8)
    sequence_type: str = Field(..., min_length=1, max_length=32)
    category: str = Field(..., min_length=1, max_length=64)
    position_name: str = Field(..., min_length=1, max_length=128)
    level_name: str = Field(..., min_length=1, max_length=128)
    level_rank: int = Field(..., ge=1, le=10)
    monthly_salary: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class InternationalJobSalaryCreate(InternationalJobSalaryBase):
    pass


class InternationalJobSalaryUpdate(BaseModel):
    region: Optional[str] = Field(None, max_length=128)
    city: Optional[str] = Field(None, min_length=1, max_length=64)
    monthly_salary: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class InternationalJobSalaryOut(InternationalJobSalaryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InternationalCalculationRequest(BaseModel):
    country_code: str
    monthly_salary: float = Field(..., ge=0)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class InternationalEmployerRuleOut(BaseModel):
    type: str
    min_base: float = 0
    max_base: float = 0
    corp_rate: float
    indiv_rate: float = 0
    calc_base: float
    amount: float
    basis: str


class InternationalCalculationOut(BaseModel):
    country_code: str
    currency: str
    currency_precision: int
    employer_rules: List[InternationalEmployerRuleOut]
    employer_total: float
