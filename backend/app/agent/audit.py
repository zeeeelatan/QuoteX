"""智能体工具调用审计（轻量日志，便于合规与效果分析）。"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("app.agent.audit")


def log_tool_call(
    *,
    session_id: str,
    tool_name: str,
    arguments: Dict[str, Any],
    result: Dict[str, Any],
    user_role: Optional[str] = None,
) -> None:
    """记录工具调用；不落库，依赖集中式日志采集。"""
    summary = {
        "ts": int(time.time()),
        "session_id": session_id,
        "tool": tool_name,
        "ok": bool(result.get("ok", True)),
        "user_role": user_role or "unknown",
        "arg_keys": sorted(list((arguments or {}).keys())),
        "error": result.get("error"),
        "ui_action": result.get("ui_action"),
        "quote_type": (result.get("structured") or {}).get("quote_type"),
    }
    logger.info("agent_tool %s", json.dumps(summary, ensure_ascii=False))
