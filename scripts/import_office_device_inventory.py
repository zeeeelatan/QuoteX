import pandas as pd
import psycopg2
from datetime import datetime
from sqlalchemy import create_engine
import os
import sys
from sqlalchemy.engine import URL

# 数据库连接配置（直接指向新数据库实例；如需临时切换仅可通过环境变量显式覆盖）
DB_NAME = os.getenv("DB_NAME") or os.getenv("POSTGRES_DB") or "device_inventory_ai_quote_test"
DB_USER = os.getenv("DB_USER") or os.getenv("POSTGRES_USER") or "device_inventory_user"
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST") or "localhost"
DB_PORT = str(os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT") or "5432")

print(f"[import_office_device_inventory] target_db={DB_NAME} user={DB_USER} host={DB_HOST} port={DB_PORT}")

# Excel 文件路径
# Excel 文件路径：请修改为实际路径，或通过环境变量 IMPORT_EXCEL_FILE 指定
EXCEL_FILE = os.getenv("IMPORT_EXCEL_FILE", os.path.expanduser("~/Desktop/报价/维保报价数据/办公设备数据.xlsx"))

def connect_to_db():
    """创建数据库连接"""
    kwargs = dict(dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT)
    if DB_PASSWORD:
        kwargs["password"] = DB_PASSWORD
    return psycopg2.connect(**kwargs)

def clear_table(conn):
    """清空办公设备清单表"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM office_device_inventory;")
        conn.commit()
    print("办公设备表已清空")

def import_data():
    """导入数据的主函数"""
    try:
        # 读取Excel文件
        print(f"正在读取Excel文件: {EXCEL_FILE}")
        df = pd.read_excel(EXCEL_FILE)
        
        print("Excel列名:", df.columns.tolist())
        
        # 重命名列以匹配数据库字段
        column_mapping = {
            '厂商': 'manufacturer',
            '设备系列': 'device_series',
            '设备型号': 'model_number',
            '业务场景': 'business_scenario',
            '设备一级分类': 'primary_category',
            '设备二级分类': 'secondary_category',
            '设备三级分类': 'tertiary_category',
            '备注': 'remarks',
            '整机价格': 'device_price',
            '设备档次': 'device_grade'
        }
        
        # 只保留需要的列
        df = df[list(column_mapping.keys())]
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 添加时间戳
        current_time = datetime.now()
        df['created_at'] = current_time
        df['updated_at'] = current_time
        
        print("处理后的列名:", df.columns.tolist())
        
        # 连接数据库并清空表
        conn = connect_to_db()
        clear_table(conn)
        
        # 创建SQLAlchemy引擎
        engine = create_engine(
            URL.create(
                "postgresql+psycopg2",
                username=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=int(DB_PORT),
                database=DB_NAME,
            )
        )
        
        # 将数据导入到数据库
        df.to_sql('office_device_inventory', engine, if_exists='append', index=False)
        
        # 导入后做一次快速校验（行数）
        with engine.connect() as c:
            count = c.exec_driver_sql("SELECT COUNT(*) FROM office_device_inventory").scalar_one()
        print(f"办公设备数据导入成功！office_device_inventory 行数={count}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_data()




