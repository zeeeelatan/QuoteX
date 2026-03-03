from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from .app import models

# 示例数据
sample_devices = [
    {
        "category": "存储设备",
        "manufacturer": "华为",
        "model": "E9000",
        "full_price": 850000.0,
        "description": "华为E9000刀片式服务器"
    },
    {
        "category": "网络设备",
        "manufacturer": "华为",
        "model": "S5720",
        "full_price": 35000.0,
        "description": "华为S5720以太网交换机"
    },
    {
        "category": "服务器",
        "manufacturer": "联想",
        "model": "ThinkSystem SR650",
        "full_price": 75000.0,
        "description": "联想ThinkSystem SR650机架式服务器"
    },
    {
        "category": "存储设备",
        "manufacturer": "IBM",
        "model": "DS8886",
        "full_price": 1250000.0,
        "description": "IBM DS8886企业级存储系统"
    },
    {
        "category": "软件",
        "manufacturer": "Oracle",
        "model": "Database 19c",
        "full_price": 450000.0,
        "description": "Oracle Database 19c企业版数据库"
    }
]

def init_db():
    # 创建数据库表
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 清空现有数据
        db.query(models.DeviceModel).delete()
        
        # 添加示例数据
        for device_data in sample_devices:
            device = models.DeviceModel(**device_data)
            db.add(device)
        
        db.commit()
        print("数据库初始化成功，已添加示例数据。")
    except Exception as e:
        db.rollback()
        print(f"初始化数据库失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("正在初始化数据库...")
    init_db()