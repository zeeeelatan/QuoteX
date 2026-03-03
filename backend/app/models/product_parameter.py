from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, func, Text
from app.database import Base


class BaseRate(Base):
    """基础费率设置 - 金牌/银牌/铜牌服务"""
    __tablename__ = "base_rate"
    id = Column(Integer, primary_key=True, index=True)
    level_code = Column(String(32), nullable=False, unique=True)  # gold, silver, bronze
    level_name = Column(String(64), nullable=False)  # 金牌服务, 银牌服务, 铜牌服务
    level_desc = Column(String(255))  # 7x24小时 + 4小时到场
    rate_value = Column(DECIMAL(6, 4), nullable=False)  # 费率值 (小数，如0.185表示18.5%)
    trend_value = Column(DECIMAL(6, 4))  # 趋势值 (小数，如0.012表示+1.2%)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SLAConfig(Base):
    """调节系数配置"""
    __tablename__ = "sla_config"
    id = Column(Integer, primary_key=True, index=True)
    coefficient_name = Column(String(128), nullable=False)  # 高风险, 特殊时段, 紧急程度
    description = Column(Text)  # 描述
    # 保留旧字段以兼容现有数据
    sla_name = Column(String(128))  # 旧字段，保留兼容
    sla_name_cn = Column(String(128))  # 旧字段，保留兼容
    response_time = Column(String(64))  # 旧字段，保留兼容
    repair_time = Column(String(64))  # 旧字段，保留兼容
    coefficient = Column(DECIMAL(6, 3), nullable=False)  # 成本系数
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class HardwareDepreciation(Base):
    """硬件折旧系数"""
    __tablename__ = "hardware_depreciation"
    id = Column(Integer, primary_key=True, index=True)
    device_type = Column(String(64), nullable=False, unique=True)  # 服务器, 存储设备, 网络设备
    rate_value = Column(DECIMAL(6, 4), nullable=False)  # 年折旧率 (小数，如0.025表示2.5%)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RegionalAdjustment(Base):
    """区域调节系数"""
    __tablename__ = "regional_adjustment"
    id = Column(Integer, primary_key=True, index=True)
    region_code = Column(String(16), nullable=False, unique=True)  # CN, HK, SG
    region_name = Column(String(64), nullable=False)  # 华东区, 港澳台, 亚太其他
    coefficient = Column(DECIMAL(6, 3), nullable=False, default=1.0)  # 调节系数
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
