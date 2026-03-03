from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, func, Text
from app.database import Base


class ServicePersonnel(Base):
    """服务人员数据 - 管理可用于项目报价的技术服务人员及其费率标准"""
    __tablename__ = "service_personnel"

    id = Column(Integer, primary_key=True, index=True)
    personnel_type = Column(String(64), nullable=False, index=True)  # 服务人员类型，如 桌面运维工程师
    skill_description = Column(Text, nullable=True)  # 技能描述
    skill_level = Column(String(32), nullable=False, index=True)  # 能力级别：专家、高级、中级、初级
    service_mode = Column(String(32), nullable=False, index=True)  # 服务模式：远程、现场
    daily_rate = Column(DECIMAL(10, 2), nullable=False)  # 人天单价
    tags = Column(String(255), nullable=True)  # 特长标签，如 "CCIE证书,PMP"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
