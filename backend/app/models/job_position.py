"""
驻场岗位职级与城市薪资数据模型
对应《IT岗位技术与管理序列分级表_含薪资》：
- job_position: 岗位职级（技术序列 23 岗位 x 4 级 + 管理序列 9 方向 x 3 级）
- job_position_salary: 岗位在各城市的税前月薪（仅存有数据的城市）
"""

from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, DateTime,
    ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class JobPosition(Base):
    """驻场岗位职级表"""
    __tablename__ = "job_position"
    __table_args__ = (
        UniqueConstraint("position_name", "level_name", name="uq_job_position_name_level"),
    )

    id = Column(Integer, primary_key=True, index=True)
    sequence_type = Column(String(20), nullable=False, index=True, comment="序列类型（技术序列/管理序列）")
    category = Column(String(50), nullable=False, index=True, comment="岗位类别/管理方向")
    position_name = Column(String(128), nullable=False, index=True, comment="岗位名称")
    level_name = Column(String(64), nullable=False, comment="技术级别/管理级别全称")
    level_rank = Column(Integer, nullable=False, default=1, comment="级别排序（1最低）")

    core_requirements = Column(Text, nullable=True, comment="级别核心要求(含建议认证)")
    certifications = Column(Text, nullable=True, comment="适用认证参考")
    work_content = Column(Text, nullable=True, comment="工作内容")
    deliverables = Column(Text, nullable=True, comment="工作产出/交付物")
    kpi_standards = Column(Text, nullable=True, comment="KPI考核点及标准参考值")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    salaries = relationship(
        "JobPositionSalary",
        back_populates="position",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class JobPositionSalary(Base):
    """岗位城市薪资表"""
    __tablename__ = "job_position_salary"
    __table_args__ = (
        UniqueConstraint("position_id", "city", name="uq_job_position_salary_city"),
    )

    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(
        Integer,
        ForeignKey("job_position.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="岗位职级ID",
    )
    province = Column(String(50), nullable=True, comment="省份")
    city = Column(String(50), nullable=False, index=True, comment="城市")
    salary = Column(DECIMAL(10, 2), nullable=False, comment="税前月薪(元)")

    position = relationship("JobPosition", back_populates="salaries")
