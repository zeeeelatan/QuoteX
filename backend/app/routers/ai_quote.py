"""
首页智能报价：调用本地 Ollama (Qwen) 分析用户需求与文档，结合系统后台数据（RAG）输出建议报价。
"""
import os
import io
import re
import logging
from typing import Optional, List
from decimal import Decimal

import requests
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from pydantic import BaseModel

from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-quote", tags=["AI报价"])

# RAG 拉取条数上限，避免上下文过长
RAG_RATES_LIMIT = 80
RAG_SERVICE_LEVELS_LIMIT = 30
RAG_DEVICES_LIMIT = 120
RAG_OFFICE_DEVICES_LIMIT = 80
RAG_GPU_LIMIT = 50
RAG_SPARE_PARTS_LIMIT = 50

OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_QUOTE_MODEL", "qwen:latest")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
MAX_FILE_COUNT = 5


def _extract_text_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        return f"[PDF 解析失败: {e}]"


def _extract_text_docx(content: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return f"[Word 解析失败: {e}]"


def _extract_text_xlsx(content: bytes) -> str:
    try:
        import pandas as pd
        df = pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)
        return df.to_string(index=False)
    except Exception as e:
        return f"[Excel 解析失败: {e}]"


def extract_text_from_file(filename: str, content: bytes) -> str:
    if len(content) > MAX_FILE_SIZE:
        return f"[文件过大，已跳过: {filename}]"
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_text_pdf(content)
    if lower.endswith(".docx"):
        return _extract_text_docx(content)
    if lower.endswith(".doc"):
        return "[.doc 格式请另存为 .docx 后上传]"
    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return _extract_text_xlsx(content)
    if lower.endswith(".txt"):
        return content.decode("utf-8", errors="replace")
    return f"[不支持的文件类型: {filename}]"


def _extract_keywords_for_rag(user_text: str) -> List[str]:
    """从用户描述中提取可能用于检索的关键词（品牌、型号等）。"""
    if not user_text or not user_text.strip():
        return []
    # 常见品牌/型号关键词（可扩展）
    known = ["戴尔", "DELL", "惠普", "HP", "HPE", "华为", "HUAWEI", "联想", "LENOVO",
             "浪潮", "INSPUR", "新华三", "H3C", "思科", "CISCO", "PowerEdge", "ProLiant",
             "服务器", "存储", "网络", "GPU", "备件"]
    text_upper = user_text.upper()
    text_lower = user_text.lower()
    found = []
    for k in known:
        if k.upper() in text_upper or k.lower() in text_lower or k in user_text:
            found.append(k)
    # 简单提取：连续中文字符段、连续英文/数字段（2字符以上）
    for m in re.finditer(r"[\u4e00-\u9fff]+", user_text):
        w = m.group().strip()
        if len(w) >= 2 and w not in found:
            found.append(w)
    for m in re.finditer(r"[A-Za-z0-9][A-Za-z0-9\-_/]{1,30}", user_text):
        w = m.group().strip()
        if w.upper() not in [x.upper() for x in found]:
            found.append(w)
    return list(dict.fromkeys(found))[:15]


