"""健康检查接口测试"""


def test_health_endpoint(client):
    """GET /health 应返回 200 和 ok 状态"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
