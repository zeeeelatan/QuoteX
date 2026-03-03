"""
叠加单价数据模型
用于存储叠加服务的单价信息
"""

from sqlalchemy import Column, Integer, String, Text, DECIMAL
from app.database import Base


class SuperimposedPrice(Base):
    """叠加单价数据表"""
    __tablename__ = "superimposed_price"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    price_description = Column(String(255), nullable=False, comment="单价说明")
    charging_standard = Column(String(500), nullable=False, comment="收费标准")
    applicable_products = Column(Text, nullable=True, comment="适用产品（JSON数组字符串）")
    remarks = Column(Text, nullable=True, comment="备注")

    def __repr__(self):
        return f"<SuperimposedPrice({self.price_description})>"