def get_rag_context(db: Session, user_text: str) -> str:
    """
    从后台数据库拉取与报价相关的数据，拼成 RAG 上下文字符串。
    供大模型严格基于「后台数据」作答；缺失项需明确说明，推断需标注。
    """
    from app.models import DeviceInventory, MaintenanceRate
    from app.models.office_device_inventory import OfficeDeviceInventory
    from app.models.gpu_price import GPUPrice
    from app.models.spare_part import SparePart

    lines = ["## 后台数据（以下为系统真实数据，请严格据此作答）", ""]
    keywords = _extract_keywords_for_rag(user_text)

    # 1. 维保费率（按一级/二级/三级分类）
    try:
        rates = (
            db.query(MaintenanceRate)
            .order_by(
                MaintenanceRate.primary_category,
                MaintenanceRate.secondary_category,
                MaintenanceRate.tertiary_category,
            )
            .limit(RAG_RATES_LIMIT)
            .all()
        )
        if rates:
            lines.append("### 1. 维保费率（一级分类 / 二级分类 / 三级分类 → 费率）")
            lines.append("  （维保价格计算公式：设备价格 × 费率 × 1.06，即含 6% 加成）")
            for r in rates:
                rate_pct = float(r.rate) * 100 if r.rate is not None else 0
                lines.append(
                    f"  - {r.primary_category or ''} / {r.secondary_category or ''} / {r.tertiary_category or ''} → {rate_pct:.2f}%"
                )
            lines.append("")
        else:
            lines.append("### 1. 维保费率：后台暂无数据")
            lines.append("")
    except Exception as e:
        logger.warning("RAG 拉取维保费率失败: %s", e)
        lines.append("### 1. 维保费率：拉取失败")
        lines.append("")

    # 2. 服务级别（level_code, response_time, coefficient）
    try:
        rows = db.execute(
            text(
                "SELECT level_code, response_time, coefficient FROM service_level ORDER BY id LIMIT :n"
            ),
            {"n": RAG_SERVICE_LEVELS_LIMIT},
        ).fetchall()
        if rows:
            lines.append("### 2. 服务级别（级别代码 / 响应时效 / 系数）")
            for row in rows:
                lines.append(f"  - {row[0]} | {row[1]} | 系数 {row[2]}")
            lines.append("")
        else:
            lines.append("### 2. 服务级别：后台暂无数据")
            lines.append("")
    except Exception as e:
        logger.warning("RAG 拉取服务级别失败: %s", e)
        lines.append("### 2. 服务级别：拉取失败")
        lines.append("")

    # 3. 设备库（数据中心）：按关键词过滤或取样本
    try:
        q = db.query(DeviceInventory).order_by(DeviceInventory.id)
        if keywords:
            or_clauses = []
            for kw in keywords[:5]:
                or_clauses.append(DeviceInventory.manufacturer.ilike(f"%{kw}%"))
                or_clauses.append(DeviceInventory.model_number.ilike(f"%{kw}%"))
                or_clauses.append(DeviceInventory.primary_category.ilike(f"%{kw}%"))
            q = q.filter(or_(*or_clauses))
        devices = q.limit(RAG_DEVICES_LIMIT).all()
        if devices:
            lines.append("### 3. 设备库（数据中心）- 厂商 / 型号 / 一级分类 / 参考价格（元）")
            for d in devices:
                price = float(d.device_price) if d.device_price is not None else None
                price_str = f"{price:,.0f}" if price is not None else "无"
                lines.append(
                    f"  - {d.manufacturer or ''} | {d.model_number or ''} | {d.primary_category or ''} | {price_str}"
                )
            lines.append("")
        else:
            lines.append("### 3. 设备库（数据中心）：后台暂无匹配数据")
            lines.append("")
    except Exception as e:
        logger.warning("RAG 拉取设备库失败: %s", e)
        lines.append("### 3. 设备库（数据中心）：拉取失败")
        lines.append("")

    # 4. 设备库（办公）
    try:
        q = db.query(OfficeDeviceInventory).order_by(OfficeDeviceInventory.id)
        if keywords:
            or_clauses = []
            for kw in keywords[:5]:
                or_clauses.append(OfficeDeviceInventory.manufacturer.ilike(f"%{kw}%"))
                or_clauses.append(OfficeDeviceInventory.model_number.ilike(f"%{kw}%"))
                or_clauses.append(OfficeDeviceInventory.primary_category.ilike(f"%{kw}%"))
            q = q.filter(or_(*or_clauses))
        office = q.limit(RAG_OFFICE_DEVICES_LIMIT).all()
        if office:
            lines.append("### 4. 设备库（办公）- 厂商 / 型号 / 一级分类 / 参考价格（元）")
            for d in office:
                price = float(d.device_price) if d.device_price is not None else None
                price_str = f"{price:,.0f}" if price is not None else "无"
                lines.append(
                    f"  - {d.manufacturer or ''} | {d.model_number or ''} | {d.primary_category or ''} | {price_str}"
                )
            lines.append("")
        else:
            lines.append("### 4. 设备库（办公）：后台暂无匹配数据")
            lines.append("")
    except Exception as e:
        logger.warning("RAG 拉取办公设备库失败: %s", e)
        lines.append("### 4. 设备库（办公）：拉取失败")
        lines.append("")

    # 5. GPU 价格
    try:
        gpus = (
            db.query(GPUPrice)
            .order_by(GPUPrice.id)
            .limit(RAG_GPU_LIMIT)
            .all()
        )
        if gpus:
            lines.append("### 5. GPU 价格 - 厂商/系列/型号 | 单价(元) | 费率 | 维保服务费(元)")
            for g in gpus:
                price = float(g.gpu_price) if g.gpu_price is not None else None
                rate = float(g.gpu_rate) * 100 if g.gpu_rate is not None else None
                fee = float(g.service_fee) if g.service_fee is not None else None
                price_s = f"{price:,.0f}" if price is not None else "无"
                rate_s = f"{rate:.2f}%" if rate is not None else "无"
                fee_s = f"{fee:,.0f}" if fee is not None else "无"
                lines.append(
                    f"  - {g.manufacturer or ''} {g.series or ''} {g.model or ''} | {price_s} | {rate_s} | {fee_s}"
                )
            lines.append("")
        else:
            lines.append("### 5. GPU 价格：后台暂无数据")
            lines.append("")
    except Exception as e:
        logger.warning("RAG 拉取 GPU 价格失败: %s", e)
        lines.append("### 5. GPU 价格：拉取失败")
        lines.append("")

    # 6. 备件
    try:
        parts = (
            db.query(SparePart)
            .order_by(SparePart.id)
            .limit(RAG_SPARE_PARTS_LIMIT)
            .all()
        )
        if parts:
            lines.append("### 6. 备件 - 厂商 / 备件PN / 描述 / 分类 / 单价(元)")
            for p in parts:
                up = float(p.unit_price) if p.unit_price is not None else "无"
                up_s = f"{up:,.0f}" if isinstance(up, (int, float)) else str(up)
                lines.append(
                    f"  - {p.manufacturer or ''} | {p.part_pn or ''} | {p.part_desc or ''} | {p.part_category or ''} | {up_s}"
                )
            lines.append("")
        else:
            lines.append("### 6. 备件：后台暂无数据")
            lines.append("")
    except Exception as e:
        logger.warning("RAG 拉取备件失败: %s", e)
        lines.append("### 6. 备件：拉取失败")
        lines.append("")

    lines.append("---")
    lines.append("请仅根据以上「后台数据」给出报价建议；若某项在后台不存在，必须明确写出「后台数据中暂无该设备/品类/费率/服务级别」；若你使用自身推断或经验补充，请在该句前标注「【模型推断/经验建议】」。")
    return "\n".join(lines)


