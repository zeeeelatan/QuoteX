"""Tool Calling 运行时：多轮工具循环 + SSE 事件流。"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx
from sqlalchemy.orm import Session

from app.agent.config import MAX_TOOL_ROUNDS
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.session import AgentSession, store
from app.agent.tools import (
    execute_tool,
    tool_schemas,
    try_extract_bom_from_requirement,
)

logger = logging.getLogger(__name__)


def _sse(payload: Dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _dashscope_headers(api_key: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


async def _dashscope_chat_once(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    resp = await client.post(
        url, json=payload, headers=_dashscope_headers(api_key), timeout=180
    )
    if resp.status_code == 401:
        raise RuntimeError("百炼 API Key 无效或已过期")
    if resp.status_code >= 400:
        raise RuntimeError(f"百炼 API 错误 {resp.status_code}: {resp.text[:300]}")
    return resp.json()


async def _stream_dashscope_text(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, Any]],
) -> AsyncIterator[str]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {"model": model, "messages": messages, "stream": True}
    async with client.stream(
        "POST", url, json=payload, headers=_dashscope_headers(api_key)
    ) as resp:
        if resp.status_code != 200:
            body = await resp.aread()
            raise RuntimeError(f"百炼流式错误 {resp.status_code}: {body.decode()[:200]}")
        async for line in resp.aiter_lines():
            if not line.startswith("data:"):
                continue
            data_str = line[5:].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
                delta = (chunk.get("choices") or [{}])[0].get("delta", {})
                c = delta.get("content") or ""
                if c:
                    yield c
            except json.JSONDecodeError:
                continue


async def _ollama_chat(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    model: str,
    messages: List[Dict[str, Any]],
    stream: bool = False,
) -> Any:
    """Ollama 无完整 tools 时降级为纯对话（工具结果已注入 system）。"""
    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {"model": model, "messages": messages, "stream": stream}
    if stream:
        return client.stream("POST", url, json=payload)
    resp = await client.post(url, json=payload, timeout=180)
    resp.raise_for_status()
    return resp.json()


def _normalize_tool_calls(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    tool_calls = message.get("tool_calls") or []
    normalized = []
    for tc in tool_calls:
        fn = tc.get("function") or {}
        args_raw = fn.get("arguments") or "{}"
        if isinstance(args_raw, dict):
            args = args_raw
        else:
            try:
                args = json.loads(args_raw)
            except json.JSONDecodeError:
                args = {}
        normalized.append(
            {
                "id": tc.get("id") or f"call_{fn.get('name')}",
                "name": fn.get("name") or "",
                "arguments": args,
            }
        )
    return normalized


async def run_agent_stream(
    *,
    db: Session,
    session: AgentSession,
    user_text: str,
    history: Optional[List[Dict[str, str]]] = None,
    model: str,
    use_dashscope: bool,
    dashscope_base_url: str,
    dashscope_api_key: str,
    ollama_base_url: str,
    http_client: httpx.AsyncClient,
) -> AsyncIterator[str]:
    """
    SSE 事件：
    - {"content": "..."} 文本增量
    - {"tool_call": {"name": "...", "arguments": {...}}}
    - {"tool_result": {"name": "...", "ok": true}}
    - {"structured": {...}} 结构化报价
    - {"session_id": "..."}
    - {"done": true}
    - {"error": "..."}
    """
    yield _sse({"session_id": session.session_id})

    # 预提取自然语言 BOM，便于维保工具
    extracted = try_extract_bom_from_requirement(user_text)
    if extracted and not session.last_bom_items:
        session.last_bom_items = extracted

    tools = tool_schemas() if use_dashscope else None
    messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 注入精简历史
    for h in (history or [])[-12:]:
        role = h.get("role")
        content = (h.get("content") or "")[:2000]
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    # 附件提示
    file_note = ""
    if session.files:
        names = ", ".join(f.filename for f in session.files)
        file_note = f"\n\n【本轮附件】{names}（可用 parse_bom_from_files 解析）"

    if extracted:
        file_note += f"\n【从描述粗提取的设备】{json.dumps(extracted, ensure_ascii=False)}"

    messages.append({"role": "user", "content": (user_text or "（见附件）") + file_note})

    latest_structured: Optional[Dict[str, Any]] = None

    try:
        if use_dashscope:
            for _round in range(MAX_TOOL_ROUNDS):
                data = await _dashscope_chat_once(
                    http_client,
                    base_url=dashscope_base_url,
                    api_key=dashscope_api_key,
                    model=model,
                    messages=messages,
                    tools=tools,
                )
                choice = (data.get("choices") or [{}])[0]
                message = choice.get("message") or {}
                tool_calls = _normalize_tool_calls(message)

                if tool_calls:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": message.get("content") or None,
                            "tool_calls": message.get("tool_calls") or [
                                {
                                    "id": tc["id"],
                                    "type": "function",
                                    "function": {
                                        "name": tc["name"],
                                        "arguments": json.dumps(
                                            tc["arguments"], ensure_ascii=False
                                        ),
                                    },
                                }
                                for tc in tool_calls
                            ],
                        }
                    )
                    for tc in tool_calls:
                        yield _sse(
                            {
                                "tool_call": {
                                    "name": tc["name"],
                                    "arguments": tc["arguments"],
                                }
                            }
                        )
                        result = execute_tool(tc["name"], tc["arguments"], db, session)
                        store.save(session)
                        yield _sse(
                            {
                                "tool_result": {
                                    "name": tc["name"],
                                    "ok": bool(result.get("ok", True)),
                                    "summary": result.get("summary")
                                    or result.get("error")
                                    or result.get("message")
                                    or {"count": result.get("count")},
                                }
                            }
                        )
                        if result.get("structured"):
                            latest_structured = result["structured"]
                            yield _sse({"structured": latest_structured})
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "name": tc["name"],
                                "content": json.dumps(result, ensure_ascii=False)[:12000],
                            }
                        )
                    continue

                content = (message.get("content") or "").strip()
                if content:
                    chunk_size = 40
                    for i in range(0, len(content), chunk_size):
                        yield _sse({"content": content[i : i + chunk_size]})
                else:
                    async for c in _stream_dashscope_text(
                        http_client,
                        base_url=dashscope_base_url,
                        api_key=dashscope_api_key,
                        model=model,
                        messages=messages,
                    ):
                        yield _sse({"content": c})
                break
            else:
                yield _sse({"content": "工具调用轮次过多，已停止。请简化需求后重试。"})
        else:
            # Ollama 降级：无 tools，把可用工具说明 + 若有预提取 BOM 则直接跑维保
            if extracted or session.files:
                if session.files and not session.last_bom_items:
                    bom = execute_tool("parse_bom_from_files", {}, db, session)
                    yield _sse({"tool_result": {"name": "parse_bom_from_files", "ok": bom.get("ok")}})
                quote = execute_tool(
                    "create_maintenance_quote",
                    {"use_last_bom": True, "items": extracted or []},
                    db,
                    session,
                )
                if quote.get("structured"):
                    latest_structured = quote["structured"]
                    yield _sse({"structured": latest_structured})
                    yield _sse(
                        {
                            "content": (
                                f"已基于本地匹配生成维保报价草稿：共 {quote['summary']['line_count']} 行，"
                                f"合计 ¥{quote['summary']['total_base']}。"
                                + (
                                    "请确认匹配结果后再导出。"
                                    if latest_structured.get("requires_confirmation")
                                    else ""
                                )
                            )
                        }
                    )
                else:
                    # 纯对话
                    data = await _ollama_chat(
                        http_client,
                        base_url=ollama_base_url,
                        model=model,
                        messages=messages,
                        stream=False,
                    )
                    content = ((data.get("message") or {}).get("content") or "").strip()
                    if content:
                        yield _sse({"content": content})
            else:
                # 尝试产品搜索关键词
                kw = (user_text or "").strip()[:80]
                if kw:
                    search = execute_tool("search_products", {"keyword": kw, "limit": 10}, db, session)
                    yield _sse({"tool_result": {"name": "search_products", "ok": search.get("ok")}})
                    messages.append(
                        {
                            "role": "system",
                            "content": "工具 search_products 结果：\n"
                            + json.dumps(search, ensure_ascii=False)[:8000],
                        }
                    )
                data = await _ollama_chat(
                    http_client,
                    base_url=ollama_base_url,
                    model=model,
                    messages=messages,
                    stream=False,
                )
                content = ((data.get("message") or {}).get("content") or "").strip()
                if content:
                    yield _sse({"content": content})

        if latest_structured is None and session.pending_quote:
            latest_structured = session.pending_quote
            yield _sse({"structured": latest_structured})

        store.save(session)
        yield _sse({"done": True, "session_id": session.session_id})
    except Exception as e:
        logger.exception("agent stream 失败: %s", e)
        yield _sse({"error": str(e)})
        yield _sse({"done": True, "session_id": session.session_id})
