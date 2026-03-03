"""
派单服务数据模型
用于存储派单服务的定价信息
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Text
from app.database import Base


class DispatchService(Base):
    """派单服务数据表"""
    __tablename__ = "dispatch_service"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    service_type = Column(String(50), nullable=False, index=True, comment="服务类型：标准报价/加急报价/人天报价/半天报价")
    unit_hours = Column(String(20), nullable=False, index=True, comment="单位工时：2小时/8小时")
    time_window = Column(String(20), nullable=False, index=True, comment="服务时间窗口：5*8/5*12/7*8/7*12")
    response_time = Column(String(20), nullable=False, index=True, comment="响应时效：4小时/8小时")
    city_tier = Column(String(20), nullable=False, index=True, comment="城市等级：一级城市/二级城市/三级城市")
    price = Column(DECIMAL(10, 2), nullable=False, comment="服务价格（元）")
    description = Column(Text, nullable=True, comment="描述说明")

    def __repr__(self):
        return f"<DispatchService({self.service_type}, {self.unit_hours}, {self.city_tier}, {self.price})>"
