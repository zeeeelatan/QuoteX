from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models import DeviceInventory, MaintenanceRate
from app.models.manufacturer import Manufacturer
from app.models.manual_matching_override import ManualMatchingOverride
from typing import Optional, Tuple, Dict, Any, List
import os
import re
import time


# 模糊召回候选数（pg_trgm KNN top-K）。可用环境变量覆盖。
TRIGRAM_RECALL_K = int(os.getenv("TRIGRAM_RECALL_K", "50"))
# 召回开关，默认开启；trgm 不可用时单次失败会自动退回全量匹配。
def _trigram_recall_enabled() -> bool:
    return os.getenv("ENABLE_TRIGRAM_RECALL", "1").strip() not in ("0", "false", "False", "")


# ---------- 品牌字典表进程级缓存（TTL，避免每次匹配全表查询） ----------

_MFR_CACHE: Dict[str, Any] = {"data": None, "ts": 0.0}
_MFR_CACHE_TTL = 60.0  # 秒


def _get_cached_manufacturers(db: Session) -> List[Tuple[str, list]]:
    """返回 [(name, aliases), ...]，带 60s TTL 缓存。品牌表极少变动。"""
    now = time.time()
    if _MFR_CACHE["data"] is None or (now - _MFR_CACHE["ts"]) > _MFR_CACHE_TTL:
        rows = db.query(Manufacturer.name, Manufacturer.aliases).all()
        _MFR_CACHE["data"] = [(n, list(a or [])) for n, a in rows]
        _MFR_CACHE["ts"] = now
    return _MFR_CACHE["data"]


def invalidate_manufacturer_cache() -> None:
    """品牌表增删改后调用，强制下次匹配刷新缓存。"""
    _MFR_CACHE["data"] = None
    _MFR_CACHE["ts"] = 0.0


# ---------- 品牌标准化（查字典表 + 硬编码兜底） ----------

# 硬编码别名作为兜底（字典表为空或未命中时使用）
_FALLBACK_ALIASES = {
    'hp': '惠普&慧与/HP&HPE',
    'hpe': '惠普&慧与/HP&HPE',
    'huawei': '华为/HUAWEI',
    'h3c': '新华三/H3C',
    'dell': '戴尔/DELL',
    'ibm': 'IBM',
    'lenovo': '联想/LENOVO',
    'inspur': '浪潮/INSPUR',
    'cisco': '思科/CISCO',
    'fujitsu': '富士通/FUJITSU',
    'hitachi': '日立/HITACHI',
    'emc': 'EMC',
    'netapp': 'NetApp',
    'oracle': 'Oracle',
    'vmware': 'VMware',
    'microsoft': 'Microsoft',
    'red hat': 'Red Hat',
    'suse': 'SUSE',
    'sangfor': '深信服/SANGFOR',
    'ewp': '新华三/H3C',
}


def normalize_manufacturer(manufacturer: str, db: Optional[Session] = None) -> str:
    """标准化品牌名称。
    优先查询品牌字典表的 aliases，未命中则退回硬编码映射。
    """
    manufacturer = str(manufacturer).strip()
    manufacturer_lower = manufacturer.lower()

    # 1. 尝试从字典表查找（带 TTL 缓存）
    if db is not None:
        try:
            for name, aliases in _get_cached_manufacturers(db):
                # 标准名匹配
                if name.lower() == manufacturer_lower:
                    return name
                # 别名匹配
                for alias in (aliases or []):
                    if str(alias).strip().lower() == manufacturer_lower:
                        return name
                    # 部分包含匹配
                    if str(alias).strip().lower() in manufacturer_lower or manufacturer_lower in str(alias).strip().lower():
                        return name
        except Exception:
            pass  # 字典表不可用时退回兜底

    # 2. 硬编码兜底
    if manufacturer_lower in _FALLBACK_ALIASES:
        return _FALLBACK_ALIASES[manufacturer_lower]
    for alias, standard in _FALLBACK_ALIASES.items():
        if alias in manufacturer_lower or manufacturer_lower in alias:
            return standard

    return manufacturer


