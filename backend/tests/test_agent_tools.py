"""专用智能体工具层单测（不依赖大模型 API）。"""
import io

import pandas as pd

from app.agent.session import AgentSession
from app.agent.tools import (
    execute_tool,
    try_extract_bom_from_requirement,
    _parse_excel_bom,
)
from app.agent.config import REQUIRE_MATCH_CONFIRMATION


def test_extract_bom_from_natural_language():
    text = "50台戴尔 PowerEdge R740\n联想 ThinkSystem SR650 x10"
    items = try_extract_bom_from_requirement(text)
    assert len(items) >= 1
    assert any("R740" in (i.get("model") or "") for i in items)


def test_parse_excel_bom_columns():
    df = pd.DataFrame(
        [
            {"厂商": "戴尔", "型号": "PowerEdge R740", "数量": 2},
            {"厂商": "华为", "型号": "2288H V5", "数量": 1},
        ]
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    items = _parse_excel_bom(buf.getvalue())
    assert len(items) == 2
    assert items[0]["model"] == "PowerEdge R740"
    assert items[0]["quantity"] == 2


def test_describe_quote_type_catalog(db):
    session = AgentSession(session_id="t1")
    result = execute_tool("describe_quote_type", {}, db=db, session=session)
    assert result["ok"] is True
    assert "catalog" in result


def test_maintenance_quote_and_confirm(db, seed_devices):
    session = AgentSession(session_id="t-maint")
    result = execute_tool(
        "create_maintenance_quote",
        {
            "items": [
                {"manufacturer": "戴尔", "model": "PowerEdge R740", "quantity": 2},
            ]
        },
        db,
        session,
    )
    assert result["ok"] is True
    structured = result["structured"]
    assert structured["quote_type"] == "maintenance"
    assert structured["devices"]
    assert "total_base" in structured
    if REQUIRE_MATCH_CONFIRMATION:
        assert structured["confirmed"] is False
        confirm = execute_tool("confirm_pending_quote", {}, db, session)
        assert confirm["ok"] is True
        assert confirm["structured"]["confirmed"] is True


def test_search_products(db, seed_devices):
    session = AgentSession(session_id="t-search")
    result = execute_tool(
        "search_products",
        {"keyword": "R740", "limit": 5},
        db,
        session,
    )
    assert result["ok"] is True
    assert result["count"] >= 1


def test_policy_endpoint(client):
    resp = client.get("/ai-quote/policy")
    assert resp.status_code == 200
    data = resp.json()
    assert "require_match_confirmation" in data
    assert "maintenance" in data["supported_quote_types"]
