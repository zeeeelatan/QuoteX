"""联想框架报价相关 Pydantic schema"""
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# ============ 分类 ============

class LenovoClassificationBase(BaseModel):
    device_category: str
    brand: Optional[str] = None
    series: Optional[str] = None
    model: str
    mt_code: Optional[str] = None
    end_type: str
    sub_category: Optional[str] = None
    source_sheet: Optional[str] = None
    notes: Optional[str] = None


class LenovoClassificationCreate(LenovoClassificationBase):
    pass


class LenovoClassificationOut(LenovoClassificationBase):
    id: int

    class Config:
        from_attributes = True


# ============ 统一机型库（lenovo_framework_models） ============

class LenovoFrameworkModelBase(BaseModel):
    device_category: str
    brand: Optional[str] = None
    series: Optional[str] = None
    model: str
    mt_code: Optional[str] = None
    end_type: Optional[str] = None
    sub_category: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    aliases: List[str] = []


class LenovoFrameworkModelCreate(LenovoFrameworkModelBase):
    pass


class LenovoFrameworkModelOut(LenovoFrameworkModelBase):
    id: int
    source_ref_id: Optional[int] = None

    class Config:
        from_attributes = True


class LenovoFrameworkModelsPage(BaseModel):
    total: int
    items: List[LenovoFrameworkModelOut]


# ============ 通配规则 ============

class LenovoPatternRuleBase(BaseModel):
    device_category: str
    brand: str
    pattern_raw: str
    pattern_regex: str
    end_type: str
    priority: int = 100
    notes: Optional[str] = None


class LenovoPatternRuleCreate(LenovoPatternRuleBase):
    pass


class LenovoPatternRuleOut(LenovoPatternRuleBase):
    id: int

    class Config:
        from_attributes = True


# ============ 价格表（每类各一组） ============

class PriceBaseMixin(BaseModel):
    notes: Optional[str] = None


# 磁带库
class LenovoPriceTapeBase(PriceBaseMixin):
    end_type: str
    drive_config: str
    sla: str
    price: Decimal


class LenovoPriceTapeCreate(LenovoPriceTapeBase):
    pass


class LenovoPriceTapeOut(LenovoPriceTapeBase):
    id: int

    class Config:
        from_attributes = True


# 网络
class LenovoPriceNetworkBase(PriceBaseMixin):
    device_category: str
    end_type: str
    sla: str
    price: Decimal


class LenovoPriceNetworkCreate(LenovoPriceNetworkBase):
    pass


class LenovoPriceNetworkOut(LenovoPriceNetworkBase):
    id: int

    class Config:
        from_attributes = True


# 服务器
class LenovoPriceServerBase(PriceBaseMixin):
    end_type: str
    includes_ssd: bool
    package_type: str
    sla: str
    includes_disk: bool
    price: Decimal


class LenovoPriceServerCreate(LenovoPriceServerBase):
    pass


class LenovoPriceServerOut(LenovoPriceServerBase):
    id: int

    class Config:
        from_attributes = True


# 存储
class LenovoPriceStorageBase(PriceBaseMixin):
    end_type: str
    sla: str
    includes_disk_no_return: bool
    price: Decimal


class LenovoPriceStorageCreate(LenovoPriceStorageBase):
    pass


class LenovoPriceStorageOut(LenovoPriceStorageBase):
    id: int

    class Config:
        from_attributes = True


# 小型机
class LenovoPriceMiniBase(PriceBaseMixin):
    end_type: str
    sla: str
    includes_disk: bool
    price: Decimal


class LenovoPriceMiniCreate(LenovoPriceMiniBase):
    pass


class LenovoPriceMiniOut(LenovoPriceMiniBase):
    id: int

    class Config:
        from_attributes = True


# 巡检
class LenovoPriceInspectionBase(PriceBaseMixin):
    unit: str
    price: Decimal
    tax_rate: Decimal = Decimal("0.06")


class LenovoPriceInspectionCreate(LenovoPriceInspectionBase):
    pass


class LenovoPriceInspectionOut(LenovoPriceInspectionBase):
    id: int

    class Config:
        from_attributes = True


# ============ 报价请求/响应 ============

class LenovoQuoteRequest(BaseModel):
    device_category: str = Field(..., description="磁带库/光纤交换机/网络设备/服务器/IB交换机/小型机/存储")
    brand: Optional[str] = None
    model: str
    sla: str
    quantity: int = 1

    # 各大类专属维度（不相关字段留空即可）
    drive_config: Optional[str] = None              # 磁带库 (LTO5/6/7/8)
    sub_category: Optional[str] = None              # 网络设备子类（如果调用方已知道）
    includes_ssd: Optional[bool] = None             # 服务器：含SSD
    package_type: Optional[str] = None              # 服务器：备件维保/整包
    includes_disk: Optional[bool] = None            # 服务器/小型机：含硬盘不返还
    includes_disk_no_return: Optional[bool] = None  # 存储：含硬盘不回收

    # 用户手动锁定端型时使用：跳过自动 _match_end_type，直接按该端型查价
    force_end_type: Optional[str] = None

    # 「原始品牌型号」完整字符串，作为 alias 快查键。命中机型库 aliases 数组即直接返回。
    # 例：用户上传时的 "Dell-PowerEdge R630"
    alias_key: Optional[str] = None


class LenovoQuoteResult(BaseModel):
    status: str                       # ok / unmatched / no_price
    message: Optional[str] = None
    device_category: str
    brand: Optional[str] = None
    model: str
    sla: str
    quantity: int

    end_type: Optional[str] = None
    sub_category: Optional[str] = None
    match_method: Optional[str] = None     # exact / fuzzy / pattern / manual / none
    matched_classification_id: Optional[int] = None
    matched_pattern_id: Optional[int] = None
    # 命中后的具体型号（精确/模糊命中 → cls.model；通配命中 → 通配 raw；不命中 → 输入 model）
    matched_brand: Optional[str] = None
    matched_model: Optional[str] = None
    # 命中机型库后返回的实际 device_category（前端"分类"列可直接显示）
    matched_device_category: Optional[str] = None

    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    price_table_row_id: Optional[int] = None
    price_notes: Optional[str] = None


class LenovoBulkQuoteRequest(BaseModel):
    items: List[LenovoQuoteRequest]


class LenovoBulkQuoteResponse(BaseModel):
    results: List[LenovoQuoteResult]
