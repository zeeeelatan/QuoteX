"""语义噪声词候选 API 路由

提供：候选词列表/筛选、触发挖掘、批量审核(采纳/拒绝)、手动增删改。
审核为 approved 的词会进入 extractor 运行期词典生效。
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.semantic_noise_term import SemanticNoiseTerm
from app.schemas.semantic_noise_term import (
    SemanticNoiseTermCreate,
    SemanticNoiseTermUpdate,
    SemanticNoiseTermResponse,
    TermReviewRequest,
    MineResult,
)
from app.semantic.miner import mine_terms

router = APIRouter(prefix="/semantic-terms", tags=["语义词典"])


@router.get("/", response_model=List[SemanticNoiseTermResponse])
def list_terms(
    status: Optional[str] = Query(None, description="筛选状态: pending/approved/rejected"),
    term_type: Optional[str] = Query(None, description="筛选类型: device_type/modifier/series"),
    search: Optional[str] = Query(None, description="搜索词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    q = db.query(SemanticNoiseTerm)
    if status:
        q = q.filter(SemanticNoiseTerm.status == status)
    if term_type:
        q = q.filter(SemanticNoiseTerm.term_type == term_type)
    if search:
        q = q.filter(SemanticNoiseTerm.term.ilike(f"%{search}%"))
    # 待审核优先、按频次降序
    q = q.order_by(
        SemanticNoiseTerm.status.asc(),
        SemanticNoiseTerm.frequency.desc(),
    )
    return q.offset(skip).limit(limit).all()


@router.get("/stats")
def term_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    rows = (
        db.query(SemanticNoiseTerm.status, func.count(SemanticNoiseTerm.id))
        .group_by(SemanticNoiseTerm.status)
        .all()
    )
    stats = {"pending": 0, "approved": 0, "rejected": 0}
    for s, c in rows:
        stats[s] = c
    stats["total"] = sum(stats.values())
    return stats


@router.post("/mine", response_model=MineResult)
def trigger_mine(db: Session = Depends(get_db)):
    """从已确认手动匹配记录挖掘噪声词候选（写入 pending）。"""
    result = mine_terms(db)
    return result


@router.post("/review")
def review_terms(req: TermReviewRequest, db: Session = Depends(get_db)):
    """批量审核：采纳(approved)或拒绝(rejected)。"""
    if req.status not in ("approved", "rejected", "pending"):
        raise HTTPException(status_code=400, detail="status 必须是 approved/rejected/pending")
    updated = (
        db.query(SemanticNoiseTerm)
        .filter(SemanticNoiseTerm.id.in_(req.ids))
        .update({SemanticNoiseTerm.status: req.status}, synchronize_session=False)
    )
    db.commit()
    return {"updated": updated, "status": req.status}


@router.post("/", response_model=SemanticNoiseTermResponse)
def create_term(data: SemanticNoiseTermCreate, db: Session = Depends(get_db)):
    """手动新增噪声词。"""
    existing = db.query(SemanticNoiseTerm).filter(SemanticNoiseTerm.term == data.term).first()
    if existing:
        raise HTTPException(status_code=409, detail="该词已存在")
    obj = SemanticNoiseTerm(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{term_id}", response_model=SemanticNoiseTermResponse)
def update_term(term_id: int, data: SemanticNoiseTermUpdate, db: Session = Depends(get_db)):
    obj = db.query(SemanticNoiseTerm).filter(SemanticNoiseTerm.id == term_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{term_id}")
def delete_term(term_id: int, db: Session = Depends(get_db)):
    obj = db.query(SemanticNoiseTerm).filter(SemanticNoiseTerm.id == term_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}
