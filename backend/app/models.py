from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

class ServiceLevel(Base):
    """SLA 标准等级表

    语义按《SLA服务等级标准定义表 - 常用SLA等级表》对齐：
    - level_code   = 服务等级（如 经济级 / 基础级 / 标准级 / 增强级 / 高级 / 关键业务级）
    - response_time= SLA 组合（如 5×8×NBD / 7×24×4 / 7×24×NBD）
    - definition   = 释义
    - aliases      = 别名列表（JSON 数组），用于把源数据中各种写法
                     （7*24*NBD / 7*24*ND维保 / 7-24-NBD 等）映射到本行
    - coefficient  = 服务级别系数值（保留兼容）
    """
    __tablename__ = "service_level"

    id = Column(Integer, primary_key=True, index=True)
    level_code = Column(String, nullable=False)        # 服务等级
    response_time = Column(String, nullable=False)     # SLA 组合
    definition = Column(Text, nullable=True)           # 释义
    aliases = Column(JSONB, nullable=True, server_default="[]")  # 别名 JSON 数组
    coefficient = Column(Numeric(10, 2), nullable=False)
    applicable_products = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())