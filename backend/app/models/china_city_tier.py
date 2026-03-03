"""
中国城市分级表数据模型
存储城市等级、行政级别、物流枢纽等级等
"""

from sqlalchemy import Column, Integer, String
from app.database import Base


class ChinaCityTier(Base):
    """中国城市分级表"""
    __tablename__ = "china_city_tier"

    id = Column(Integer, primary_key=True, index=True)

    seq_no = Column(Integer, nullable=True, comment="序号")
    city_tier = Column(String(50), nullable=True, comment="城市等级")
    tier_code = Column(String(20), nullable=True, comment="城市等级代码")
    city_name = Column(String(50), nullable=False, comment="城市名称")
    province = Column(String(50), nullable=True, comment="所属省份")
    admin_level = Column(String(50), nullable=True, comment="行政级别")
    is_provincial_capital = Column(String(10), nullable=True, comment="是否省会")
    is_gdp_trillion = Column(String(10), nullable=True, comment="GDP万亿城市")
    logistics_hub_level = Column(String(50), nullable=True, comment="物流枢纽等级")
    remarks = Column(String(200), nullable=True, comment="备注")
