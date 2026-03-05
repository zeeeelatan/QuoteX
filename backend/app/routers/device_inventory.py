from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
import pandas as pd
import math
import io
from fastapi.responses import StreamingResponse
from datetime import datetime

from app.database import get_db
from app.models.device_inventory import DeviceInventory
from app.schemas.device_inventory import DeviceInventoryCreate, DeviceInventoryUpdate, DeviceInventoryOut, DeviceInventoryListResponse

router = APIRouter(prefix="/devices", tags=["设备库管理"])


def device_to_dict(device: DeviceInventory) -> dict:
    """将设备对象转换为字典"""
    return {
        "id": device.id,
        "manufacturer": device.manufacturer,
        "model_number": device.model_number,
        "primary_category": device.primary_category,
        "secondary_category": device.secondary_category,
        "tertiary_category": device.tertiary_category,
        "business_scenario": device.business_scenario,
        "remarks": device.remarks,
        "device_grade": device.device_grade,
        "device_series": device.device_series,
        "device_price": float(device.device_price) if device.device_price else None,
        "rack_height_u": device.rack_height_u,
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
    }


@router.get("/", response_model=DeviceInventoryListResponse)
def list_devices(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=200, description="每页记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    manufacturer: Optional[str] = Query(None, description="厂商筛选"),
    device_series: Optional[str] = Query(None, description="设备系列筛选"),
    business_scenario: Optional[str] = Query(None, description="业务场景筛选"),
    device_grade: Optional[str] = Query(None, description="设备档次筛选"),
    db: Session = Depends(get_db)
):
    """分页查询设备列表"""
    query = db.query(DeviceInventory)

    # 搜索过滤
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                DeviceInventory.manufacturer.ilike(search_pattern),
                DeviceInventory.model_number.ilike(search_pattern),
                DeviceInventory.device_series.ilike(search_pattern),
                DeviceInventory.remarks.ilike(search_pattern)
            )
        )

    # 厂商筛选
    if manufacturer:
        query = query.filter(DeviceInventory.manufacturer == manufacturer)

    # 设备系列筛选
    if device_series:
        query = query.filter(DeviceInventory.device_series.ilike(f"%{device_series}%"))

    # 业务场景筛选
    if business_scenario:
        query = query.filter(DeviceInventory.business_scenario.ilike(f"%{business_scenario}%"))

    # 设备档次筛选
    if device_grade:
        query = query.filter(DeviceInventory.device_grade == device_grade)

    # 获取总数
    total = query.count()

    # 排序和分页
    devices = query.order_by(DeviceInventory.id.desc()).offset(skip).limit(limit).all()

    return DeviceInventoryListResponse(
        data=[device_to_dict(d) for d in devices],
        total=total
    )


@router.get("/count")
def get_devices_count(
    search: Optional[str] = Query(None, description="搜索关键词"),
    manufacturer: Optional[str] = Query(None, description="厂商筛选"),
    device_series: Optional[str] = Query(None, description="设备系列筛选"),
    business_scenario: Optional[str] = Query(None, description="业务场景筛选"),
    device_grade: Optional[str] = Query(None, description="设备档次筛选"),
    db: Session = Depends(get_db)
):
    """获取设备总数"""
    query = db.query(func.count(DeviceInventory.id))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                DeviceInventory.manufacturer.ilike(search_pattern),
                DeviceInventory.model_number.ilike(search_pattern),
                DeviceInventory.device_series.ilike(search_pattern),
                DeviceInventory.remarks.ilike(search_pattern)
            )
        )

    if manufacturer:
        query = query.filter(DeviceInventory.manufacturer == manufacturer)

    if device_series:
        query = query.filter(DeviceInventory.device_series.ilike(f"%{device_series}%"))

    if business_scenario:
        query = query.filter(DeviceInventory.business_scenario.ilike(f"%{business_scenario}%"))

    if device_grade:
        query = query.filter(DeviceInventory.device_grade == device_grade)

    return {"total": query.scalar()}


@router.get("/manufacturers")
def get_manufacturers(db: Session = Depends(get_db)):
    """获取所有厂商列表"""
    manufacturers = db.query(DeviceInventory.manufacturer).distinct().all()
    return [m[0] for m in manufacturers if m[0]]


@router.get("/device-series")
def get_device_series(db: Session = Depends(get_db)):
    """获取所有设备系列列表"""
    series = db.query(DeviceInventory.device_series).distinct().all()
    return [s[0] for s in series if s[0]]


