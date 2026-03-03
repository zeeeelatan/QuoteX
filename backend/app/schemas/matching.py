from pydantic import BaseModel
from typing import Optional, List

class MatchRequest(BaseModel):
    manufacturer: str
    model: str
    category: Optional[str] = None
    source: Optional[str] = 'datacenter'

class MatchResponse(BaseModel):
    matched_model: Optional[str] = None
    match_rate: float
    price: Optional[float] = None
    device_price: Optional[float] = None
    rate: Optional[float] = None
    device_category: Optional[str] = None
    primary_category: Optional[str] = None
    secondary_category: Optional[str] = None
    tertiary_category: Optional[str] = None
    manufacturer: Optional[str] = None  # 匹配到的设备厂商
    device_series: Optional[str] = None  # 设备系列

class BulkMatchRequest(BaseModel):
    items: List[MatchRequest]
