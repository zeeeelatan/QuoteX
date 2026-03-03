import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import DeviceInventory

EXCEL_PATH = '(导入)DC基础数据20250529-收集数据导入.xlsx'
SHEET_NAME = '基础数据'

# Excel中文列名到数据库字段名的映射
df_column_map = {
    '厂商': 'manufacturer',
    '设备系列': 'device_series',
    '设备型号': 'model_number',
    '业务场景': 'business_scenario',
    '设备一级分类': 'primary_category',
    '设备二级分类': 'secondary_category',
    '设备三级分类': 'tertiary_category',
    '备注': 'remarks',
    '整机价格': 'device_price',
    '设备档次': 'device_grade',
}

def import_excel_to_db():
    # 读取Excel
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    print("Excel原始数据：")
    print(df.head())
    print("原始列名：", list(df.columns))
    # 重命名为数据库字段名
    df = df.rename(columns=df_column_map)
    print("重命名后列名：", list(df.columns))
    # 用数据库字段名过滤列
    model_fields = set(c.name for c in DeviceInventory.__table__.columns)
    print("数据库字段：", list(model_fields))
    df = df[[col for col in df.columns if col in model_fields]]
    # 转为字典列表
    records = df.to_dict(orient='records')

    session: Session = SessionLocal()
    try:
        # 清空表
        session.query(DeviceInventory).delete()
        session.commit()
        # 批量插入
        objs = [DeviceInventory(**record) for record in records]
        session.bulk_save_objects(objs)
        session.commit()
        print(f"成功导入 {len(objs)} 条数据！")
    except Exception as e:
        session.rollback()
        print(f"导入失败: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    import_excel_to_db() 