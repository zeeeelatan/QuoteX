from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime
from app.database import Base


class OfficeDeviceInventory(Base):
    """
    办公场景设备台账表
    说明：字段与 `device_inventory` 一致，用于区分办公场景的数据来源，
    方便在报价需求中按场景检索与匹配。
    """

    __tablename__ = "office_device_inventory"

    id = Column(Integer, primary_key=True, index=True)
    device_price = Column(Numeric)
    manufacturer = Column(String)
    model_number = Column(String)
    primary_category = Column(String)
    secondary_category = Column(String)
    tertiary_category = Column(String)
    business_scenario = Column(Text)
    remarks = Column(Text)
    device_grade = Column(String)
    device_series = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)