@router.get("/business-scenarios")
def get_business_scenarios(db: Session = Depends(get_db)):
    """获取所有业务场景列表"""
    scenarios = db.query(DeviceInventory.business_scenario).distinct().all()
    return [s[0] for s in scenarios if s[0]]


@router.get("/device-grades")
def get_device_grades(db: Session = Depends(get_db)):
    """获取所有设备档次列表"""
    grades = db.query(DeviceInventory.device_grade).distinct().all()
    return [g[0] for g in grades if g[0]]


@router.get("/{device_id}", response_model=DeviceInventoryOut)
def get_device(device_id: int, db: Session = Depends(get_db)):
    """获取单个设备详情"""
    device = db.query(DeviceInventory).filter(DeviceInventory.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device_to_dict(device)


@router.post("/", response_model=DeviceInventoryOut)
def create_device(device: DeviceInventoryCreate, db: Session = Depends(get_db)):
    """创建新设备"""
    db_device = DeviceInventory(**device.model_dump(exclude_unset=True))
    db_device.created_at = datetime.now()
    db_device.updated_at = datetime.now()
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return device_to_dict(db_device)


@router.put("/{device_id}", response_model=DeviceInventoryOut)
def update_device(device_id: int, device: DeviceInventoryUpdate, db: Session = Depends(get_db)):
    """更新设备信息"""
    db_device = db.query(DeviceInventory).filter(DeviceInventory.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="设备不存在")

    update_data = device.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_device, key, value)

    db_device.updated_at = datetime.now()
    db.commit()
    db.refresh(db_device)
    return device_to_dict(db_device)


@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """删除设备"""
    db_device = db.query(DeviceInventory).filter(DeviceInventory.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="设备不存在")

    db.delete(db_device)
    db.commit()
    return {"ok": True, "message": "设备删除成功"}


@router.get("/template/download")
def download_template(fmt: str = Query("xlsx", pattern="^(xlsx|csv)$")):
    """下载设备导入模板"""
    columns = [
        '厂商', '设备系列', '设备型号', '业务场景',
        '一级分类', '二级分类', '三级分类', '备注', '整机价格', '档次'
    ]
    df = pd.DataFrame(columns=columns)

    if fmt == 'csv':
        content = df.to_csv(index=False).encode('utf-8-sig')
        bio = io.BytesIO(content)
        bio.seek(0)
        return StreamingResponse(
            bio,
            media_type='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename="device_template.csv"'}
        )

    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='模板')
        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="device_template.xlsx"'}
        )
    except Exception:
        content = df.to_csv(index=False).encode('utf-8-sig')
        bio = io.BytesIO(content)
        bio.seek(0)
        return StreamingResponse(
            bio,
            media_type='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename="device_template.csv"'}
        )


@router.post("/import")
async def import_devices(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """批量导入设备"""
    raw = await file.read()
    bio = io.BytesIO(raw)

    try:
        xls = pd.ExcelFile(bio)
        frames = [xls.parse(sn) for sn in xls.sheet_names]
        df = pd.concat(frames, ignore_index=True)
    except Exception:
        bio.seek(0)
        df = pd.read_excel(bio)

    # 中文列名映射到英文字段名
    cn2field = {
        '厂商': 'manufacturer',
        '设备系列': 'device_series',
        '设备型号': 'model_number',
        '业务场景': 'business_scenario',
        '一级分类': 'primary_category',
        '二级分类': 'secondary_category',
        '三级分类': 'tertiary_category',
        '备注': 'remarks',
        '整机价格': 'device_price',
        '档次': 'device_grade',
    }

    df = df.rename(columns=cn2field)

    # 保留需要的字段
    keep_fields = [
        'manufacturer', 'device_series', 'model_number', 'business_scenario',
        'primary_category', 'secondary_category', 'tertiary_category',
        'remarks', 'device_price', 'device_grade'
    ]
    df = df[[c for c in keep_fields if c in df.columns]].copy()

    # 价格转换函数
    def to_float(x):
        try:
            s = str(x).replace(',', '').replace('¥', '').replace('￥', '').strip()
            return float(s) if s not in (None, '', 'nan') else None
        except Exception:
            return None

    if 'device_price' in df.columns:
        df['device_price'] = df['device_price'].apply(to_float)

    # 导入数据
    now = datetime.now()
    records = df.to_dict(orient='records')
    objs = []
    for r in records:
        r['created_at'] = now
        r['updated_at'] = now
        # 将 NaN 转为 None，避免数据库类型错误
        for k, v in r.items():
            if isinstance(v, float) and math.isnan(v):
                r[k] = None
        objs.append(DeviceInventory(**r))

    if objs:
        db.bulk_save_objects(objs)
        db.commit()

    return {"ok": True, "count": len(objs)}


@router.get("/export/data")
def export_devices(
    search: Optional[str] = Query(None, description="搜索关键词"),
    manufacturer: Optional[str] = Query(None, description="厂商筛选"),
    db: Session = Depends(get_db)
):
    """导出设备数据为Excel"""
    query = db.query(DeviceInventory)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                DeviceInventory.manufacturer.ilike(search_pattern),
                DeviceInventory.model_number.ilike(search_pattern),
                DeviceInventory.device_series.ilike(search_pattern),
                DeviceInventory.remarks.ilike(search_pattern)
            )
        )

    if manufacturer:
        query = query.filter(DeviceInventory.manufacturer == manufacturer)

    devices = query.order_by(DeviceInventory.id.desc()).all()

    # 构建数据
    data = []
    for d in devices:
        data.append({
            '厂商': d.manufacturer or '',
            '设备系列': d.device_series or '',
            '设备型号': d.model_number or '',
            '业务场景': d.business_scenario or '',
            '一级分类': d.primary_category or '',
            '二级分类': d.secondary_category or '',
            '三级分类': d.tertiary_category or '',
            '备注': d.remarks or '',
            '整机价格': float(d.device_price) if d.device_price else '',
            '档次': d.device_grade or '',
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='设备库')
    output.seek(0)

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename="devices_export.xlsx"'}
    )


