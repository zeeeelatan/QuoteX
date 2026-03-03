from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models import DeviceInventory, MaintenanceRate
from app.models.office_device_inventory import OfficeDeviceInventory
from app.models.manual_matching_override import ManualMatchingOverride
from typing import Optional, Tuple, Dict, Any
import re

def normalize_manufacturer(manufacturer: str) -> str:
    manufacturer = str(manufacturer).lower()
    manufacturer_aliases = {
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
    if manufacturer in manufacturer_aliases:
        return manufacturer_aliases[manufacturer]
    for alias, standard in manufacturer_aliases.items():
        if alias in manufacturer or manufacturer in alias:
            return standard
    return manufacturer

def normalize_model(model: str) -> str:
    """标准化型号字符串，移除多余的空格和特殊字符"""
    model = str(model).strip()
    # 将多个空格替换为单个空格
    model = re.sub(r'\s+', ' ', model)
    # 移除型号中的特殊字符，但保留 - _ /
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
    # 匹配常见的型号前缀模式
    # 1. 字母+横杠+数字 (AF-2000 -> AF)
    match = re.match(r'^([A-Z]+)[-_]?\d', model)
    if match:
        return match.group(1)
    # 2. 纯字母开头的单词 (PowerEdge R740 -> POWEREDGE)
    match = re.match(r'^([A-Z]+)', model)
    if match:
        return match.group(1)
    return ''


def extract_version(model: str) -> str:
    """提取版本号（如 AF-2000 V8.0 -> V8.0）"""
    model = str(model).strip().upper()
    # 匹配版本号模式 V数字.数字
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
    
    # 基础相似度（SequenceMatcher）
    base_score = SequenceMatcher(None, input_model, db_model).ratio() * 100
    
    # 1. 最长公共子串奖励（最重要的指标）
    lcs_len = longest_common_substring(input_model, db_model)
    max_len = max(len(input_model), len(db_model))
    lcs_ratio = lcs_len / max_len if max_len > 0 else 0
    lcs_bonus = lcs_ratio * 30  # 最多 30 分奖励
    
    # 2. 型号前缀匹配奖励
    input_prefix = extract_model_prefix(input_model)
    db_prefix = extract_model_prefix(db_model)
    prefix_bonus = 0
    if input_prefix and db_prefix:
        if input_prefix == db_prefix:
            prefix_bonus = 25  # 完全匹配奖励 25 分
        elif input_prefix in db_prefix or db_prefix in input_prefix:
            prefix_bonus = 15  # 部分匹配奖励 15 分
    
    # 3. 版本号匹配奖励
    input_version = extract_version(input_model)
    db_version = extract_version(db_model)
    version_bonus = 0
    if input_version and db_version:
        if input_version == db_version:
            version_bonus = 15  # 版本完全匹配奖励 15 分
        elif input_version[0:2] == db_version[0:2]:  # V8 == V8
            version_bonus = 8  # 主版本匹配奖励 8 分
    
    # 4. 厂商匹配奖励
    manufacturer_bonus = 0
    if input_manufacturer and db_manufacturer:
        input_mfr = str(input_manufacturer).strip().upper()
        db_mfr = str(db_manufacturer).strip().upper()
        if input_mfr in db_mfr or db_mfr in input_mfr:
            manufacturer_bonus = 10  # 厂商匹配奖励 10 分
    
    # 综合得分（基础 40% + 奖励）
    final_score = base_score * 0.4 + lcs_bonus + prefix_bonus + version_bonus + manufacturer_bonus
    
    # 确保分数在 0-100 范围内
    return min(100.0, max(0.0, final_score))

def get_maintenance_rate(db: Session, device: DeviceInventory) -> float:
    """
    获取设备的维保费率
    按照三级分类 -> 二级分类 -> 一级分类的顺序查找
    如果都没有找到，返回默认费率0.02
    """
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
    # 三级分类查找
    if primary_category and secondary_category and tertiary_category:
        rate = db.query(MaintenanceRate).filter_by(
            primary_category=primary_category,
            secondary_category=secondary_category,
            tertiary_category=tertiary_category
        ).first()
        if rate:
            return float(rate.rate)

    # 二级分类查找（tertiary_category=None）
    if primary_category and secondary_category:
        rate = db.query(MaintenanceRate).filter_by(
            primary_category=primary_category,
            secondary_category=secondary_category,
            tertiary_category=None
        ).first()
        if rate:
            return float(rate.rate)

    # 一级分类查找（secondary_category=None, tertiary_category=None）
    if primary_category:
        rate = db.query(MaintenanceRate).filter_by(
            primary_category=primary_category,
            secondary_category=None,
            tertiary_category=None
        ).first()
        if rate:
            return float(rate.rate)

    # 默认费率
    return 0.02

def calculate_maintenance_price(device_price: float, rate: float) -> float:
    """计算维保单价：整机价格 * 费率 * 1.06"""
    if not device_price:
        return 0.0
    return float(device_price) * rate * 1.06

def match_device(db: Session, manufacturer: str, model: str, category: Optional[str] = None, source: str = 'datacenter') -> Dict[str, Any]:
    """
    匹配设备，返回匹配结果字典
    匹配策略（优先级从高到低）：
    0. 手动匹配覆盖：查询 manual_matching_override 表
    1. 精确匹配：型号完全相同
    2. 前缀匹配：搜索型号是目标型号的前缀
    3. 模糊匹配：使用相似度算法
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

    normalized_manufacturer = normalize_manufacturer(manufacturer)
    normalized_model = normalize_model(model)

    # ============ 优先级0: 检查手动匹配覆盖表 ============
    # 匹配规则：
    # 前端"原始品牌型号"是"厂商-型号"拼接，我们用 manufacturer 和 model 组合值
    # 去匹配手动匹配库中的 original_manufacturer 和 original_model 组合值
    # 匹配时去掉分隔符进行规范化比较
    
    def normalize_for_manual_match(s: str) -> str:
        """规范化字符串用于手动匹配比较：去掉分隔符、空格，统一转大写"""
        if not s:
            return ''
        # 去掉常见分隔符：空格、横杠、斜杠、下划线
        normalized = re.sub(r'[\s\-_/]+', '', str(s).strip())
        return normalized.upper()
    
    # 构建输入的规范化形式（厂商+型号组合）
    input_manufacturer_normalized = normalize_for_manual_match(manufacturer)
    input_model_normalized = normalize_for_manual_match(model)
    input_combined_normalized = normalize_for_manual_match(f"{manufacturer}{model}")
    
    # 查询手动匹配库中所有符合 data_source 的已确认记录
    manual_overrides = db.query(ManualMatchingOverride).filter(
        ManualMatchingOverride.data_source == source,
        ManualMatchingOverride.is_confirmed == True  # 只匹配已确认的记录
    ).all()
    
    manual_override = None
    for override in manual_overrides:
        # 规范化数据库中的原始厂商和原始型号
        db_original_manufacturer_normalized = normalize_for_manual_match(override.original_manufacturer or '')
        db_original_model_normalized = normalize_for_manual_match(override.original_model)
        db_combined_normalized = normalize_for_manual_match(
            f"{override.original_manufacturer or ''}{override.original_model}"
        )
        
        # 匹配规则（按优先级）：
        # 1. 精确匹配：输入的(厂商+型号)组合 == 数据库的(原始厂商+原始型号)组合
        # 2. 厂商和型号分别匹配
        # 3. 输入的型号 == 数据库的原始型号（兼容旧数据）
        if (input_combined_normalized == db_combined_normalized or
            (input_manufacturer_normalized == db_original_manufacturer_normalized and 
             input_model_normalized == db_original_model_normalized) or
            input_model_normalized == db_original_model_normalized):
            manual_override = override
            break

    if manual_override:
        # 找到手动匹配覆盖记录，直接返回
        rate = get_maintenance_rate_for_category(
            db,
            manual_override.primary_category,
            manual_override.secondary_category,
            manual_override.tertiary_category
        )
        price = calculate_maintenance_price(manual_override.device_price or 0, rate)

        return {
            "matched_model": manual_override.matched_model_number,
            "match_rate": 100.0,  # 手动匹配视为100%匹配
            "price": price,
            "device_price": float(manual_override.device_price) if manual_override.device_price else None,
            "rate": rate,
            "device_category": manual_override.device_category or manual_override.tertiary_category or "",
            "primary_category": manual_override.primary_category,
            "secondary_category": manual_override.secondary_category,
            "tertiary_category": manual_override.tertiary_category,
            "manufacturer": manual_override.matched_manufacturer,  # 返回匹配后厂商
            "device_series": None,  # 手动匹配库暂无此字段
            "is_manual_override": True  # 标记为手动覆盖
        }

    # ============ 以下为原有的自动匹配逻辑 ============
    
    def load_from_table(table_cls):
        query = db.query(table_cls)
        if category:
            data = query.filter(table_cls.primary_category == category).all()
            if data:
                return data
        return query.all()

    if source == 'datacenter':
        devices = load_from_table(DeviceInventory)
    elif source == 'office':
        devices = load_from_table(OfficeDeviceInventory)
    else:  # hybrid
        devices = load_from_table(DeviceInventory) + load_from_table(OfficeDeviceInventory)
        
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

    # 1. 精确匹配
    for device in devices:
        device_model = normalize_model(device.model_number)
        if device_model == normalized_model:
            manufacturer_score = similarity_ratio(normalized_manufacturer, device.manufacturer)
            if manufacturer_score > 80:  # 厂商相似度要求降低，因为已经是精确型号匹配
                rate = get_maintenance_rate(db, device)
                price = calculate_maintenance_price(device.device_price, rate)
                return {
                    "matched_model": device.model_number,
                    "match_rate": 100.0,
                    "price": price,
                    "device_price": float(device.device_price) if device.device_price else None,
                    "rate": rate,
                    "device_category": device.tertiary_category or "",
                    "primary_category": device.primary_category,
                    "secondary_category": device.secondary_category,
                    "tertiary_category": device.tertiary_category,
                    "manufacturer": device.manufacturer,
                    "device_series": device.device_series
                }

    # 2. 前缀匹配
    prefix_matches = []
    for device in devices:
        device_model = normalize_model(device.model_number)
        if normalized_model in device_model or device_model in normalized_model:
            manufacturer_score = similarity_ratio(normalized_manufacturer, device.manufacturer)
            if manufacturer_score > 85:  # 厂商相似度要求提高，因为是前缀匹配
                model_score = 90.0  # 前缀匹配给予较高的基础分
                prefix_matches.append((device, model_score))

    if prefix_matches:
        # 选择最佳前缀匹配
        best_prefix_match = max(prefix_matches, key=lambda x: x[1])
        device = best_prefix_match[0]
        rate = get_maintenance_rate(db, device)
        price = calculate_maintenance_price(device.device_price, rate)
        return {
            "matched_model": device.model_number,
            "match_rate": best_prefix_match[1],
            "price": price,
            "device_price": float(device.device_price) if device.device_price else None,
            "rate": rate,
            "device_category": device.tertiary_category or "",
            "primary_category": device.primary_category,
            "secondary_category": device.secondary_category,
            "tertiary_category": device.tertiary_category,
            "manufacturer": device.manufacturer,
            "device_series": device.device_series
        }

    # 3. 模糊匹配（使用优化的设备型号匹配算法）
    best_match = None
    best_score = 0.0
    best_price = 0.0
    best_rate = 0.0
    best_device_price = None
    best_category = ""
    best_device = None
    best_primary_category = None
    best_secondary_category = None
    best_tertiary_category = None

    for device in devices:
        # 使用优化的型号相似度算法（考虑最长公共子串、前缀匹配、版本号匹配）
        model_score = model_similarity_score(
            normalized_model, 
            normalize_model(device.model_number),
            normalized_manufacturer,
            device.manufacturer
        )

        if model_score > best_score:
            best_score = model_score
            best_match = device.model_number
            best_category = device.tertiary_category or ""
            best_device = device
            best_primary_category = device.primary_category
            best_secondary_category = device.secondary_category
            best_tertiary_category = device.tertiary_category

    # 只返回相似度超过阈值的结果
    if best_score > 50 and best_device:  # 阈值调整为 50，因为新算法分数分布不同
        best_rate = get_maintenance_rate(db, best_device)
        best_price = calculate_maintenance_price(best_device.device_price, best_rate)
        best_device_price = float(best_device.device_price) if best_device.device_price else None
        return {
            "matched_model": best_match,
            "match_rate": best_score,
            "price": best_price,
            "device_price": best_device_price,
            "rate": best_rate,
            "device_category": best_category,
            "primary_category": best_primary_category,
            "secondary_category": best_secondary_category,
            "tertiary_category": best_tertiary_category,
            "manufacturer": best_device.manufacturer,
            "device_series": best_device.device_series
        }

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
