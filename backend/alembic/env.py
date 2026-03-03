"""
Alembic 迁移环境配置

从 app.database 复用数据库连接配置，确保与应用使用同一套环境变量。
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# 将 backend/ 加入 sys.path，确保能 import app.*
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, SQLALCHEMY_DATABASE_URL

# 导入所有 model，确保 Base.metadata 包含全部表
from app import models  # noqa: F401
from app.models.office_device_inventory import OfficeDeviceInventory  # noqa: F401
from app.models.manual_matching_override import ManualMatchingOverride  # noqa: F401
from app.models.service_level import ServiceLevel  # noqa: F401
from app.models.service_terms import ServiceTerms  # noqa: F401
from app.models.service_personnel import ServicePersonnel  # noqa: F401
from app.models.pricing_parameter import PricingParameter  # noqa: F401
from app.models.single_service import SingleService  # noqa: F401
from app.models.outsourced_personnel import OutsourcedPersonnel  # noqa: F401
from app.models.dispatch_service import DispatchService  # noqa: F401
from app.models.superimposed_price import SuperimposedPrice  # noqa: F401
from app.models.city_social_insurance import CitySocialInsurance  # noqa: F401
from app.models.user_profile import UserProfile  # noqa: F401

config = context.config

# 用应用的数据库 URL 覆盖 alembic.ini 中的占位值
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：生成 SQL 脚本而不连接数据库"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：连接数据库执行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
