from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, func
from app.database import Base

class MaintenanceRate(Base):
    __tablename__ = "maintenance_rate"
    id = Column(Integer, primary_key=True, index=True)
    primary_category = Column(String(64), nullable=False)
    secondary_category = Column(String(64), nullable=False)
    tertiary_category = Column(String(64), nullable=False)
    rate = Column(DECIMAL(6,4), nullable=False)  # 存小数
    remark = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 