def call_ollama_chat(system: str, user_content: str, model: str = OLLAMA_MODEL) -> str:
    url = f"{OLLAMA_BASE.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        "stream": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code == 404:
            raise HTTPException(
                status_code=502,
                detail=f"模型「{model}」未安装或不存在。请在本机执行：ollama pull {model} 或 ollama pull qwen；也可设置环境变量 OLLAMA_QUOTE_MODEL 为已安装的模型名（如 qwen）。",
            )
        resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError as e:
            raise HTTPException(status_code=502, detail=f"大模型返回非 JSON: {e}")
        msg = data.get("message") or {}
        return (msg.get("content") or "").strip()
    except HTTPException:
        raise
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="无法连接本地大模型服务。请确认 Ollama 已启动（如未安装请访问 https://ollama.com），并已拉取模型：ollama pull qwen2.5 或 ollama pull qwen。",
        )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="大模型响应超时")
    except requests.exceptions.RequestException as e:
        err_msg = str(e)
        if "404" in err_msg:
            raise HTTPException(
                status_code=502,
                detail=f"模型「{model}」未安装。请执行：ollama pull {model} 或 ollama pull qwen；或设置 OLLAMA_QUOTE_MODEL 为已安装的模型名。",
            )
        raise HTTPException(status_code=502, detail=f"调用大模型失败: {err_msg}")


