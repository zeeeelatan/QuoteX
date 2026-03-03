from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy.engine import URL

"""
数据库连接配置（支持通过环境变量覆盖，便于“克隆后库名变化/多环境部署”）

优先级：
- DATABASE_URL（完整连接串）
- DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT（拼接生成）
- 兜底为当前默认值（保持兼容）
"""

DEFAULT_DB_NAME = "device_inventory_ai_quote_test"
DEFAULT_DB_USER = "device_inventory_user"
DEFAULT_DB_PASSWORD = "change_me_password"
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 5432

_database_url_env = os.getenv("DATABASE_URL")
if _database_url_env:
    SQLALCHEMY_DATABASE_URL = _database_url_env
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    db_name = os.getenv("DB_NAME") or os.getenv("POSTGRES_DB") or DEFAULT_DB_NAME
    db_user = os.getenv("DB_USER") or os.getenv("POSTGRES_USER") or DEFAULT_DB_USER
    db_password = os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD") or DEFAULT_DB_PASSWORD
    # 在 Docker 内未设置 DB_HOST 时使用服务名 postgres，避免连到 localhost
    _db_host = os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST")
    if _db_host:
        db_host = _db_host
    elif os.path.exists("/.dockerenv"):
        db_host = "postgres"
    else:
        db_host = DEFAULT_DB_HOST
    db_port = int(os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT") or DEFAULT_DB_PORT)

    engine = create_engine(
        URL.create(
            "postgresql+psycopg2",
            username=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name,
        )
    )
    # 仅用于打印/调试（在运行时可通过环境变量验证到底连到哪个库）
    SQLALCHEMY_DATABASE_URL = str(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
