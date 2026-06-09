"""语义噪声词候选 Pydantic Schemas"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SemanticNoiseTermBase(BaseModel):
    term: str = Field(..., description="噪声词/设备类型词")
    term_type: str = Field("device_type", description="词类型: device_type/modifier/series")
    lang: str = Field("cn", description="语言: cn/en")
    notes: Optional[str] = Field(None, description="备注")


class SemanticNoiseTermCreate(SemanticNoiseTermBase):
    """手动新增噪声词（直接生效需再审核为 approved）"""
    status: str = Field("approved", description="审核状态")
    source: str = Field("manual", description="来源")


class SemanticNoiseTermUpdate(BaseModel):
    term: Optional[str] = None
    term_type: Optional[str] = None
    status: Optional[str] = Field(None, description="审核状态: pending/approved/rejected")
    notes: Optional[str] = None


class SemanticNoiseTermResponse(SemanticNoiseTermBase):
    id: int
    frequency: int
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TermReviewRequest(BaseModel):
    """批量审核请求"""
    ids: List[int] = Field(..., description="待审核的候选词 ID 列表")
    status: str = Field(..., description="目标状态: approved/rejected")


class MineResult(BaseModel):
    """挖掘结果摘要"""
    scanned_records: int
    new_candidates: int
    updated_candidates: int
    total_pending: int