SYSTEM_PROMPT_TEMPLATE = """你是智能报价助手，必须**严格基于系统后台数据**作答。

规则：
1. 下方会提供「后台数据」区块，包含：维保费率、服务级别、设备库（数据中心/办公）、GPU 价格、备件等。报价中的费率、服务级别系数、设备型号与参考价格等**必须以该后台数据为准**。
2. 若用户需求中的设备、品类、服务级别或费率在后台数据中**不存在**，你必须明确写出：「**后台数据中暂无该设备/品类/费率/服务级别**」，不得编造具体数值。
3. 若你基于常识或经验给出补充说明（如维保周期、响应方式等非价格建议），必须在该句或该段前标注：「**【模型推断/经验建议】**」，以区分于后台数据。
4. 回复使用中文，条理清晰；先归纳需求，再基于后台数据列出可用的费率/设备/服务级别与报价建议，最后可附模型推断类说明。便于后续生成正式报价单。

---
{rag_context}
"""


class AnalyzeResponse(BaseModel):
    analysis: str
    suggestion: Optional[str] = None


class ModelsResponse(BaseModel):
    models: List[str]


@router.get("/models", response_model=ModelsResponse)
def list_ollama_models():
    """获取本地 Ollama 可用模型列表，供前端模型选择。"""
    url = f"{OLLAMA_BASE.rstrip('/')}/api/tags"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return ModelsResponse(models=[OLLAMA_MODEL])
        data = resp.json()
        names = []
        for m in data.get("models") or []:
            name = (m.get("name") or "").strip()
            if name and ":" in name:
                names.append(name)
            elif name:
                names.append(name)
        if not names:
            names = [OLLAMA_MODEL]
        return ModelsResponse(models=names)
    except Exception as e:
        logger.warning("拉取 Ollama 模型列表失败: %s", e)
        return ModelsResponse(models=[OLLAMA_MODEL])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_requirement(request: Request, db: Session = Depends(get_db)):
    """分析用户需求与上传文档，调用本地 Ollama (Qwen) 生成报价建议。手动解析 multipart 避免无 files 时 500。"""
    try:
        content_type = request.headers.get("content-type") or ""
        if "multipart/form-data" not in content_type:
            raise HTTPException(status_code=400, detail="请使用 multipart/form-data 提交")

        form = await request.form()
        requirement = (form.get("requirement") or "").strip()
        model_name = (form.get("model") or "").strip() or OLLAMA_MODEL
        # 无 files 时 form.getlist("files") 为 []，不会报错
        file_list = form.getlist("files")
        if not isinstance(file_list, list):
            file_list = [file_list] if file_list else []
        # 过滤掉空值（部分框架会传空字符串）
        file_list = [f for f in file_list if hasattr(f, "read") and hasattr(f, "filename")]

        if not requirement and not file_list:
            raise HTTPException(status_code=400, detail="请输入需求描述或上传需求文档")

        # 构建用户内容：需求 + 文档提取文本
        parts = []
        if requirement.strip():
            parts.append("【用户描述】\n" + requirement.strip())

        if len(file_list) > MAX_FILE_COUNT:
            raise HTTPException(status_code=400, detail=f"最多上传 {MAX_FILE_COUNT} 个文件")

        for f in file_list:
            content = await f.read() if hasattr(f, "read") else b""
            filename = getattr(f, "filename", None) or "file"
            text = extract_text_from_file(filename, content)
            if text and not text.startswith("["):
                parts.append(f"【文档: {filename}】\n" + text[:30000])
            elif text.startswith("["):
                parts.append(text)

        user_content = "\n\n".join(parts) if parts else "（无文字内容）"

        # RAG：拉取后台数据并注入系统提示，使模型严格基于后台数据作答
        rag_context = get_rag_context(db, requirement)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(rag_context=rag_context)

        analysis = call_ollama_chat(system_prompt, user_content, model=model_name)
        return AnalyzeResponse(analysis=analysis, suggestion=analysis)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("ai-quote/analyze 失败: %s", e)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")
