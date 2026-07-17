from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.quote_history import QuoteHistory
from app.models.quote_live_snapshot import QuoteLiveSnapshot
from app.models.user_profile import UserProfile
from app.schemas.quote_history import (
    QuoteHistoryCreate,
    QuoteHistoryOut,
    QuoteHistoryListItem,
    QuoteHistoryUpdate,
    QuoteLiveSnapshotUpsert,
    QuoteLiveSnapshotOut,
)
from app.auth import get_current_user_id, get_current_user_required

router = APIRouter(prefix="/quote-history", tags=["历史记录"])


def _filter_by_user(query, user_id: Optional[int]):
    if user_id is not None:
        return query.filter(QuoteHistory.user_id == user_id)
    return query.filter(QuoteHistory.user_id.is_(None))


@router.get("/", response_model=List[QuoteHistoryListItem])
def get_quote_history(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=200, description="返回记录数"),
    status: Optional[str] = Query(None, description="状态筛选: completed, processing, failed, draft"),
    search: Optional[str] = Query(None, description="搜索关键词: 文件名或用户名"),
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取历史记录列表（按当前用户隔离；未登录仅返回无主数据）"""
    query = _filter_by_user(db.query(QuoteHistory), user_id)
    if status:
        query = query.filter(QuoteHistory.status == status)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (QuoteHistory.file_name.ilike(search_pattern)) |
            (QuoteHistory.user_name.ilike(search_pattern))
        )
    order_column = QuoteHistory.updated_at if status == 'draft' else QuoteHistory.created_at
    query = query.order_by(order_column.desc())
    return query.offset(skip).limit(limit).all()


@router.get("/drafts", response_model=List[QuoteHistoryListItem])
def get_drafts(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=200, description="返回记录数"),
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取草稿列表（按当前用户隔离）"""
    query = _filter_by_user(db.query(QuoteHistory).filter(QuoteHistory.status == 'draft'), user_id)
    query = query.order_by(QuoteHistory.updated_at.desc())
    return query.offset(skip).limit(limit).all()


