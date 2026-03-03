"""API CRUD 接口基础测试"""
import pytest


class TestMaintenanceRateAPI:
    """维保费率 CRUD 接口"""

    def test_list_maintenance_rates(self, client):
        response = client.get("/maintenance_rates/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_maintenance_rate(self, client):
        payload = {
            "primary_category": "测试分类",
            "secondary_category": "测试二级",
            "tertiary_category": "测试三级",
            "rate": 0.05,
        }
        response = client.post("/maintenance_rates/", json=payload)
        # 接受 200 或 201
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["primary_category"] == "测试分类"
        assert float(data["rate"]) == 0.05


class TestServiceLevelAPI:
    """服务等级接口"""

    def test_list_service_levels(self, client):
        response = client.get("/service-level/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestDeviceSearchAPI:
    """设备搜索接口"""

    def test_search_empty_query(self, client):
        response = client.get("/devices/search/?model=&source=datacenter")
        assert response.status_code == 200

    def test_search_with_model(self, client, seed_devices):
        response = client.get("/devices/search/?model=R740&source=datacenter")
        assert response.status_code == 200


class TestBulkMatchAPI:
    """批量匹配接口"""

    def test_bulk_match(self, client, seed_devices):
        payload = [
            {
                "manufacturer": "dell",
                "model": "PowerEdge R740",
                "source": "datacenter",
            }
        ]
        response = client.post("/bulk-match/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
