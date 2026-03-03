from pydantic import BaseModel

class MaintenanceRateBase(BaseModel):
    primary_category: str
    secondary_category: str
    tertiary_category: str
    rate: float  # 前端传百分比，后端存小数
    remark: str = ""

class MaintenanceRateCreate(MaintenanceRateBase):
    pass

class MaintenanceRateUpdate(MaintenanceRateBase):
    pass

class MaintenanceRateOut(MaintenanceRateBase):
    id: int
    class Config:
        from_attributes = True 