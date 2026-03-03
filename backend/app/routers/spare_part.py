from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
import pandas as pd
import io
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.models.spare_part import SparePart
from app.schemas.spare_part import SparePartOut

router = APIRouter(prefix="/spare_parts", tags=["备件管理"])


@router.get("/", response_model=List[SparePartOut])
def list_spare_parts(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=200, description="每页记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """分页查询备件列表"""
    query = db.query(SparePart)
    
    # 搜索过滤
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                SparePart.manufacturer.ilike(search_pattern),
                SparePart.part_pn.ilike(search_pattern),
                SparePart.part_desc.ilike(search_pattern),
                SparePart.part_category.ilike(search_pattern)
            )
        )
    
    # 排序和分页
    return query.order_by(SparePart.id.desc()).offset(skip).limit(limit).all()


@router.get("/count")
def get_spare_parts_count(
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """获取备件总数"""
    query = db.query(func.count(SparePart.id))
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                SparePart.manufacturer.ilike(search_pattern),
                SparePart.part_pn.ilike(search_pattern),
                SparePart.part_desc.ilike(search_pattern),
                SparePart.part_category.ilike(search_pattern)
            )
        )
    
    return {"total": query.scalar()}


@router.get("/template")
def download_template(fmt: str = Query("xlsx", pattern="^(xlsx|csv)$")):
    columns = ['序号','厂商','备件PN','备件描述','备件分类','备件成色','报修方式','报修期限','单价']
    df = pd.DataFrame(columns=columns)
    if fmt == 'csv':
        content = df.to_csv(index=False).encode('utf-8-sig')
        bio = io.BytesIO(content)
        bio.seek(0)
        return StreamingResponse(bio, media_type='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename="spare_part_template.csv"'})
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='模板')
        output.seek(0)
        return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': 'attachment; filename="spare_part_template.xlsx"'})
    except Exception:
        content = df.to_csv(index=False).encode('utf-8-sig')
        bio = io.BytesIO(content)
        bio.seek(0)
        return StreamingResponse(bio, media_type='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename="spare_part_template.csv"'})


@router.post("/import")
async def import_spare_parts(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = await file.read()
    bio = io.BytesIO(raw)
    try:
        xls = pd.ExcelFile(bio)
        frames = [xls.parse(sn) for sn in xls.sheet_names]
        df = pd.concat(frames, ignore_index=True)
    except Exception:
        bio.seek(0)
        df = pd.read_excel(bio)

    cn2field = {
        '厂商': 'manufacturer',
        '备件PN': 'part_pn',
        '备件描述': 'part_desc',
        '备件分类': 'part_category',
        '备件成色': 'part_condition',
        '报修方式': 'repair_method',
        '报修期限': 'repair_period',
        '单价': 'unit_price',
    }
    df = df.rename(columns=cn2field)
    keep = ['manufacturer','part_pn','part_desc','part_category','part_condition','repair_method','repair_period','unit_price']
    df = df[[c for c in keep if c in df.columns]].copy()

    def to_float(x):
        try:
            s = str(x).replace(',', '').replace('¥','').replace('￥','').strip()
            return float(s) if s not in (None,'','nan') else 0.0
        except Exception:
            return 0.0

    if 'unit_price' in df.columns:
        df['unit_price'] = df['unit_price'].apply(to_float)

    # 清空并导入
    db.query(SparePart).delete()
    db.commit()
    records = df.to_dict(orient='records')
    objs = [SparePart(**r) for r in records]
    if objs:
        db.bulk_save_objects(objs)
        db.commit()
    return {"ok": True, "count": len(objs)}


@router.delete("/clear")
def clear_spare_parts(db: Session = Depends(get_db)):
    db.query(SparePart).delete()
    db.commit()
    return {"ok": True}


