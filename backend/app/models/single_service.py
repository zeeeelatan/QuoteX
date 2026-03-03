from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, func, Text
from app.database import Base


class SingleService(Base):
    """单次服务数据"""
    __tablename__ = "single_service"

    id = Column(Integer, primary_key=True, index=True)
    business_type = Column(String(64), nullable=False, index=True)  # 业务类型
    service_name = Column(String(128), nullable=False, index=True)  # 服务名称
    service_detail = Column(String(255), nullable=False)  # 服务细项
    device_type = Column(String(128), nullable=False)  # 设备类型（硬件/软件）
    device_level = Column(String(64), nullable=False)  # 设备/服务级别
    engineer_capability = Column(String(16), nullable=False)  # 工程师能力标签
    quantity = Column(DECIMAL(10, 2), nullable=False)  # 数量
    on_site_fee = Column(DECIMAL(10, 2), nullable=False)  # 上门费用
    base_hours = Column(DECIMAL(10, 2), nullable=False)  # 基准工时数
    base_hourly_rate = Column(DECIMAL(10, 2), nullable=False)  # 基准工时费
    unit = Column(String(16), nullable=False)  # 单位
    standard_quote = Column(DECIMAL(10, 2), nullable=False)  # 标准报价
    emergency_response = Column(DECIMAL(10, 3))  # 紧急响应系数
    special_time_period = Column(DECIMAL(10, 3))  # 特殊时间段（夜晚及节假日）
    tier1_city = Column(DECIMAL(10, 3))  # 一线/新一线/省会城市
    other_city = Column(DECIMAL(10, 3))  # 其他城市
    remarks = Column(Text)  # 备注
    applicable_cities = Column(Text)  # 适用城市
    batch_demand = Column(DECIMAL(10, 3))  # 批量需求(每增加一次)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
