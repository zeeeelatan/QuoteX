from pydantic import BaseModel, Field
from typing import Optional


class ManufacturerBase(BaseModel):
    name: str = Field(..., description="标准品牌名称")
    aliases: list[str] = Field(default_factory=list, description="品牌别名列表")


class ManufacturerCreate(ManufacturerBase):
    pass


class ManufacturerUpdate(BaseModel):
    name: Optional[str] = Field(None, description="标准品牌名称")
    aliases: Optional[list[str]] = Field(None, description="品牌别名列表")


class ManufacturerOut(ManufacturerBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ManufacturerListResponse(BaseModel):
    data: list[ManufacturerOut]
    total: int
