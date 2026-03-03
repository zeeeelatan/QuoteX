"""
城市社保基准数据 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional


class CitySocialInsuranceBase(BaseModel):
    """城市社保基准基础字段"""
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    city_alias: Optional[str] = Field(None, description="城市别名")
    upper_limit: int = Field(..., description="社保基数上限")
    lower_limit: int = Field(..., description="社保基数下限")
    calc_base: int = Field(..., description="计算基数")
    injury_base: Optional[int] = Field(None, description="工伤扣款基数")
    corp_pension_rate: Optional[float] = Field(None, description="养老保险-公司比例")
    corp_medical_rate: Optional[float] = Field(None, description="医疗保险-公司比例")
    corp_injury_rate: Optional[float] = Field(None, description="工伤保险-公司比例")
    corp_maternity_rate: Optional[float] = Field(None, description="生育保险-公司比例")
    corp_unemployment_rate: Optional[float] = Field(None, description="失业保险-公司比例")
    corp_disability_rate: Optional[float] = Field(None, description="残保金-公司比例")
    corp_fund_rate: Optional[float] = Field(None, description="公积金-公司比例")
    indiv_pension_rate: Optional[float] = Field(None, description="养老保险-个人比例")
    indiv_medical_rate: Optional[float] = Field(None, description="医疗保险-个人比例")
    indiv_injury_rate: Optional[float] = Field(None, description="工伤保险-个人比例")
    indiv_maternity_rate: Optional[float] = Field(None, description="生育保险-个人比例")
    indiv_unemployment_rate: Optional[float] = Field(None, description="失业保险-个人比例")
    indiv_fund_rate: Optional[float] = Field(None, description="公积金-个人比例")
    is_active: Optional[bool] = Field(True, description="是否启用")
    remarks: Optional[str] = Field(None, description="备注")


class CitySocialInsuranceCreate(CitySocialInsuranceBase):
    """创建城市社保基准数据"""
    pass


class CitySocialInsuranceUpdate(BaseModel):
    """更新城市社保基准数据（所有字段可选）"""
    province: Optional[str] = None
    city: Optional[str] = None
    city_alias: Optional[str] = None
    upper_limit: Optional[int] = None
    lower_limit: Optional[int] = None
    calc_base: Optional[int] = None
    injury_base: Optional[int] = None
    corp_pension_rate: Optional[float] = None
    corp_medical_rate: Optional[float] = None
    corp_injury_rate: Optional[float] = None
    corp_maternity_rate: Optional[float] = None
    corp_unemployment_rate: Optional[float] = None
    corp_disability_rate: Optional[float] = None
    corp_fund_rate: Optional[float] = None
    indiv_pension_rate: Optional[float] = None
    indiv_medical_rate: Optional[float] = None
    indiv_injury_rate: Optional[float] = None
    indiv_maternity_rate: Optional[float] = None
    indiv_unemployment_rate: Optional[float] = None
    indiv_fund_rate: Optional[float] = None
    is_active: Optional[bool] = None
    remarks: Optional[str] = None


class CitySocialInsuranceOut(CitySocialInsuranceBase):
    """城市社保基准数据输出"""
    id: int

    class Config:
        from_attributes = True
