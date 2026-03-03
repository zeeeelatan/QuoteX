from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from .database import Base

class ServiceLevel(Base):
    __tablename__ = "service_level"
    
    id = Column(Integer, primary_key=True, index=True)
    level_code = Column(String, nullable=False)  # 服务级别
    response_time = Column(String, nullable=False)  # 响应时效
    coefficient = Column(Numeric(10, 2), nullable=False)  # 服务级别系数值
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 