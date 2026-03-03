from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.database import Base


class GPUPrice(Base):
    __tablename__ = "gpu_price"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String, nullable=True)
    series = Column(String, nullable=True)
    model = Column(String, nullable=True)  # 可选：GPU型号/名称
    gpu_memory = Column(String, nullable=True)
    gpu_interface_type = Column(String, nullable=True)
    sales_status = Column(String, nullable=True)

    gpu_price = Column(Numeric(14, 2))            # GPU卡价格（元）
    gpu_rate = Column(Numeric(8, 4))              # GPU卡费率（小数，例如 0.06）
    spare_repair_cost = Column(Numeric(14, 2))    # 备件维修费（元）
    labor_repair_cost = Column(Numeric(14, 2))    # 人工维修费（元）
    service_fee = Column(Numeric(14, 2))          # 维保服务费（元）

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())



