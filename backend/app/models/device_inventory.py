from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class DeviceInventory(Base):
    __tablename__ = "device_inventory"

    id = Column(Integer, primary_key=True, index=True)

    # 品牌 — 外键引用字典表 + 冗余文本列（方便查询与导出）
    manufacturer_id = Column(Integer, ForeignKey("manufacturer.id"), nullable=True, index=True)
    manufacturer_name = Column(String, nullable=True, index=True)  # 冗余：存储标准品牌名

    # 保留原始 manufacturer 列用于过渡期兼容，后续清理时移除
    manufacturer = Column(String)

    model_number = Column(String)
    device_price = Column(Numeric)

    primary_category = Column(String)
    secondary_category = Column(String)
    tertiary_category = Column(String)

    business_scenario = Column(Text)
    remarks = Column(Text)
    device_grade = Column(String)
    device_series = Column(String)

    # 动态扩展字段
    type_attributes = Column(JSONB, default={})     # 类型级私有字段，如 {"port_speed":"10GbE","port_count":48}
    custom_attributes = Column(JSONB, default={})   # 实例级私有字段，如 {"color":"黑色"}

    # 保留 rack_height_u 用于过渡期兼容，后续数据迁移到 type_attributes 后移除
    rack_height_u = Column(Integer)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)