def normalize_model(model: str) -> str:
    """标准化型号字符串，移除多余的空格和特殊字符"""
    model = str(model).strip()
    model = re.sub(r'\s+', ' ', model)
    model = re.sub(r'[^\w\s\-_/]', '', model)
    return model.upper()


def similarity_ratio(a: str, b: str) -> float:
    """计算两个字符串的相似度"""
    if not a or not b:
        return 0.0
    a = str(a).strip().upper()
    b = str(b).strip().upper()
    return SequenceMatcher(None, a, b).ratio() * 100


def longest_common_substring(a: str, b: str) -> int:
    """计算最长公共子串长度"""
    if not a or not b:
        return 0
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_len = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                max_len = max(max_len, dp[i][j])
    return max_len


def extract_model_prefix(model: str) -> str:
    """提取型号前缀（如 AF-2000 -> AF, PowerEdge R740 -> POWEREDGE）"""
    model = str(model).strip().upper()
    match = re.match(r'^([A-Z]+)[-_]?\d', model)
    if match:
        return match.group(1)
    match = re.match(r'^([A-Z]+)', model)
    if match:
        return match.group(1)
    return ''


def extract_version(model: str) -> str:
    """提取版本号（如 AF-2000 V8.0 -> V8.0）"""
    model = str(model).strip().upper()
    match = re.search(r'(V\d+\.?\d*)', model)
    if match:
        return match.group(1)
    return ''


def model_similarity_score(input_model: str, db_model: str, input_manufacturer: str = '', db_manufacturer: str = '') -> float:
    """
    计算设备型号的相似度得分（专为设备型号优化）
    综合考虑：
    1. 最长公共子串长度
    2. 型号前缀匹配
    3. 版本号匹配
    4. 整体相似度
    """
    if not input_model or not db_model:
        return 0.0

    input_model = str(input_model).strip().upper()
    db_model = str(db_model).strip().upper()

    base_score = SequenceMatcher(None, input_model, db_model).ratio() * 100

    lcs_len = longest_common_substring(input_model, db_model)
    max_len = max(len(input_model), len(db_model))
    lcs_ratio = lcs_len / max_len if max_len > 0 else 0
    lcs_bonus = lcs_ratio * 30

    input_prefix = extract_model_prefix(input_model)
    db_prefix = extract_model_prefix(db_model)
    prefix_bonus = 0
    if input_prefix and db_prefix:
        if input_prefix == db_prefix:
            prefix_bonus = 25
        elif input_prefix in db_prefix or db_prefix in input_prefix:
            prefix_bonus = 15

    input_version = extract_version(input_model)
    db_version = extract_version(db_model)
    version_bonus = 0
    if input_version and db_version:
        if input_version == db_version:
            version_bonus = 15
        elif input_version[0:2] == db_version[0:2]:
            version_bonus = 8

    manufacturer_bonus = 0
    if input_manufacturer and db_manufacturer:
        input_mfr = str(input_manufacturer).strip().upper()
        db_mfr = str(db_manufacturer).strip().upper()
        if input_mfr in db_mfr or db_mfr in input_mfr:
            manufacturer_bonus = 10

    final_score = base_score * 0.4 + lcs_bonus + prefix_bonus + version_bonus + manufacturer_bonus
    return min(100.0, max(0.0, final_score))


def get_maintenance_rate(db: Session, device: DeviceInventory) -> float:
    """获取设备的维保费率"""
    return get_maintenance_rate_for_category(
        db,
        device.primary_category,
        device.secondary_category,
        device.tertiary_category
    )