@router.get("/count")
def get_quote_history_count(
    status: Optional[str] = Query(None, description="状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取历史记录总数（按当前用户隔离）"""
    query = _filter_by_user(db.query(QuoteHistory), user_id)
    if status:
        query = query.filter(QuoteHistory.status == status)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (QuoteHistory.file_name.ilike(search_pattern)) |
            (QuoteHistory.user_name.ilike(search_pattern))
        )
    return {"total": query.count()}


@router.get("/today-count")
def get_today_quote_count(db: Session = Depends(get_db)):
    """获取今日及昨日所有用户生成的报价单数量（不区分用户），用于趋势对比"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    completed_filter = QuoteHistory.status == 'completed'
    today_count = db.query(func.count(QuoteHistory.id)).filter(
        func.date(QuoteHistory.created_at) == today, completed_filter,
    ).scalar() or 0
    yesterday_count = db.query(func.count(QuoteHistory.id)).filter(
        func.date(QuoteHistory.created_at) == yesterday, completed_filter,
    ).scalar() or 0
    total_count = db.query(func.count(QuoteHistory.id)).filter(
        completed_filter,
    ).scalar() or 0
    online_threshold = datetime.utcnow() - timedelta(minutes=15)
    online_count = db.query(func.count(UserProfile.id)).filter(
        UserProfile.last_active_at >= online_threshold,
    ).scalar() or 0
    return {
        "today_count": today_count,
        "yesterday_count": yesterday_count,
        "total_count": total_count,
        "online_count": online_count,
    }


@router.get("/by-ref/{ref}", response_model=QuoteHistoryOut)
def get_quote_history_by_ref(ref: str, db: Session = Depends(get_db)):
    """
    按外部引用令牌(external_ref)查询报价结果，供第三方系统（如 TopSales）集成使用。

    与常规的 /quote-history/{id} 不同，本接口不做用户身份校验：
    ref 由调用方系统生成的高强度随机字符串（如 UUID）充当一次性查询凭证，
    只要不外泄该 ref，安全性即等价于"分享链接"模式。

    调用方需在发起询价时把 ref 作为 URL 参数带给本系统前端
    （见 DocumentRecognition.vue 对 route.query.ref 的读取），
    并在 QuotationGeneration.vue 完成保存时把 ref 写入 quote_metadata.external_ref。
    """
    if not ref or len(ref) < 8:
        raise HTTPException(status_code=400, detail="无效的引用令牌")
    history = (
        db.query(QuoteHistory)
        .filter(QuoteHistory.quote_metadata["external_ref"].as_string() == ref)
        .order_by(QuoteHistory.created_at.desc())
        .first()
    )
    if not history:
        raise HTTPException(status_code=404, detail="未找到对应的报价结果，请确认已在生成报价页完成保存")
    return history


@router.put("/live-by-ref/{ref}", response_model=QuoteLiveSnapshotOut)
def upsert_live_snapshot(ref: str, payload: QuoteLiveSnapshotUpsert, db: Session = Depends(get_db)):
    """
    按外部引用令牌(external_ref) upsert "生成报价单"页面的实时快照。

    由本系统前端在报价值变化时（防抖）及"导出Excel"完成后推送，
    供第三方系统（如 TopSales）在用户点击"完成报价"前实时拉取报价结果。
    安全模型与 by-ref 一致：ref 为调用方生成的高强度随机凭证。
    data 与 files 均为可选，只更新传入的字段（互不覆盖）。
    """
    if not ref or len(ref) < 8:
        raise HTTPException(status_code=400, detail="无效的引用令牌")
    snapshot = db.query(QuoteLiveSnapshot).filter(QuoteLiveSnapshot.external_ref == ref).first()
    if not snapshot:
        snapshot = QuoteLiveSnapshot(external_ref=ref)
        db.add(snapshot)
    if payload.data is not None:
        snapshot.data = payload.data
    if payload.files is not None:
        snapshot.files = payload.files
    snapshot.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(snapshot)
    return snapshot


@router.get("/live-by-ref/{ref}", response_model=QuoteLiveSnapshotOut)
def get_live_snapshot(ref: str, db: Session = Depends(get_db)):
    """按外部引用令牌查询实时报价快照（供第三方系统轮询/按需拉取）"""
    if not ref or len(ref) < 8:
        raise HTTPException(status_code=400, detail="无效的引用令牌")
    snapshot = db.query(QuoteLiveSnapshot).filter(QuoteLiveSnapshot.external_ref == ref).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="未找到实时报价数据，请确认已在生成报价单页面打开本次询价")
    return snapshot


@router.get("/{history_id}", response_model=QuoteHistoryOut)
def get_quote_history_detail(
    history_id: int,
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取历史记录详情（仅当前用户可访问）"""
    history = db.query(QuoteHistory).filter(QuoteHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    if user_id is not None and history.user_id is not None and history.user_id != user_id:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    if user_id is None and history.user_id is not None:
        raise HTTPException(status_code=401, detail="请先登录")
    return history


@router.post("/", response_model=QuoteHistoryOut)
def create_quote_history(
    data: QuoteHistoryCreate,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """创建历史记录（需登录，归属当前用户）"""
    history = QuoteHistory(
        user_id=user_id,
        file_name=data.file_name,
        user_name=data.user_name,
        status=data.status,
        total_amount=data.total_amount,
        import_data=data.import_data,
        match_data=data.match_data,
        price_adjust_data=data.price_adjust_data,
        quote_data=data.quote_data,
        quote_metadata=data.quote_metadata,
        page_states=data.page_states,
        data_source=data.data_source,
        device_count=data.device_count,
        draft_stage=data.draft_stage,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


@router.put("/{history_id}", response_model=QuoteHistoryOut)
def update_quote_history(
    history_id: int,
    data: QuoteHistoryUpdate,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """更新历史记录（仅当前用户）"""
    history = db.query(QuoteHistory).filter(QuoteHistory.id == history_id, QuoteHistory.user_id == user_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="历史记录不存在")

    # 更新字段
    if data.status is not None:
        history.status = data.status
    if data.total_amount is not None:
        history.total_amount = data.total_amount
    if data.import_data is not None:
        history.import_data = data.import_data
    if data.match_data is not None:
        history.match_data = data.match_data
    if data.price_adjust_data is not None:
        history.price_adjust_data = data.price_adjust_data
    if data.quote_data is not None:
        history.quote_data = data.quote_data
    if data.quote_metadata is not None:
        history.quote_metadata = data.quote_metadata
    if data.page_states is not None:
        history.page_states = data.page_states
    if data.data_source is not None:
        history.data_source = data.data_source
    if data.device_count is not None:
        history.device_count = data.device_count
    if data.draft_stage is not None:
        history.draft_stage = data.draft_stage

    db.commit()
    db.refresh(history)

    return history


@router.delete("/{history_id}")
def delete_quote_history(
    history_id: int,
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """删除历史记录：有主草稿仅本人可删，无主草稿（user_id 为空）任何人可删"""
    history = db.query(QuoteHistory).filter(QuoteHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    if history.user_id is not None:
        if user_id is None:
            raise HTTPException(status_code=401, detail="请先登录后删除该草稿")
        if history.user_id != user_id:
            raise HTTPException(status_code=404, detail="历史记录不存在")
    db.delete(history)
    db.commit()
    return {"message": "删除成功"}
