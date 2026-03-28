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
from app.models.device_field_config import DeviceFieldConfig
from app.models.manufacturer import Manufacturer
from app.schemas.device_inventory import DeviceInventoryCreate, DeviceInventoryUpdate, DeviceInventoryOut, DeviceInventoryListResponse

router = APIRouter(prefix="/devices", tags=["设备库管理"])


# ---------- 固定列的中英文映射 ----------

FIXED_CN2FIELD = {
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

FIXED_FIELDS = [
    'manufacturer', 'device_series', 'model_number', 'business_scenario',
    'primary_category', 'secondary_category', 'tertiary_category',
    'remarks', 'device_price', 'device_grade', 'rack_height_u',
]

FIXED_FIELD2CN = {
    'manufacturer': '厂商',
    'device_series': '设备系列',
    'model_number': '设备型号',
    'business_scenario': '业务场景',
    'primary_category': '一级分类',
    'secondary_category': '二级分类',
    'tertiary_category': '三级分类',
    'remarks': '备注',
    'device_price': '整机价格',
    'device_grade': '档次',
}


# ---------- 辅助函数 ----------

def _resolve_manufacturer(db: Session, raw_name: str):
    """通过别名匹配品牌字典，返回 (manufacturer_id, manufacturer_name)。
    未匹配到则自动创建新品牌。
    """
    if not raw_name or not str(raw_name).strip():
        return None, raw_name

    raw_name = str(raw_name).strip()
    raw_lower = raw_name.lower()

    all_manufacturers = db.query(Manufacturer).all()
    for mfr in all_manufacturers:
        if mfr.name.lower() == raw_lower:
            return mfr.id, mfr.name
        for alias in (mfr.aliases or []):
            if str(alias).strip().lower() == raw_lower:
                return mfr.id, mfr.name

    # 未匹配 — 自动创建新品牌（以原始名为标准名，原始名也加入别名）
    now = datetime.now()
    new_mfr = Manufacturer(
        name=raw_name,
        aliases=[raw_name],
        created_at=now,
        updated_at=now,
    )
    db.add(new_mfr)
    db.flush()  # 获取 id，但不提交（由调用方统一 commit）
    return new_mfr.id, new_mfr.name


def _get_field_config_map(db: Session, device_type: Optional[str] = None) -> dict:
    """获取 field_label -> field_key 的映射（用于 Excel 导入时匹配扩展列）"""
    query = db.query(DeviceFieldConfig)
    if device_type:
        query = query.filter(
            (DeviceFieldConfig.device_type == device_type) |
            (DeviceFieldConfig.device_type.is_(None))
        )
    configs = query.all()
    return {c.field_label: c.field_key for c in configs}


def _get_field_configs_for_export(db: Session, device_types: list) -> list:
    """获取导出时需要的扩展字段配置"""
    query = db.query(DeviceFieldConfig).filter(
        (DeviceFieldConfig.device_type.in_(device_types)) |
        (DeviceFieldConfig.device_type.is_(None))
    ).order_by(DeviceFieldConfig.display_order)
    return query.all()


def device_to_dict(device: DeviceInventory) -> dict:
    """将设备对象转换为字典，展开动态字段"""
    result = {
        "id": device.id,
        "manufacturer": device.manufacturer,
        "manufacturer_id": device.manufacturer_id,
        "manufacturer_name": device.manufacturer_name,
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
        "type_attributes": device.type_attributes or {},
        "custom_attributes": device.custom_attributes or {},
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
    }
    return result


def _apply_source_filter(query, source: Optional[str]):
    """根据 source 参数过滤 business_scenario"""
    if source == 'office':
        query = query.filter(DeviceInventory.business_scenario.ilike('%办公%'))
    elif source == 'datacenter':
        query = query.filter(
            or_(
                DeviceInventory.business_scenario.is_(None),
                DeviceInventory.business_scenario == '',
                ~DeviceInventory.business_scenario.ilike('%办公%')
            )
        )
    # hybrid / all / None: 不过滤
    return query


# ---------- CRUD 端点 ----------

@router.get("/", response_model=DeviceInventoryListResponse)
def list_devices(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=200, description="每页记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    manufacturer: Optional[str] = Query(None, description="厂商筛选"),
    device_series: Optional[str] = Query(None, description="设备系列筛选"),
    business_scenario: Optional[str] = Query(None, description="业务场景筛选"),
    device_grade: Optional[str] = Query(None, description="设备档次筛选"),
    source: Optional[str] = Query(None, description="数据源: datacenter/office/all"),
    db: Session = Depends(get_db)
):
    """分页查询设备列表"""
    query = db.query(DeviceInventory)
    query = _apply_source_filter(query, source)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                DeviceInventory.manufacturer.ilike(search_pattern),
                DeviceInventory.manufacturer_name.ilike(search_pattern),
                DeviceInventory.model_number.ilike(search_pattern),
                DeviceInventory.device_series.ilike(search_pattern),
                DeviceInventory.remarks.ilike(search_pattern)
            )
        )

    if manufacturer:
        query = query.filter(
            or_(
                DeviceInventory.manufacturer == manufacturer,
                DeviceInventory.manufacturer_name == manufacturer,
            )
        )

    if device_series:
        query = query.filter(DeviceInventory.device_series.ilike(f"%{device_series}%"))

    if business_scenario:
        query = query.filter(DeviceInventory.business_scenario.ilike(f"%{business_scenario}%"))

    if device_grade:
        query = query.filter(DeviceInventory.device_grade == device_grade)

    total = query.count()
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
    source: Optional[str] = Query(None, description="数据源: datacenter/office/all"),
    db: Session = Depends(get_db)
):
    """获取设备总数"""
    query = db.query(func.count(DeviceInventory.id))
    query = _apply_source_filter(query, source)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                DeviceInventory.manufacturer.ilike(search_pattern),
                DeviceInventory.manufacturer_name.ilike(search_pattern),
                DeviceInventory.model_number.ilike(search_pattern),
                DeviceInventory.device_series.ilike(search_pattern),
                DeviceInventory.remarks.ilike(search_pattern)
            )
        )

    if manufacturer:
        query = query.filter(
            or_(
                DeviceInventory.manufacturer == manufacturer,
                DeviceInventory.manufacturer_name == manufacturer,
            )
        )

    if device_series:
        query = query.filter(DeviceInventory.device_series.ilike(f"%{device_series}%"))

    if business_scenario:
        query = query.filter(DeviceInventory.business_scenario.ilike(f"%{business_scenario}%"))

    if device_grade:
        query = query.filter(DeviceInventory.device_grade == device_grade)

    return {"total": query.scalar()}


