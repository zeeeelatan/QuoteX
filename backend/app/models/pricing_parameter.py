from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, func
from app.database import Base


class PricingParameter(Base):
    """调价参数统一表"""
    __tablename__ = "pricing_parameter"

    id = Column(Integer, primary_key=True, index=True)
    parameter_category = Column(String(64), nullable=False, index=True)  # 调价参数项：学历名称、工作年限、服务模式等
    parameter_value = Column(String(128), nullable=False)  # 调价参数值：博士、10年、人工维保等
    applicable_products = Column(String(1000), nullable=True)  # 适用产品，JSON字符串
    coefficient = Column(DECIMAL(10, 3), nullable=False)  # 系数值
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
