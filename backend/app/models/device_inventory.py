from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime
from app.database import Base

class DeviceInventory(Base):
    __tablename__ = "device_inventory"

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
    rack_height_u = Column(Integer)  # 机架高度(U)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
