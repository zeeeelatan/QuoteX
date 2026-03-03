from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SparePart(Base):
    __tablename__ = "spare_part"

    id = Column(Integer, primary_key=True, index=True)

    manufacturer = Column(String, nullable=False)         # 厂商
    part_pn = Column(String, nullable=False)               # 备件PN
    part_desc = Column(String, nullable=False)             # 备件描述
    part_category = Column(String, nullable=False)         # 备件分类
    part_condition = Column(String, nullable=False)        # 备件成色
    repair_method = Column(String, nullable=False)         # 报修方式
    repair_period = Column(String, nullable=False)         # 报修期限

    unit_price = Column(Numeric(14, 2), nullable=False)    # 单价（元）

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