def get_maintenance_rate_for_category(
    db: Session,
    primary_category: Optional[str],
    secondary_category: Optional[str],
    tertiary_category: Optional[str]
) -> float:
    """
    根据分类获取维保费率
    按照三级分类 -> 二级分类 -> 一级分类的顺序查找
    如果都没有找到，返回默认费率0.02
    """
    if primary_category and secondary_category and tertiary_category:
        rate = db.query(MaintenanceRate).filter_by(
            primary_category=primary_category,
            secondary_category=secondary_category,
            tertiary_category=tertiary_category
        ).first()
        if rate:
            return float(rate.rate)

    if primary_category and secondary_category:
        rate = db.query(MaintenanceRate).filter_by(
            primary_category=primary_category,
            secondary_category=secondary_category,
            tertiary_category=None
        ).first()
        if rate:
            return float(rate.rate)

    if primary_category:
        rate = db.query(MaintenanceRate).filter_by(
            primary_category=primary_category,
            secondary_category=None,
            tertiary_category=None
        ).first()
        if rate:
            return float(rate.rate)

    return 0.02


def calculate_maintenance_price(device_price: float, rate: float) -> float:
    """计算维保单价：整机价格 * 费率 * 1.06"""
    if not device_price:
        return 0.0
    return float(device_price) * rate * 1.06


def _get_device_manufacturer(device) -> str:
    """获取设备的品牌名称，兼容新旧字段"""
    return device.manufacturer_name or device.manufacturer or ''


def _apply_source_filter(query, source: str):
    """按数据源（business_scenario）过滤设备查询。"""
    if source == 'datacenter':
        # 非办公场景（兼容旧数据：business_scenario 为空也视为数据中心）
        return query.filter(
            or_(
                DeviceInventory.business_scenario.is_(None),
                DeviceInventory.business_scenario == '',
                ~DeviceInventory.business_scenario.ilike('%办公%')
            )
        )
    if source == 'office':
        return query.filter(DeviceInventory.business_scenario.ilike('%办公%'))
    # hybrid: 不加过滤
    return query


def _recall_candidates(
    db: Session,
    queries: List[str],
    source: str,
    category: Optional[str],
    k: int = TRIGRAM_RECALL_K,
) -> Optional[list]:
    """用 pg_trgm GiST 索引做 KNN 近邻召回，返回 top-K 候选设备对象。

    把模糊匹配的候选集从全表 9.5 万行缩小到 top-K（默认 50），单次匹配
    从 ~750ms 降到 ~10ms，匹配语义不变（仍由现有三级逻辑在候选集上精排）。

    返回 None 表示召回不可用（pg_trgm 未装等），调用方应退回全量加载。
    """
    queries = [q for q in (queries or []) if q and q.strip()]
    if not queries or not _trigram_recall_enabled():
        return None
    try:
        seen, ids = set(), []
        for q in queries:
            sub = _apply_source_filter(db.query(DeviceInventory.id), source)
            if category:
                sub = sub.filter(DeviceInventory.primary_category == category)
            # KNN: lower(model_number) <-> lower(:q)，命中 lower() 表达式 GiST 索引
            dist = func.lower(DeviceInventory.model_number).op('<->')(func.lower(q))
            for (i,) in sub.order_by(dist).limit(k).all():
                if i not in seen:
                    seen.add(i)
                    ids.append(i)
        # category 过滤后召回为空 → 放宽不带 category 再召回（与原全量逻辑一致）
        if not ids and category:
            return _recall_candidates(db, queries, source, None, k)
        if not ids:
            return []
        return db.query(DeviceInventory).filter(DeviceInventory.id.in_(ids)).all()
    except Exception:
        return None  # 召回不可用，退回全量匹配


