#!/usr/bin/env python3
"""
创建服务级别表的独立脚本
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from app.database import Base, engine

class ServiceLevel(Base):
    __tablename__ = "service_level"
    
    id = Column(Integer, primary_key=True, index=True)
    level_code = Column(String, nullable=False)  # 服务级别
    response_time = Column(String, nullable=False)  # 响应时效
    coefficient = Column(Numeric(10, 2), nullable=False)  # 服务级别系数值
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

if __name__ == "__main__":
    print("Creating service_level table...")
    ServiceLevel.__table__.create(engine, checkfirst=True)
    print("Table created successfully!") 