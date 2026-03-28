from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models import DeviceInventory, MaintenanceRate
from app.models.manufacturer import Manufacturer
from app.models.manual_matching_override import ManualMatchingOverride
from typing import Optional, Tuple, Dict, Any
import re


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

    # 1. 尝试从字典表查找
    if db is not None:
        try:
            all_manufacturers = db.query(Manufacturer).all()
            for mfr in all_manufacturers:
                # 标准名匹配
                if mfr.name.lower() == manufacturer_lower:
                    return mfr.name
                # 别名匹配
                for alias in (mfr.aliases or []):
                    if str(alias).strip().lower() == manufacturer_lower:
                        return mfr.name
                    # 部分包含匹配
                    if str(alias).strip().lower() in manufacturer_lower or manufacturer_lower in str(alias).strip().lower():
                        return mfr.name
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


def match_device(db: Session, manufacturer: str, model: str, category: Optional[str] = None, source: str = 'datacenter') -> Dict[str, Any]:
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

    manual_overrides = db.query(ManualMatchingOverride).filter(
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
        query = db.query(DeviceInventory)
        # 通过 business_scenario 过滤数据源
        if source == 'datacenter':
            # 非办公场景的设备（兼容旧数据：business_scenario 为空也视为数据中心）
            query = query.filter(
                or_(
                    DeviceInventory.business_scenario.is_(None),
                    DeviceInventory.business_scenario == '',
                    ~DeviceInventory.business_scenario.ilike('%办公%')
                )
            )
        elif source == 'office':
            query = query.filter(DeviceInventory.business_scenario.ilike('%办公%'))
        # hybrid: 不加过滤，查全量

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

    # 1. 精确匹配
    for device in devices:
        device_model = normalize_model(device.model_number)
        if device_model == normalized_model:
            mfr = _get_device_manufacturer(device)
            manufacturer_score = similarity_ratio(normalized_manufacturer, mfr)
            if manufacturer_score > 80:
                return _build_result(device, 100.0)

    # 2. 前缀匹配
    prefix_matches = []
    for device in devices:
        device_model = normalize_model(device.model_number)
        if normalized_model in device_model or device_model in normalized_model:
            mfr = _get_device_manufacturer(device)
            manufacturer_score = similarity_ratio(normalized_manufacturer, mfr)
            if manufacturer_score > 85:
                prefix_matches.append((device, 90.0))

    if prefix_matches:
        best_prefix_match = max(prefix_matches, key=lambda x: x[1])
        device = best_prefix_match[0]
        return _build_result(device, best_prefix_match[1])

    # 3. 模糊匹配
    best_score = 0.0
    best_device = None

    for device in devices:
        mfr = _get_device_manufacturer(device)
        model_score = model_similarity_score(
            normalized_model,
            normalize_model(device.model_number),
            normalized_manufacturer,
            mfr
        )
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
