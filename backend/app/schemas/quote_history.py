from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class QuoteHistoryCreate(BaseModel):
    """创建历史记录"""
    file_name: str
    user_name: str
    status: str = 'completed'
    total_amount: Optional[float] = None
    import_data: Optional[Dict[str, Any]] = None
    match_data: Optional[List[Dict[str, Any]]] = None
    price_adjust_data: Optional[List[Dict[str, Any]]] = None
    quote_data: Optional[Dict[str, Any]] = None
    quote_metadata: Optional[Dict[str, Any]] = None  # 报价单元数据
    page_states: Optional[Dict[str, Any]] = None  # 各页面UI状态
    data_source: str = 'datacenter'
    device_count: int = 0
    draft_stage: Optional[str] = None  # 草稿阶段


class QuoteHistoryUpdate(BaseModel):
    """更新历史记录"""
    status: Optional[str] = None
    total_amount: Optional[float] = None
    import_data: Optional[Dict[str, Any]] = None
    match_data: Optional[List[Dict[str, Any]]] = None
    price_adjust_data: Optional[List[Dict[str, Any]]] = None
    quote_data: Optional[Dict[str, Any]] = None
    quote_metadata: Optional[Dict[str, Any]] = None
    page_states: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    device_count: Optional[int] = None
    draft_stage: Optional[str] = None


class QuoteHistoryOut(BaseModel):
    """历史记录输出"""
    id: int
    file_name: str
    user_name: str
    status: str
    total_amount: Optional[float] = None
    device_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    draft_stage: Optional[str] = None
    # 快照数据
    import_data: Optional[Dict[str, Any]] = None
    match_data: Optional[List[Dict[str, Any]]] = None
    price_adjust_data: Optional[List[Dict[str, Any]]] = None
    quote_data: Optional[Dict[str, Any]] = None
    quote_metadata: Optional[Dict[str, Any]] = None  # 报价单元数据
    page_states: Optional[Dict[str, Any]] = None  # 各页面UI状态

    class Config:
        from_attributes = True


class QuoteLiveSnapshotUpsert(BaseModel):
    """实时报价快照 upsert（生成报价单页面推送）"""
    data: Optional[Dict[str, Any]] = None   # { subtotal, tax_rate, total, valid_days, ... }
    files: Optional[List[Dict[str, Any]]] = None  # [{ name, size, type, content(dataURL base64) }]


class QuoteLiveSnapshotOut(BaseModel):
    """实时报价快照输出"""
    external_ref: str
    data: Optional[Dict[str, Any]] = None
    files: Optional[List[Dict[str, Any]]] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuoteHistoryListItem(BaseModel):
    """历史记录列表项"""
    id: int
    file_name: str
    user_name: str
    status: str
    total_amount: Optional[float] = None
    device_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    draft_stage: Optional[str] = None

    class Config:
        from_attributes = True
