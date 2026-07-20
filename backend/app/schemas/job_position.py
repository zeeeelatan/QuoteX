from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ---------- 岗位职级 ----------

class JobPositionBase(BaseModel):
    sequence_type: str = Field(..., description="序列类型（技术序列/管理序列）")
    category: str = Field(..., description="岗位类别/管理方向")
    position_name: str = Field(..., description="岗位名称")
    level_name: str = Field(..., description="技术级别/管理级别全称")
    level_rank: int = Field(1, description="级别排序（1最低）")
    system_salary_max: Optional[float] = Field(None, ge=0, description="系统允许的税前月薪最大值(元)")
    system_salary_min: Optional[float] = Field(None, ge=0, description="系统允许的税前月薪最小值(元)")
    core_requirements: Optional[str] = Field(None, description="级别核心要求")
    certifications: Optional[str] = Field(None, description="适用认证参考")
    work_content: Optional[str] = Field(None, description="工作内容")
    deliverables: Optional[str] = Field(None, description="工作产出/交付物")
    kpi_standards: Optional[str] = Field(None, description="KPI考核点及标准参考值")


class JobPositionCreate(JobPositionBase):
    pass


class JobPositionUpdate(BaseModel):
    sequence_type: Optional[str] = None
    category: Optional[str] = None
    position_name: Optional[str] = None
    level_name: Optional[str] = None
    level_rank: Optional[int] = None
    system_salary_max: Optional[float] = Field(None, ge=0)
    system_salary_min: Optional[float] = Field(None, ge=0)
    core_requirements: Optional[str] = None
    certifications: Optional[str] = None
    work_content: Optional[str] = None
    deliverables: Optional[str] = None
    kpi_standards: Optional[str] = None


class JobPositionOut(JobPositionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobPositionListItem(BaseModel):
    """列表项（不含大文本字段）"""
    id: int
    sequence_type: str
    category: str
    position_name: str
    level_name: str
    level_rank: int
    system_salary_max: Optional[float] = None
    system_salary_min: Optional[float] = None
    salary_city_count: int = 0

    class Config:
        from_attributes = True


class JobPositionDetail(JobPositionOut):
    salary_city_count: int = 0


class JobPositionOption(BaseModel):
    """测算器下拉选项"""
    id: int
    sequence_type: str
    category: str
    position_name: str
    level_name: str
    level_rank: int
    system_salary_max: Optional[float] = None
    system_salary_min: Optional[float] = None


# ---------- 城市薪资 ----------

class SalaryItem(BaseModel):
    id: int
    province: Optional[str] = None
    city: str
    salary: float

    class Config:
        from_attributes = True


class SalaryUpsert(BaseModel):
    city: str = Field(..., description="城市")
    salary: float = Field(..., ge=0, description="税前月薪(元)")
    province: Optional[str] = Field(None, description="省份")


class SalaryQueryResult(BaseModel):
    """薪资查询结果（含回退来源）"""
    position_id: int
    city: str
    salary: Optional[float] = None
    source: str = Field(..., description="exact/provincial_capital/national_baseline/none")
    source_city: Optional[str] = Field(None, description="薪资实际来源城市")


class SalaryBatchQueryItem(BaseModel):
    position_id: int
    city: str


class SalaryBatchQueryRequest(BaseModel):
    items: List[SalaryBatchQueryItem]
