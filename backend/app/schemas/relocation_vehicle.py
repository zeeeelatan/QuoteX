"""
机房搬迁车型数据 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class RelocationVehicleBase(BaseModel):
    seq_no: Optional[int] = None
    vehicle_category: Optional[str] = None
    vehicle_name: Optional[str] = None
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    height_m: Optional[float] = None
    volume_m3: Optional[float] = None
    load_ton: Optional[float] = None
    server_1u: Optional[str] = None
    server_2u: Optional[str] = None
    rack_count: Optional[str] = None
    scenario: Optional[str] = None
    distance_advice: Optional[str] = None
    license_required: Optional[str] = None
    city_restrict: Optional[str] = None
    basement_limit: Optional[str] = None
    start_price: Optional[str] = None
    km_price: Optional[str] = None
    remark: Optional[str] = None


class RelocationVehicleCreate(RelocationVehicleBase):
    pass


class RelocationVehicleUpdate(BaseModel):
    seq_no: Optional[int] = None
    vehicle_category: Optional[str] = None
    vehicle_name: Optional[str] = None
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    height_m: Optional[float] = None
    volume_m3: Optional[float] = None
    load_ton: Optional[float] = None
    server_1u: Optional[str] = None
    server_2u: Optional[str] = None
    rack_count: Optional[str] = None
    scenario: Optional[str] = None
    distance_advice: Optional[str] = None
    license_required: Optional[str] = None
    city_restrict: Optional[str] = None
    basement_limit: Optional[str] = None
    start_price: Optional[str] = None
    km_price: Optional[str] = None
    remark: Optional[str] = None


class RelocationVehicleOut(RelocationVehicleBase):
    id: int

    class Config:
        from_attributes = True
