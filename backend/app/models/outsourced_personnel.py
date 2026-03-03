from sqlalchemy import Column, Integer, String, Text, DECIMAL
from app.database import Base


class OutsourcedPersonnel(Base):
    """外包人员岗位及薪资 - 管理外包人员的岗位级别、能力要求及薪资标准"""
    __tablename__ = "outsourced_personnel"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(String(64), nullable=False, index=True, comment="岗位")
    level = Column(String(32), nullable=False, index=True, comment="级别")
    subtype = Column(String(10), nullable=True, comment="子类型（A/B）")
    education = Column(String(64), nullable=False, comment="学历要求")
    language_requirement = Column(String(255), nullable=False, comment="语言要求")
    work_experience = Column(String(128), nullable=True, comment="工作经验要求")
    general_ability = Column(Text, nullable=True, comment="通用能力要求")
    technical_skill = Column(Text, nullable=True, comment="专业技术要求")
    tier1_city_salary = Column(DECIMAL(10, 2), nullable=True, comment="一线城市参考月工资")
