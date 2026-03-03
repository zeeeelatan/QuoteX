from pydantic import BaseModel


class SparePartBase(BaseModel):
    manufacturer: str
    part_pn: str
    part_desc: str
    part_category: str
    part_condition: str
    repair_method: str
    repair_period: str
    unit_price: float


class SparePartCreate(SparePartBase):
    pass


class SparePartUpdate(SparePartBase):
    pass


class SparePartOut(SparePartBase):
    id: int
    class Config:
        from_attributes = True


