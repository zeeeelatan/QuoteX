"""
首页专用智能体：DashScope Tool Calling（或 Ollama 降级），
编排产品查询 / 维保 / 联想 / 驻场 / 搬迁等确定性后端能力。
"""
from __future__ import annotations

import os
import json
import logging
from typing import Optional, List, Any, Dict

import httpx
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.agent.session import store, UploadedFile
from app.agent.runtime import run_agent_stream
from app.agent.tools import execute_tool
from app.agent.config import REQUIRE_MATCH_CONFIRMATION

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-quote", tags=["AI报价"])

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_QUOTE_MODEL", "qwen:latest")

MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_FILE_COUNT = 5

_http_client: Optional[httpx.AsyncClient] = None


async def _get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10, read=180, write=10, pool=10)
        )
    return _http_client


def _use_dashscope() -> bool:
    return bool(DASHSCOPE_API_KEY)


def extract_text_from_file(filename: str, content: bytes) -> str:
    if len(content) > MAX_FILE_SIZE:
        return f"[文件过大，已跳过: {filename}]"
    lower = filename.lower()
    try:
        if lower.endswith(".pdf"):
            from pypdf import PdfReader
            import io

            reader = PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if lower.endswith(".docx"):
            from docx import Document
            import io

            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        if lower.endswith(".doc"):
            return "[.doc 格式请另存为 .docx 后上传]"
        if lower.endswith(".xlsx") or lower.endswith(".xls"):
            import pandas as pd
            import io

            df = pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)
            return df.to_string(index=False)
        if lower.endswith(".txt"):
            return content.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[解析失败: {e}]"
    return f"[不支持的文件类型: {filename}]"


class AnalyzeResponse(BaseModel):
    analysis: str
    suggestion: Optional[str] = None
    session_id: Optional[str] = None
    structured: Optional[Dict[str, Any]] = None


class ModelsResponse(BaseModel):
    models: List[str]


class ConfirmRequest(BaseModel):
    session_id: str


class ConfirmResponse(BaseModel):
    ok: bool
    message: str
    structured: Optional[Dict[str, Any]] = None


@router.get("/models", response_model=ModelsResponse)
async def list_available_models():
    if _use_dashscope():
        return ModelsResponse(models=["qwen-plus", "qwen-turbo", "qwen-max"])
    url = f"{OLLAMA_BASE.rstrip('/')}/api/tags"
    client = await _get_http_client()
    try:
        resp = await client.get(url, timeout=5)
        if resp.status_code != 200:
            return ModelsResponse(models=[OLLAMA_MODEL])
        data = resp.json()
        names = [
            m.get("name", "").strip()
            for m in (data.get("models") or [])
            if m.get("name")
        ]
        return ModelsResponse(models=names or [OLLAMA_MODEL])
    except Exception as e:
        logger.warning("拉取模型列表失败: %s", e)
        return ModelsResponse(models=[OLLAMA_MODEL])


@router.get("/policy")
async def agent_policy():
    """前端可读的智能体策略（计划默认值）。"""
    return {
        "require_match_confirmation": REQUIRE_MATCH_CONFIRMATION,
        "forbid_invented_prices": True,
        "supported_quote_types": [
            "product_query",
            "maintenance",
            "lenovo",
            "onsite",
            "relocation",
        ],
        "export_formats": ["excel", "pdf"],
        "model_provider": "dashscope" if _use_dashscope() else "ollama",
        "default_model": DASHSCOPE_MODEL if _use_dashscope() else OLLAMA_MODEL,
    }


