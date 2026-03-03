"""
测试公共 fixtures：
- 创建测试用数据库 session（使用真实 PostgreSQL，CI 中通过 service container 提供）
- 创建 FastAPI TestClient
- 预置测试数据
"""
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

from app.database import Base, get_db
from app.main import app

# 测试数据库连接（优先环境变量，兼容 CI 和本地）
TEST_DB_HOST = os.getenv("DB_HOST", "localhost")
TEST_DB_PORT = int(os.getenv("DB_PORT", "5432"))
TEST_DB_NAME = os.getenv("DB_NAME", "ai_quote_test")
TEST_DB_USER = os.getenv("DB_USER", "test_user")
TEST_DB_PASSWORD = os.getenv("DB_PASSWORD", "test_password")

test_engine = create_engine(
    URL.create(
        "postgresql+psycopg2",
        username=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
        database=TEST_DB_NAME,
    )
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """session 级别：创建所有表，测试结束后销毁"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db():
    """每个测试用例独立的数据库 session，结束后回滚"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient，注入测试数据库 session"""
    from httpx import AsyncClient, ASGITransport

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    from starlette.testclient import TestClient
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_devices(db):
    """预置设备数据用于匹配测试"""
    from app.models import DeviceInventory, MaintenanceRate

    # 维保费率
    rate1 = MaintenanceRate(
        primary_category="服务器",
        secondary_category="机架式服务器",
        tertiary_category="标准机架式",
        rate=0.08,
    )
    rate2 = MaintenanceRate(
        primary_category="网络设备",
        secondary_category="交换机",
        tertiary_category="核心交换机",
        rate=0.05,
    )
    db.add_all([rate1, rate2])

    # 设备
    devices = [
        DeviceInventory(
            manufacturer="戴尔/DELL",
            model_number="PowerEdge R740",
            device_price=45000,
            primary_category="服务器",
            secondary_category="机架式服务器",
            tertiary_category="标准机架式",
            device_series="PowerEdge",
        ),
        DeviceInventory(
            manufacturer="戴尔/DELL",
            model_number="PowerEdge R750",
            device_price=58000,
            primary_category="服务器",
            secondary_category="机架式服务器",
            tertiary_category="标准机架式",
            device_series="PowerEdge",
        ),
        DeviceInventory(
            manufacturer="惠普&慧与/HP&HPE",
            model_number="ProLiant DL380 Gen10",
            device_price=42000,
            primary_category="服务器",
            secondary_category="机架式服务器",
            tertiary_category="标准机架式",
            device_series="ProLiant",
        ),
        DeviceInventory(
            manufacturer="华为/HUAWEI",
            model_number="CE6881-48S6CQ",
            device_price=35000,
            primary_category="网络设备",
            secondary_category="交换机",
            tertiary_category="核心交换机",
            device_series="CloudEngine",
        ),
    ]
    db.add_all(devices)
    db.flush()

    return {"devices": devices, "rates": [rate1, rate2]}