def match_device(db: Session, manufacturer: str, model: str, category: Optional[str] = None, source: str = 'datacenter', _skip_manual_override: bool = False) -> Dict[str, Any]:
    """
    匹配设备，返回匹配结果字典
    匹配策略（优先级从高到低）：
    0. 手动匹配覆盖：查询 manual_matching_override 表
    1. 精确匹配：型号完全相同
    2. 前缀匹配：搜索型号是目标型号的前缀
    3. 模糊匹配：使用相似度算法

    source 参数通过 business_scenario 过滤：
    - 'datacenter': 数据中心场景设备
    - 'office': 办公场景设备
    - 'hybrid': 所有设备
    """
    if not model:
        return {
            "matched_model": None,
            "match_rate": 0.0,
            "price": 0.0,
            "device_price": None,
            "rate": None,
            "device_category": "",
            "primary_category": None,
            "secondary_category": None,
            "tertiary_category": None,
            "manufacturer": None,
            "device_series": None
        }

    normalized_manufacturer = normalize_manufacturer(manufacturer, db=db)
    normalized_model = normalize_model(model)

    # ============ 语义抽取层（灰度开关，异常自动退回原逻辑）============
    # 把原始型号拆成 品牌/设备类型/型号核心串，后续自动匹配用「核心串」算相似度，
    # 避免设备类型词、品牌词、配置参数稀释型号相似度。手动覆盖逻辑不受影响。
    semantic_fields = None
    semantic_model = normalized_model  # 默认退回整串
    semantic_model_alt = ""            # 含系列名的弱信号核心串（匹配兜底）
    try:
        from app.semantic import extract_fields, is_semantic_enabled
        if is_semantic_enabled():
            semantic_fields = extract_fields(
                model, manufacturer, db=db, normalize_manufacturer=normalize_manufacturer
            )
            if semantic_fields.core:
                semantic_model = normalize_model(semantic_fields.core)
            if semantic_fields.core_with_series:
                alt = normalize_model(semantic_fields.core_with_series)
                if alt and alt != semantic_model:
                    semantic_model_alt = alt
            # 入参品牌为空时，用从型号中抽取/反推的品牌补全品牌校验维度
            if (not manufacturer or not str(manufacturer).strip()) and semantic_fields.brand:
                normalized_manufacturer = semantic_fields.brand
    except Exception:
        semantic_fields = None
        semantic_model = normalized_model
        semantic_model_alt = ""

    # 参与匹配的候选型号串：默认核心串 +（可选）含系列弱信号串
    candidate_models = [m for m in (semantic_model, semantic_model_alt) if m]

    # ============ 优先级0: 检查手动匹配覆盖表 ============
    def normalize_for_manual_match(s: str) -> str:
        """规范化字符串用于手动匹配比较：去掉分隔符、空格，统一转大写"""
        if not s:
            return ''
        normalized = re.sub(r'[\s\-_/]+', '', str(s).strip())
        return normalized.upper()

    input_manufacturer_normalized = normalize_for_manual_match(manufacturer)
    input_model_normalized = normalize_for_manual_match(model)
    input_combined_normalized = normalize_for_manual_match(f"{manufacturer}{model}")

    manual_overrides = [] if _skip_manual_override else db.query(ManualMatchingOverride).filter(
        ManualMatchingOverride.data_source == source,
        ManualMatchingOverride.is_confirmed == True
    ).all()

    manual_override = None
    for override in manual_overrides:
        db_original_manufacturer_normalized = normalize_for_manual_match(override.original_manufacturer or '')
        db_original_model_normalized = normalize_for_manual_match(override.original_model)
        db_combined_normalized = normalize_for_manual_match(
            f"{override.original_manufacturer or ''}{override.original_model}"
        )

        if (input_combined_normalized == db_combined_normalized or
            (input_manufacturer_normalized == db_original_manufacturer_normalized and
             input_model_normalized == db_original_model_normalized) or
            input_model_normalized == db_original_model_normalized):
            manual_override = override
            break

    if manual_override:
        rate = get_maintenance_rate_for_category(
            db,
            manual_override.primary_category,
            manual_override.secondary_category,
            manual_override.tertiary_category
        )
        price = calculate_maintenance_price(manual_override.device_price or 0, rate)

        return {
            "matched_model": manual_override.matched_model_number,
            "match_rate": 100.0,
            "price": price,
            "device_price": float(manual_override.device_price) if manual_override.device_price else None,
            "rate": rate,
            "device_category": manual_override.device_category or manual_override.tertiary_category or "",
            "primary_category": manual_override.primary_category,
            "secondary_category": manual_override.secondary_category,
            "tertiary_category": manual_override.tertiary_category,
            "manufacturer": manual_override.matched_manufacturer,
            "device_series": None,
            "is_manual_override": True
        }

    # ============ 自动匹配逻辑 — 统一查 device_inventory ============

    def load_devices():
        # 优先用 pg_trgm KNN 召回 top-K 候选（候选串 = 型号核心串），
        # 将候选集从全表缩到几十行；召回不可用时返回 None，退回全量加载。
        recalled = _recall_candidates(db, candidate_models, source, category)
        if recalled is not None:
            return recalled

        # —— 退回：全量加载（trgm 不可用时的兜底，保持原行为）——
        query = _apply_source_filter(db.query(DeviceInventory), source)
        if category:
            data = query.filter(DeviceInventory.primary_category == category).all()
            if data:
                return data
            # 无分类匹配时退回全量
            return query.all()
        return query.all()

    devices = load_devices()

    if not devices:
        return {
            "matched_model": None,
            "match_rate": 0.0,
            "price": 0.0,
            "device_price": None,
            "rate": None,
            "device_category": "",
            "primary_category": None,
            "secondary_category": None,
            "tertiary_category": None,
            "manufacturer": None,
            "device_series": None
        }

    def _build_result(device, match_rate):
        rate = get_maintenance_rate(db, device)
        price = calculate_maintenance_price(device.device_price, rate)
        mfr = _get_device_manufacturer(device)
        return {
            "matched_model": device.model_number,
            "match_rate": match_rate,
            "price": price,
            "device_price": float(device.device_price) if device.device_price else None,
            "rate": rate,
            "device_category": device.tertiary_category or "",
            "primary_category": device.primary_category,
            "secondary_category": device.secondary_category,
            "tertiary_category": device.tertiary_category,
            "manufacturer": mfr,
            "device_series": device.device_series
        }

    # 品牌门槛：当完全没有品牌信息时不应卡住型号的精确/前缀命中
    has_brand_info = bool(normalized_manufacturer and normalized_manufacturer.strip())

    def _brand_pass(mfr: str, threshold: float) -> bool:
        if not has_brand_info:
            return True
        return similarity_ratio(normalized_manufacturer, mfr) > threshold

    # 1. 精确匹配（基于型号核心串，逐个候选串尝试）
    for device in devices:
        device_model = normalize_model(device.model_number)
        if device_model and device_model in candidate_models:
            mfr = _get_device_manufacturer(device)
            if _brand_pass(mfr, 80):
                return _build_result(device, 100.0)

    # 2. 前缀匹配（核心串与库内型号互为子串）
    prefix_matches = []
    for device in devices:
        device_model = normalize_model(device.model_number)
        if not device_model:
            continue
        # 任一候选串与库内型号互为子串，且被包含一方≥3字符，避免极短串误命中
        contained = any(
            (cm in device_model and len(cm) >= 3) or
            (device_model in cm and len(device_model) >= 3)
            for cm in candidate_models
        )
        if contained:
            mfr = _get_device_manufacturer(device)
            if _brand_pass(mfr, 85):
                prefix_matches.append((device, 90.0))

    if prefix_matches:
        best_prefix_match = max(prefix_matches, key=lambda x: x[1])
        device = best_prefix_match[0]
        return _build_result(device, best_prefix_match[1])

    # 3. 模糊匹配（基于型号核心串，取各候选串的最高分）
    best_score = 0.0
    best_device = None

    for device in devices:
        mfr = _get_device_manufacturer(device)
        db_model = normalize_model(device.model_number)
        model_score = max(
            model_similarity_score(cm, db_model, normalized_manufacturer, mfr)
            for cm in candidate_models
        ) if candidate_models else 0.0
        if model_score > best_score:
            best_score = model_score
            best_device = device

    if best_score > 50 and best_device:
        return _build_result(best_device, best_score)

    return {
        "matched_model": None,
        "match_rate": 0.0,
        "price": 0.0,
        "device_price": None,
        "rate": None,
        "device_category": "",
        "primary_category": None,
        "secondary_category": None,
        "tertiary_category": None,
        "manufacturer": None,
        "device_series": None
    }
