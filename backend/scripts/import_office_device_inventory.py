import os
import sys
import pandas as pd
from sqlalchemy.orm import Session

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.database import SessionLocal, engine
from app.models.office_device_inventory import OfficeDeviceInventory


EXCEL_PATH = os.getenv("IMPORT_EXCEL_FILE", "./data/办公设备数据.xlsx")

SHEET_NAME = 0  # 默认第一张表

# Excel中文列名到数据库字段名的映射（与 device_inventory 一致）
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


def create_table_if_not_exists():
    # 通过模型元数据确保表存在
    OfficeDeviceInventory.metadata.create_all(bind=engine)


def import_excel_to_db():
    print(f"读取Excel: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    print("Excel原始列名:", list(df.columns))

    # 重命名为数据库字段名
    df = df.rename(columns=df_column_map)

    # 仅保留模型字段
    model_fields = set(c.name for c in OfficeDeviceInventory.__table__.columns)
    keep_cols = [col for col in df.columns if col in model_fields]
    df = df[keep_cols]

    # 将 NaN 转为空字符串/None 以避免类型问题
    df = df.where(pd.notnull(df), None)

    records = df.to_dict(orient='records')
    print(f"准备导入 {len(records)} 条记录到 office_device_inventory 表")

    session: Session = SessionLocal()
    try:
        # 清空并重导（如需追加可删除此行）
        session.query(OfficeDeviceInventory).delete()
        session.commit()

        objs = [OfficeDeviceInventory(**record) for record in records]
        session.bulk_save_objects(objs)
        session.commit()
        print(f"成功导入 {len(objs)} 条记录！")
    except Exception as e:
        session.rollback()
        print("导入失败:", e)
        raise
    finally:
        session.close()


if __name__ == '__main__':
    create_table_if_not_exists()
    import_excel_to_db()