@router.post("/replace-import")
async def replace_import_devices(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """清空表并重新导入设备数据（替换导入）"""
    raw = await file.read()
    bio = io.BytesIO(raw)

    try:
        xls = pd.ExcelFile(bio)
        frames = [xls.parse(sn) for sn in xls.sheet_names]
        df = pd.concat(frames, ignore_index=True)
    except Exception:
        bio.seek(0)
        df = pd.read_excel(bio)

    # 兼容两套列名（脚本旧名 + 现有端点名）
    cn2field = {
        '厂商': 'manufacturer',
        '设备系列': 'device_series',
        '设备型号': 'model_number',
        '业务场景': 'business_scenario',
        '一级分类': 'primary_category',
        '设备一级分类': 'primary_category',
        '二级分类': 'secondary_category',
        '设备二级分类': 'secondary_category',
        '三级分类': 'tertiary_category',
        '设备三级分类': 'tertiary_category',
        '备注': 'remarks',
        '整机价格': 'device_price',
        '档次': 'device_grade',
        '设备档次': 'device_grade',
        '机架高度(U)': 'rack_height_u',
    }

    # 验证必要表头
    required_cn = {'厂商', '设备型号', '整机价格'}
    # 检查原始列名中是否包含必要字段
    actual_columns = set(df.columns.tolist())
    missing = required_cn - actual_columns
    if missing:
        raise HTTPException(status_code=400, detail=f"Excel 缺少必要列: {', '.join(sorted(missing))}")

    # 记录匹配/忽略的列
    matched_columns = [c for c in df.columns if c in cn2field]
    ignored_columns = [c for c in df.columns if c not in cn2field]

    df = df.rename(columns=cn2field)

    keep_fields = [
        'manufacturer', 'device_series', 'model_number', 'business_scenario',
        'primary_category', 'secondary_category', 'tertiary_category',
        'remarks', 'device_price', 'device_grade', 'rack_height_u'
    ]
    df = df[[c for c in keep_fields if c in df.columns]].copy()

    def to_float(x):
        try:
            s = str(x).replace(',', '').replace('¥', '').replace('￥', '').strip()
            return float(s) if s not in (None, '', 'nan') else None
        except Exception:
            return None

    if 'device_price' in df.columns:
        df['device_price'] = df['device_price'].apply(to_float)

    # 清空表
    db.query(DeviceInventory).delete()

    # 导入数据
    now = datetime.now()
    records = df.to_dict(orient='records')
    objs = []
    for r in records:
        r['created_at'] = now
        r['updated_at'] = now
        # 将 NaN 转为 None，避免数据库类型错误
        for k, v in r.items():
            if isinstance(v, float) and math.isnan(v):
                r[k] = None
        objs.append(DeviceInventory(**r))

    if objs:
        db.bulk_save_objects(objs)
    db.commit()

    return {
        "ok": True,
        "count": len(objs),
        "matched_columns": matched_columns,
        "ignored_columns": ignored_columns
    }


@router.delete("/clear")
def clear_devices(db: Session = Depends(get_db)):
    """清空所有设备"""
    db.query(DeviceInventory).delete()
    db.commit()
    return {"ok": True, "message": "设备库已清空"}
