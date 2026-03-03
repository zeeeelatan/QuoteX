import pandas as pd
import psycopg2
from datetime import datetime
from sqlalchemy import create_engine
import os
from urllib.parse import urlparse
from sqlalchemy.engine import URL

# 数据库连接配置
def _try_get_backend_database_url():
    """
    尝试读取后端正在使用的数据库连接串，避免“克隆后库名变化”导致脚本与系统不一致。
    - 先读环境变量 DATABASE_URL
    - 再尝试从 backend/app/database.py 导入 SQLALCHEMY_DATABASE_URL
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    try:
        from backend.app.database import SQLALCHEMY_DATABASE_URL  # type: ignore
        return SQLALCHEMY_DATABASE_URL
    except Exception:
        return None


_backend_url = _try_get_backend_database_url()
_parsed = urlparse(_backend_url) if _backend_url else None

# 优先读取环境变量（便于不同环境复用），其次跟随后端配置，最后才回落到默认值
DB_NAME = (
    os.getenv("DB_NAME")
    or os.getenv("POSTGRES_DB")
    or (_parsed.path.lstrip("/") if _parsed and _parsed.path else None)
    or "device_inventory_ai_quote_test"  # 与后端 database.py 保持一致
)
DB_USER = (
    os.getenv("DB_USER")
    or os.getenv("POSTGRES_USER")
    or (_parsed.username if _parsed and _parsed.username else None)
    or "device_inventory_user"  # 与后端 database.py 保持一致
)
DB_PASSWORD = (
    os.getenv("DB_PASSWORD")
    or os.getenv("POSTGRES_PASSWORD")
    or (_parsed.password if _parsed and _parsed.password else None)
    or "change_me_password"  # 与后端 database.py 保持一致
)
DB_HOST = (
    os.getenv("DB_HOST")
    or os.getenv("POSTGRES_HOST")
    or (_parsed.hostname if _parsed and _parsed.hostname else None)
    or "localhost"
)
DB_PORT = str(
    os.getenv("DB_PORT")
    or os.getenv("POSTGRES_PORT")
    or (_parsed.port if _parsed and _parsed.port else None)
    or "5432"
)

# Excel 文件路径
# Excel 文件路径：请修改为实际路径，或通过环境变量 IMPORT_EXCEL_FILE 指定
EXCEL_FILE = os.getenv("IMPORT_EXCEL_FILE", "./data/(导入)DC基础数据.xlsx")

def connect_to_db():
    """创建数据库连接"""
    kwargs = dict(dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT)
    if DB_PASSWORD:
        kwargs["password"] = DB_PASSWORD
    return psycopg2.connect(**kwargs)

def clear_table(conn):
    """清空设备清单表"""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM device_inventory;")
        conn.commit()
    print("表已清空")

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
            '设备档次': 'device_grade',
            '机架高度(U)': 'rack_height_u'
        }

        # 只保留需要的列（允许列不存在，兼容旧版Excel）
        available_columns = [col for col in column_mapping.keys() if col in df.columns]
        df = df[available_columns]
        
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
        df.to_sql('device_inventory', engine, if_exists='append', index=False)
        
        print("数据导入成功！")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_data() 
