from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Manufacturer(Base):
    """品牌字典表 — 统一管理设备厂商名称与别名"""
    __tablename__ = "manufacturer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)   # 标准名称，如 "华为/HUAWEI"
    aliases = Column(JSONB, default=[])                   # 别名列表 ["HuaWei","HUAWEI","huawei","华为"]
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
