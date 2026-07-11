"""
Alembic 迁移环境配置

直接复用 app.database 的 engine 实例，避免 str(engine.url) 密码被遮蔽导致连接失败。
"""
from logging.config import fileConfig
from alembic import context
import os
import sys

# 将 backend/ 加入 sys.path，确保能 import app.*
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, engine

# 导入所有 model，确保 Base.metadata 包含全部表
# 1) models 包（__init__.py 已导出大部分模型）
from app import models  # noqa: F401
# 2) models 包中未在 __init__.py 导出的模型
from app.models.manual_matching_override import ManualMatchingOverride  # noqa: F401
from app.models.service_personnel import ServicePersonnel  # noqa: F401
from app.models.pricing_parameter import PricingParameter  # noqa: F401
from app.models.single_service import SingleService  # noqa: F401
from app.models.job_position import JobPosition, JobPositionSalary  # noqa: F401
from app.models.dispatch_service import DispatchService  # noqa: F401
from app.models.superimposed_price import SuperimposedPrice  # noqa: F401
from app.models.city_social_insurance import CitySocialInsurance  # noqa: F401
from app.models.user_profile import UserProfile  # noqa: F401
# 3) 定义在 router 中的模型（历史遗留，模型内联于路由文件）
from app.routers.service_level import ServiceLevel  # noqa: F401
from app.routers.service_terms import ServiceTerm  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：生成 SQL 脚本而不连接数据库"""
    url = engine.url.render_as_string(hide_password=False)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：直接复用应用的 engine，确保连接参数一致"""
    with engine.connect() as connection:
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
