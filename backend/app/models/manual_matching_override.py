"""
手动匹配覆盖模型
用于存储用户手动调整后的匹配结果，优先级高于AI匹配
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class ManualMatchingOverride(Base):
    __tablename__ = "manual_matching_override"

    id = Column(Integer, primary_key=True, index=True)
    # 原始信息（来自用户上传的Excel）
    original_manufacturer = Column(String(255), nullable=True, default='', comment="原始厂商（可为空）")
    original_model = Column(String(255), nullable=False, comment="原始型号")

    # 手动匹配结果（来自设备库）
    matched_manufacturer = Column(String(255), nullable=False, comment="匹配后厂商")
    matched_model_number = Column(String(255), nullable=False, comment="匹配后型号")
    device_price = Column(Float, comment="设备价格")
    primary_category = Column(String(255), comment="一级分类")
    secondary_category = Column(String(255), comment="二级分类")
    tertiary_category = Column(String(255), comment="三级分类")
    device_category = Column(String(255), comment="设备分类")

    # 数据来源
    data_source = Column(String(50), default="datacenter", comment="数据来源: datacenter/office")

    # 确认状态
    is_confirmed = Column(Boolean, default=False, comment="是否已确认")
    confirmed_at = Column(DateTime(timezone=True), comment="确认时间")

    # 审计字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 备注
    notes = Column(Text, comment="备注")

    def __repr__(self):
        return f"<ManualMatchingOverride(id={self.id}, original={self.original_manufacturer} {self.original_model}, matched={self.matched_model_number})>"
