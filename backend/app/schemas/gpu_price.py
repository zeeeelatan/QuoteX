from pydantic import BaseModel


class GPUPriceBase(BaseModel):
    manufacturer: str | None = None
    series: str | None = None
    model: str | None = None
    gpu_memory: str | None = None
    gpu_interface_type: str | None = None
    sales_status: str | None = None

    gpu_price: float
    gpu_rate: float              # 小数，例如 0.06
    spare_repair_cost: float
    labor_repair_cost: float
    service_fee: float


class GPUPriceCreate(GPUPriceBase):
    pass


class GPUPriceUpdate(GPUPriceBase):
    pass


class GPUPriceOut(GPUPriceBase):
    id: int
    class Config:
        from_attributes = True