async def _parse_agent_form(request: Request):
    content_type = request.headers.get("content-type") or ""
    if "multipart/form-data" not in content_type:
        raise HTTPException(status_code=400, detail="请使用 multipart/form-data 提交")

    form = await request.form()
    requirement = (form.get("requirement") or "").strip()
    model_name = (form.get("model") or "").strip()
    session_id = (form.get("session_id") or "").strip() or None
    history_raw = form.get("history")
    history: List[Dict[str, str]] = []
    if history_raw:
        try:
            parsed = json.loads(str(history_raw))
            if isinstance(parsed, list):
                history = [
                    {"role": m.get("role", "user"), "content": str(m.get("content") or "")}
                    for m in parsed
                    if isinstance(m, dict)
                ]
        except json.JSONDecodeError:
            history = []

    file_list = form.getlist("files")
    if not isinstance(file_list, list):
        file_list = [file_list] if file_list else []
    file_list = [f for f in file_list if hasattr(f, "read") and hasattr(f, "filename")]

    if not requirement and not file_list:
        raise HTTPException(status_code=400, detail="请输入需求描述或上传需求文档")
    if len(file_list) > MAX_FILE_COUNT:
        raise HTTPException(status_code=400, detail=f"最多上传 {MAX_FILE_COUNT} 个文件")

    uploads: List[UploadedFile] = []
    for f in file_list:
        content = await f.read()
        filename = getattr(f, "filename", None) or "file"
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"文件过大: {filename}")
        text_preview = extract_text_from_file(filename, content)[:30000]
        uploads.append(
            UploadedFile(filename=filename, content=content, text_preview=text_preview)
        )

    if _use_dashscope():
        effective_model = model_name if model_name and model_name != OLLAMA_MODEL else DASHSCOPE_MODEL
    else:
        effective_model = model_name or OLLAMA_MODEL

    return requirement, effective_model, session_id, history, uploads


@router.post("/analyze-stream")
async def analyze_requirement_stream(request: Request, db: Session = Depends(get_db)):
    """专用智能体流式端点（SSE）。"""
    try:
        requirement, model_name, session_id, history, uploads = await _parse_agent_form(
            request
        )
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

    session = store.get_or_create(session_id)
    if uploads:
        session.files = uploads
        store.save(session)

    client = await _get_http_client()

    async def event_generator():
        async for chunk in run_agent_stream(
            db=db,
            session=session,
            user_text=requirement,
            history=history,
            model=model_name,
            use_dashscope=_use_dashscope(),
            dashscope_base_url=DASHSCOPE_BASE_URL,
            dashscope_api_key=DASHSCOPE_API_KEY,
            ollama_base_url=OLLAMA_BASE,
            http_client=client,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_requirement(request: Request, db: Session = Depends(get_db)):
    """非流式兼容：聚合 SSE 结果。"""
    try:
        requirement, model_name, session_id, history, uploads = await _parse_agent_form(
            request
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    session = store.get_or_create(session_id)
    if uploads:
        session.files = uploads
        store.save(session)

    client = await _get_http_client()
    parts: List[str] = []
    structured = None
    sid = session.session_id
    async for raw in run_agent_stream(
        db=db,
        session=session,
        user_text=requirement,
        history=history,
        model=model_name,
        use_dashscope=_use_dashscope(),
        dashscope_base_url=DASHSCOPE_BASE_URL,
        dashscope_api_key=DASHSCOPE_API_KEY,
        ollama_base_url=OLLAMA_BASE,
        http_client=client,
    ):
        if not raw.startswith("data:"):
            continue
        try:
            payload = json.loads(raw[5:].strip())
        except json.JSONDecodeError:
            continue
        if payload.get("content"):
            parts.append(payload["content"])
        if payload.get("structured"):
            structured = payload["structured"]
        if payload.get("session_id"):
            sid = payload["session_id"]
        if payload.get("error"):
            raise HTTPException(status_code=502, detail=payload["error"])

    analysis = "".join(parts) or "未返回分析内容"
    return AnalyzeResponse(
        analysis=analysis,
        suggestion=analysis,
        session_id=sid,
        structured=structured,
    )


@router.post("/confirm", response_model=ConfirmResponse)
async def confirm_quote(body: ConfirmRequest, db: Session = Depends(get_db)):
    """用户确认待导出报价。"""
    session = store.get(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")
    result = execute_tool("confirm_pending_quote", {}, db, session)
    store.save(session)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error") or "确认失败")
    return ConfirmResponse(
        ok=True,
        message=result.get("message") or "已确认",
        structured=result.get("structured"),
    )


@router.get("/session/{session_id}")
async def get_session_state(session_id: str):
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")
    return {
        "session_id": session.session_id,
        "quote_type": session.quote_type,
        "pending_quote": session.pending_quote,
        "confirmed_quote": session.confirmed_quote,
        "slots": session.slots,
        "file_names": [f.filename for f in session.files],
    }
