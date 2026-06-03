"""联想框架报价相关模型

独立于现有「设备价格 × 费率 × 1.06」逻辑，提供按
(设备大类 × 端型 × SLA × 配置维度) → 单价 的直查口径。

包含三类表：
1. 机型分类（lenovo_classification）：型号 → 端型 / sub_category
2. 通配规则（lenovo_pattern_rule）：Word 兜底规则
3. 价格表（5 张，按设备大类分）+ 巡检价格表
"""
from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class LenovoClassification(Base):
    """机型 → 端型 分类表（由 Excel 数字开头的 sheet 导入）"""
    __tablename__ = "lenovo_classification"

    id = Column(Integer, primary_key=True, index=True)
    device_category = Column(String(32), nullable=False, index=True)
    # 磁带库 / 光纤交换机 / 网络设备 / 服务器 / IB交换机 / 小型机 / 存储

    brand = Column(String(128), nullable=True)
    series = Column(String(255), nullable=True)
    model = Column(String(255), nullable=False, index=True)
    mt_code = Column(String(64), nullable=True)

    end_type = Column(String(32), nullable=False)
    # 低端 / 中端 / 高端 / 超高端 / L1 / L2 / M

    sub_category = Column(String(32), nullable=True)
    # 仅 device_category=网络设备 时使用: 网络交换机/路由器/无线AP/无线控制器

    source_sheet = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_lenovo_classification_lookup", "device_category", "brand", "model"),
    )


class LenovoPatternRule(Base):
    """Word 文档兜底通配规则（仅 服务器 / 存储）"""
    __tablename__ = "lenovo_pattern_rule"

    id = Column(Integer, primary_key=True, index=True)
    device_category = Column(String(32), nullable=False, index=True)
    brand = Column(String(128), nullable=False, index=True)
    pattern_raw = Column(String(512), nullable=False)
    pattern_regex = Column(String(1024), nullable=False)
    end_type = Column(String(32), nullable=False)
    priority = Column(Integer, nullable=False, server_default="100")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LenovoPriceTapeLibrary(Base):
    """磁带库价格：端型 × 驱动器配置 × SLA"""
    __tablename__ = "lenovo_price_tape_library"

    id = Column(Integer, primary_key=True, index=True)
    end_type = Column(String(16), nullable=False)             # 低端/中端/高端
    drive_config = Column(String(16), nullable=False)         # LTO5/LTO6/LTO7/LTO8
    sla = Column(String(32), nullable=False)                  # 5*9*NBD维保 / 7*24*ND维保 / 7*24*4上门维保
    price = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("end_type", "drive_config", "sla", name="uq_lenovo_price_tape"),
    )


class LenovoPriceNetwork(Base):
    """网络/光纤/IB 价格：设备大类 × 端型 × SLA"""
    __tablename__ = "lenovo_price_network"

    id = Column(Integer, primary_key=True, index=True)
    device_category = Column(String(32), nullable=False)
    # FC光纤交换机 / 网络交换机 / 路由器 / 无线控制器 / IB光纤交换机
    end_type = Column(String(16), nullable=False)             # 低端/中端
    sla = Column(String(32), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("device_category", "end_type", "sla", name="uq_lenovo_price_network"),
    )


class LenovoPriceServer(Base):
    """服务器价格：端型 × 含SSD × 备件or整包 × SLA × 含硬盘"""
    __tablename__ = "lenovo_price_server"

    id = Column(Integer, primary_key=True, index=True)
    end_type = Column(String(16), nullable=False)             # 低端/中端/高端
    includes_ssd = Column(Boolean, nullable=False)            # True=含SSD, False=不含
    package_type = Column(String(16), nullable=False)         # 备件维保 / 整包
    sla = Column(String(16), nullable=False)                  # 5*9*NBD / 7*24 / 7*24*4
    includes_disk = Column(Boolean, nullable=False)           # True=含硬盘不返还, False=不含硬盘不返还
    price = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "end_type", "includes_ssd", "package_type", "sla", "includes_disk",
            name="uq_lenovo_price_server",
        ),
    )


class LenovoPriceStorage(Base):
    """存储新口径价格：端型(L1/L2/M) × SLA × 含硬盘不回收"""
    __tablename__ = "lenovo_price_storage"

    id = Column(Integer, primary_key=True, index=True)
    end_type = Column(String(8), nullable=False)              # L1 / L2 / M
    sla = Column(String(16), nullable=False)                  # 5*9*NBD / 7*24 / 7*24*4
    includes_disk_no_return = Column(Boolean, nullable=False) # True=含硬盘不回收
    price = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("end_type", "sla", "includes_disk_no_return", name="uq_lenovo_price_storage"),
    )


class LenovoPriceMinicomputer(Base):
    """小型机价格：端型 × SLA × 含硬盘"""
    __tablename__ = "lenovo_price_minicomputer"

    id = Column(Integer, primary_key=True, index=True)
    end_type = Column(String(16), nullable=False)             # 低端/中端/高端/超高端
    sla = Column(String(32), nullable=False)
    includes_disk = Column(Boolean, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("end_type", "sla", "includes_disk", name="uq_lenovo_price_mini"),
    )


class LenovoFrameworkModel(Base):
    """统一的"联想框架机型库"

    将原 lenovo_classification（人工录入的机型分类）+ lenovo_pattern_rule 展开后的具体机型
    + 从 device_inventory / office_device_inventory 导入的型号 合并存储。

    匹配链路的"事实表"：报价时按 (device_category, lower(brand), lower(model)) 精确查找。
    端型允许 NULL —— 由 dc_inventory 导入但无端型信息的记录留空，由用户在前端报价时手动选择，
    选定后回写。
    """
    __tablename__ = "lenovo_framework_models"

    id = Column(Integer, primary_key=True, index=True)

    device_category = Column(String(32), nullable=False, index=True)
    # 磁带库 / 服务器 / 存储 / 小型机 / 网络设备 / 光纤交换机 / IB交换机

    brand = Column(String(128), nullable=True, index=True)
    series = Column(String(128), nullable=True)
    model = Column(String(255), nullable=False, index=True)
    mt_code = Column(String(64), nullable=True)

    end_type = Column(String(16), nullable=True)
    # 低端 / 中端 / 高端 / 超高端 / L1 / L2 / M。NULL = 留待人工指定。

    sub_category = Column(String(32), nullable=True)
    # 仅 device_category=网络设备 时使用: 网络交换机 / 路由器 / 无线AP / 无线控制器

    source = Column(String(32), nullable=False, server_default="manual")
    # classification / pattern_expanded / dc_inventory / office_inventory / manual / user_confirmed

    source_ref_id = Column(Integer, nullable=True)
    # 来源原始记录的 id（如 device_inventory.id），用于追溯

    aliases = Column(JSONB, nullable=True, server_default="[]")
    # 「原始品牌型号」别名数组（归一化字符串）。
    # 用户上传的 "Dell-PowerEdge R630" / "DELL R630" 等 raw 字符串归一化后存入。
    # 匹配链路最前置：normalize(input) 在 aliases 数组里命中即返回。

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("device_category", "brand", "model", name="uq_lenovo_models"),
        Index("ix_lenovo_models_lookup", "device_category", "model"),
    )


class LenovoPriceInspection(Base):
    """巡检价格（仅标准价）"""
    __tablename__ = "lenovo_price_inspection"

    id = Column(Integer, primary_key=True, index=True)
    unit = Column(String(16), nullable=False, unique=True)    # 人天 / 半人天
    price = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(6, 4), nullable=False, server_default="0.06")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
