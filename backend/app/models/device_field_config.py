from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class DeviceFieldConfig(Base):
    """设备动态字段配置表 — 定义每种设备类型的扩展字段"""
    __tablename__ = "device_field_config"

    id = Column(Integer, primary_key=True, index=True)
    device_type = Column(String, nullable=True, index=True)  # 关联任意分类级别(一/二/三级)，NULL 表示全局通用
    field_key = Column(String, nullable=False)                # 字段标识，如 "port_speed"
    field_label = Column(String, nullable=False)              # 显示名，如 "端口速率"
    field_type = Column(String, default="string")             # string / number / enum / boolean
    required = Column(Boolean, default=False)
    enum_options = Column(JSONB, nullable=True)               # 枚举选项，如 ["10GbE","25GbE"]
    default_value = Column(String, nullable=True)
    display_order = Column(Integer, default=0)
    scope = Column(String, default="type")                    # "type"(类型级) / "instance"(实例级)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
