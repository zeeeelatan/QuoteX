from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.quote_history import QuoteHistory
from app.schemas.quote_history import QuoteHistoryCreate, QuoteHistoryOut, QuoteHistoryListItem, QuoteHistoryUpdate
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