@router.get("/manufacturers")
def get_manufacturers(
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """获取所有厂商列表"""
    query = db.query(DeviceInventory.manufacturer_name).distinct()
    query = _apply_source_filter(query, source)
    names = [m[0] for m in query.all() if m[0]]

    # 兼容：也取旧 manufacturer 列
    query2 = db.query(DeviceInventory.manufacturer).distinct()
    query2 = _apply_source_filter(query2, source)
    for m in query2.all():
        if m[0] and m[0] not in names:
            names.append(m[0])

    return sorted(set(names))


@router.get("/device-series")
def get_device_series(
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """获取所有设备系列列表"""
    query = db.query(DeviceInventory.device_series).distinct()
    query = _apply_source_filter(query, source)
    return [s[0] for s in query.all() if s[0]]


@router.get("/business-scenarios")
def get_business_scenarios(
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """获取所有业务场景列表"""
    query = db.query(DeviceInventory.business_scenario).distinct()
    query = _apply_source_filter(query, source)
    return [s[0] for s in query.all() if s[0]]


@router.get("/device-grades")
def get_device_grades(
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """获取所有设备档次列表"""
    query = db.query(DeviceInventory.device_grade).distinct()
    query = _apply_source_filter(query, source)
    return [g[0] for g in query.all() if g[0]]


@router.get("/template/download")
def download_template(
    fmt: str = Query("xlsx", pattern="^(xlsx|csv)$"),
    device_type: Optional[str] = Query(None, description="设备类型，用于加载扩展字段列"),
    db: Session = Depends(get_db),
):
    """下载设备导入模板（支持根据设备类型动态扩展列）"""
    columns = list(FIXED_FIELD2CN.values())

    # 根据 device_type 追加扩展字段列
    if device_type:
        configs = db.query(DeviceFieldConfig).filter(
            (DeviceFieldConfig.device_type == device_type) |
            (DeviceFieldConfig.device_type.is_(None))
        ).order_by(DeviceFieldConfig.display_order).all()
        for c in configs:
            if c.field_label not in columns:
                columns.append(c.field_label)

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
    data = device.model_dump(exclude_unset=True)

    # 品牌字典匹配
    raw_manufacturer = data.pop('manufacturer', None)
    mfr_id, mfr_name = _resolve_manufacturer(db, raw_manufacturer)
    data['manufacturer_id'] = mfr_id
    data['manufacturer_name'] = mfr_name
    data['manufacturer'] = raw_manufacturer  # 保留原始值兼容

    db_device = DeviceInventory(**data)
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

    # 如果更新了品牌名称，重新匹配字典
    if 'manufacturer' in update_data:
        mfr_id, mfr_name = _resolve_manufacturer(db, update_data['manufacturer'])
        update_data['manufacturer_id'] = mfr_id
        update_data['manufacturer_name'] = mfr_name

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


# ---------- 导入 ----------

def _parse_excel(raw: bytes) -> pd.DataFrame:
    """解析 Excel 文件，支持多 sheet 合并"""
    bio = io.BytesIO(raw)
    try:
        xls = pd.ExcelFile(bio)
        frames = [xls.parse(sn) for sn in xls.sheet_names]
        return pd.concat(frames, ignore_index=True)
    except Exception:
        bio.seek(0)
        return pd.read_excel(bio)


def _to_float(x):
    try:
        s = str(x).replace(',', '').replace('¥', '').replace('￥', '').strip()
        return float(s) if s not in (None, '', 'nan') else None
    except Exception:
        return None


def _source_to_scenario(source: Optional[str]) -> Optional[str]:
    """将前端 source 参数转为 business_scenario 值"""
    if source == 'datacenter':
        return '数据中心'
    elif source == 'office':
        return '办公'
    return None


def _build_device_records(df: pd.DataFrame, db: Session, default_scenario: Optional[str] = None) -> list:
    """将 DataFrame 转为 DeviceInventory 对象列表，处理品牌匹配和动态字段"""
    # 1. 分离固定列和扩展列
    all_cn_columns = df.columns.tolist()
    fixed_mapping = {}
    extra_columns = []

    for col in all_cn_columns:
        if col in FIXED_CN2FIELD:
            fixed_mapping[col] = FIXED_CN2FIELD[col]
        else:
            extra_columns.append(col)

    # 2. 获取扩展字段配置（field_label -> field_key）
    all_configs = db.query(DeviceFieldConfig).all()
    label_to_key = {c.field_label: c.field_key for c in all_configs}

    # 3. 重命名固定列
    df_renamed = df.rename(columns=fixed_mapping)

    # 4. 处理价格
    if 'device_price' in df_renamed.columns:
        df_renamed['device_price'] = df_renamed['device_price'].apply(_to_float)

    # 5. 构建品牌缓存（避免每行都查库）
    manufacturer_cache = {}  # raw_name -> (id, name)

    now = datetime.now()
    records = df_renamed.to_dict(orient='records')
    objs = []

    for r in records:
        # NaN 清理
        for k, v in list(r.items()):
            if isinstance(v, float) and math.isnan(v):
                r[k] = None

        # 提取固定字段
        fixed_data = {}
        for field in FIXED_FIELDS:
            if field in r:
                fixed_data[field] = r[field]

        # 品牌字典匹配
        raw_mfr = fixed_data.get('manufacturer')
        if raw_mfr and str(raw_mfr).strip():
            cache_key = str(raw_mfr).strip().lower()
            if cache_key not in manufacturer_cache:
                manufacturer_cache[cache_key] = _resolve_manufacturer(db, raw_mfr)
            mfr_id, mfr_name = manufacturer_cache[cache_key]
        else:
            mfr_id, mfr_name = None, raw_mfr

        fixed_data['manufacturer_id'] = mfr_id
        fixed_data['manufacturer_name'] = mfr_name

        # 提取扩展字段
        type_attrs = {}
        custom_attrs = {}
        for col in extra_columns:
            val = r.get(col)
            if val is None:
                continue
            if isinstance(val, float) and math.isnan(val):
                continue
            if col in label_to_key:
                type_attrs[label_to_key[col]] = val
            else:
                # 未配置的列存入 custom_attributes
                custom_attrs[col] = val

        fixed_data['type_attributes'] = type_attrs if type_attrs else {}
        fixed_data['custom_attributes'] = custom_attrs if custom_attrs else {}

        # 如果 Excel 中没有 business_scenario，使用前端传入的默认值
        if not fixed_data.get('business_scenario') and default_scenario:
            fixed_data['business_scenario'] = default_scenario

        fixed_data['created_at'] = now
        fixed_data['updated_at'] = now

        objs.append(DeviceInventory(**fixed_data))

    return objs


@router.post("/import")
async def import_devices(
    file: UploadFile = File(...),
    source: Optional[str] = Query(None, description="数据源: datacenter/office，用于设置默认业务场景"),
    db: Session = Depends(get_db),
):
    """批量导入设备（追加模式）"""
    raw = await file.read()
    df = _parse_excel(raw)
    objs = _build_device_records(df, db, default_scenario=_source_to_scenario(source))

    if objs:
        db.bulk_save_objects(objs)
        db.commit()

    return {"ok": True, "count": len(objs)}


@router.post("/replace-import")
async def replace_import_devices(
    file: UploadFile = File(...),
    source: Optional[str] = Query(None, description="数据源: datacenter/office，为空则清空全部"),
    db: Session = Depends(get_db),
):
    """替换导入：清空指定数据源后重新导入"""
    raw = await file.read()
    df = _parse_excel(raw)

    # 验证必要表头
    required_cn = {'厂商', '设备型号', '整机价格'}
    actual_columns = set(df.columns.tolist())
    missing = required_cn - actual_columns
    if missing:
        raise HTTPException(status_code=400, detail=f"Excel 缺少必要列: {', '.join(sorted(missing))}")

    matched_columns = [c for c in df.columns if c in FIXED_CN2FIELD]
    ignored_columns = [c for c in df.columns if c not in FIXED_CN2FIELD]

    # 清空对应数据源
    delete_query = db.query(DeviceInventory)
    if source:
        delete_query = _apply_source_filter(delete_query, source)
    delete_query.delete(synchronize_session=False)

    objs = _build_device_records(df, db, default_scenario=_source_to_scenario(source))

    if objs:
        db.bulk_save_objects(objs)
    db.commit()

    return {
        "ok": True,
        "count": len(objs),
        "matched_columns": matched_columns,
        "ignored_columns": ignored_columns
    }


# ---------- 导出 ----------

@router.get("/export/data")
def export_devices(
    search: Optional[str] = Query(None, description="搜索关键词"),
    manufacturer: Optional[str] = Query(None, description="厂商筛选"),
    source: Optional[str] = Query(None, description="数据源: datacenter/office/all"),
    db: Session = Depends(get_db)
):
    """导出设备数据为Excel（固定列 + 动态扩展列）"""
    query = db.query(DeviceInventory)
    query = _apply_source_filter(query, source)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                DeviceInventory.manufacturer.ilike(search_pattern),
                DeviceInventory.manufacturer_name.ilike(search_pattern),
                DeviceInventory.model_number.ilike(search_pattern),
                DeviceInventory.device_series.ilike(search_pattern),
                DeviceInventory.remarks.ilike(search_pattern)
            )
        )

    if manufacturer:
        query = query.filter(
            or_(
                DeviceInventory.manufacturer == manufacturer,
                DeviceInventory.manufacturer_name == manufacturer,
            )
        )

    devices = query.order_by(DeviceInventory.id.desc()).all()

    # 收集所有出现的 type_attributes 和 custom_attributes 键
    all_type_keys = set()
    all_custom_keys = set()
    for d in devices:
        if d.type_attributes:
            all_type_keys.update(d.type_attributes.keys())
        if d.custom_attributes:
            all_custom_keys.update(d.custom_attributes.keys())

    # 获取 field_key -> field_label 映射
    all_configs = db.query(DeviceFieldConfig).all()
    key_to_label = {c.field_key: c.field_label for c in all_configs}

    # 构建数据行
    data = []
    for d in devices:
        row = {
            '厂商': d.manufacturer_name or d.manufacturer or '',
            '设备系列': d.device_series or '',
            '设备型号': d.model_number or '',
            '业务场景': d.business_scenario or '',
            '一级分类': d.primary_category or '',
            '二级分类': d.secondary_category or '',
            '三级分类': d.tertiary_category or '',
            '备注': d.remarks or '',
            '整机价格': float(d.device_price) if d.device_price else '',
            '档次': d.device_grade or '',
        }

        # 展开 type_attributes
        for key in sorted(all_type_keys):
            label = key_to_label.get(key, key)
            row[label] = (d.type_attributes or {}).get(key, '')

        # 展开 custom_attributes
        for key in sorted(all_custom_keys):
            col_name = f"[自定义]{key}" if key in all_type_keys else key
            row[col_name] = (d.custom_attributes or {}).get(key, '')

        data.append(row)

    df = pd.DataFrame(data)

    output = io.BytesIO()
    sheet_name = '设备库'
    if source == 'office':
        sheet_name = '办公设备库'
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename="devices_export.xlsx"'}
    )


@router.delete("/clear")
def clear_devices(
    source: Optional[str] = Query(None, description="数据源: datacenter/office，为空则清空全部"),
    db: Session = Depends(get_db),
):
    """清空设备"""
    query = db.query(DeviceInventory)
    if source:
        query = _apply_source_filter(query, source)
    query.delete(synchronize_session=False)
    db.commit()
    return {"ok": True, "message": "设备库已清空"}
