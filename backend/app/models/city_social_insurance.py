"""
城市社保基准数据模型
存储各城市的社保缴纳基数和比例
"""

from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base


class CitySocialInsurance(Base):
    """城市社保基准数据表"""
    __tablename__ = "city_social_insurance"

    id = Column(Integer, primary_key=True, index=True)

    # 地区信息
    province = Column(String(50), nullable=False, comment="省份")
    city = Column(String(50), nullable=False, comment="城市")
    city_alias = Column(String(50), nullable=True, comment="城市别名（如：深圳（非深户））")

    # 社保基数
    upper_limit = Column(Integer, nullable=False, comment="社保基数上限")
    lower_limit = Column(Integer, nullable=False, comment="社保基数下限")
    calc_base = Column(Integer, nullable=False, comment="计算基数")
    injury_base = Column(Integer, nullable=True, comment="工伤扣款基数")

    # 公司部分比例
    corp_pension_rate = Column(Float, nullable=True, comment="养老保险-公司比例")
    corp_medical_rate = Column(Float, nullable=True, comment="医疗保险-公司比例")
    corp_injury_rate = Column(Float, nullable=True, comment="工伤保险-公司比例")
    corp_maternity_rate = Column(Float, nullable=True, comment="生育保险-公司比例")
    corp_unemployment_rate = Column(Float, nullable=True, comment="失业保险-公司比例")
    corp_disability_rate = Column(Float, nullable=True, comment="残保金-公司比例")
    corp_fund_rate = Column(Float, nullable=True, comment="公积金-公司比例")

    # 个人部分比例
    indiv_pension_rate = Column(Float, nullable=True, comment="养老保险-个人比例")
    indiv_medical_rate = Column(Float, nullable=True, comment="医疗保险-个人比例")
    indiv_injury_rate = Column(Float, nullable=True, comment="工伤保险-个人比例")
    indiv_maternity_rate = Column(Float, nullable=True, comment="生育保险-个人比例")
    indiv_unemployment_rate = Column(Float, nullable=True, comment="失业保险-个人比例")
    indiv_fund_rate = Column(Float, nullable=True, comment="公积金-个人比例")

    # 扩展字段
    is_active = Column(Boolean, default=True, comment="是否启用")
    remarks = Column(String(500), nullable=True, comment="备注")
