"""智能体工具定义与执行（价格/匹配一律走后端确定性逻辑）。"""
from __future__ import annotations

import io
import json
import logging
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.agent.audit import log_tool_call
from app.agent.config import LOW_MATCH_RATE_THRESHOLD, REQUIRE_MATCH_CONFIRMATION
from app.agent.prompts import QUOTE_TYPE_CATALOG
from app.agent.session import AgentSession, UploadedFile
from app import matching

logger = logging.getLogger(__name__)


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj


def tool_schemas() -> List[Dict[str, Any]]:
    """OpenAI/DashScope function tools 列表。"""
    return [
        {
            "type": "function",
            "function": {
                "name": "search_products",
                "description": "在产品设备库中按型号/关键词查询设备（厂商、型号、分类、参考价）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "型号或关键词"},
                        "source": {
                            "type": "string",
                            "enum": ["datacenter", "office", "hybrid"],
                            "description": "数据源场景，默认 hybrid",
                        },
                        "limit": {"type": "integer", "description": "返回条数，默认 20"},
                    },
                    "required": ["keyword"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_service_levels",
                "description": "列出系统服务级别（级别代码、响应时效、系数）。",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "describe_quote_type",
                "description": "说明某类报价的适用场景、必填字段、是否可在对话内完成。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "quote_type": {
                            "type": "string",
                            "description": "maintenance/lenovo/onsite/relocation/itsupport/... 或中文名",
                        }
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "parse_bom_from_files",
                "description": "从当前会话已上传的附件中解析设备 BOM（厂商/型号/数量）。支持 Excel；其它格式返回文本线索。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_rows": {"type": "integer", "description": "最多解析行数，默认 200"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "match_devices",
                "description": "批量匹配设备到系统库，返回匹配型号、匹配率、设备价、维保单价（不含服务级别系数）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "manufacturer": {"type": "string"},
                                    "model": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "category": {"type": "string"},
                                    "source": {"type": "string"},
                                },
                                "required": ["model"],
                            },
                        }
                    },
                    "required": ["items"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_maintenance_quote",
                "description": "基于设备清单生成维保结构化报价（会写入会话待确认状态）。勿编造价格。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "manufacturer": {"type": "string"},
                                    "model": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "source": {"type": "string"},
                                },
                                "required": ["model"],
                            },
                        },
                        "service_level_code": {
                            "type": "string",
                            "description": "可选服务级别代码，如 7x24",
                        },
                        "use_last_bom": {
                            "type": "boolean",
                            "description": "若为 true 且未传 items，使用上次解析的 BOM",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "confirm_pending_quote",
                "description": "用户确认当前待确认报价后调用，解锁导出。",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "lenovo_quote",
                "description": "联想框架口径单条或批量报价。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "device_category": {"type": "string"},
                                    "brand": {"type": "string"},
                                    "model": {"type": "string"},
                                    "sla": {"type": "string"},
                                    "quantity": {"type": "integer"},
                                    "alias_key": {"type": "string"},
                                },
                                "required": ["device_category", "model", "sla"],
                            },
                        }
                    },
                    "required": ["items"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_job_positions",
                "description": "检索驻场岗位职级列表。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"},
                        "limit": {"type": "integer"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "query_city_social",
                "description": "查询城市社保公积金基数/比例摘要。",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "onsite_quote_estimate",
                "description": "驻场服务粗算：岗位薪资×人数×月数，附加社保雇主成本摘要（若有城市数据）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "position_id": {"type": "integer"},
                        "position_keyword": {"type": "string", "description": "无 position_id 时按关键词找岗位"},
                        "headcount": {"type": "integer"},
                        "months": {"type": "number"},
                    },
                    "required": ["city", "headcount", "months"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_relocation_vehicles",
                "description": "列出搬迁车辆类型与参考单价。",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "relocation_quote_estimate",
                "description": "搬迁服务粗算：按车辆单价×数量（趟次）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vehicle_keyword": {"type": "string"},
                        "quantity": {"type": "number"},
                        "city": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["vehicle_keyword", "quantity"],
                },
            },
        },
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MFR_KEYS = ("厂商", "品牌", "manufacturer", "brand", "厂家", "制造商")
_MODEL_KEYS = ("型号", "model", "设备型号", "产品型号", "机型", "model_number")
_QTY_KEYS = ("数量", "qty", "quantity", "台数", "套数", "数量（台）")


def _pick_col(headers: List[str], keys: tuple) -> Optional[str]:
    lower_map = {str(h).strip().lower(): h for h in headers if h is not None}
    for k in keys:
        for hk, orig in lower_map.items():
            if k.lower() in hk or hk == k.lower():
                return orig
    return None


def _parse_excel_bom(content: bytes, max_rows: int = 200) -> List[Dict[str, Any]]:
    import pandas as pd

    xls = pd.ExcelFile(io.BytesIO(content))
    items: List[Dict[str, Any]] = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=0)
        if df.empty:
            continue
        headers = [str(c) for c in df.columns.tolist()]
        mfr_col = _pick_col(headers, _MFR_KEYS)
        model_col = _pick_col(headers, _MODEL_KEYS)
        qty_col = _pick_col(headers, _QTY_KEYS)
        if not model_col:
            # 尝试无表头：第一列型号
            continue
        for _, row in df.head(max_rows).iterrows():
            model = str(row.get(model_col) or "").strip()
            if not model or model.lower() == "nan":
                continue
            mfr = str(row.get(mfr_col) or "").strip() if mfr_col else ""
            if mfr.lower() == "nan":
                mfr = ""
            qty = 1
            if qty_col:
                try:
                    qty = float(row.get(qty_col) or 1)
                except (TypeError, ValueError):
                    qty = 1
            items.append({"manufacturer": mfr, "model": model, "quantity": qty, "sheet": sheet})
        if items:
            break
    return items


def _extract_devices_from_text(text: str) -> List[Dict[str, Any]]:
    """从自然语言中粗提取「数量+品牌+型号」行。"""
    items: List[Dict[str, Any]] = []
    # 例：50台戴尔 PowerEdge R740 / 戴尔 PowerEdge R740 x50
    patterns = [
        r"(\d+)\s*台?\s*([A-Za-z\u4e00-\u9fff]+)\s+([A-Za-z0-9][A-Za-z0-9\-_/ ]{2,40})",
        r"([A-Za-z\u4e00-\u9fff]+)\s+([A-Za-z0-9][A-Za-z0-9\-_/]{2,40})\s*[x×\*]\s*(\d+)",
    ]
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.search(patterns[0], line)
        if m:
            items.append(
                {
                    "manufacturer": m.group(2).strip(),
                    "model": m.group(3).strip(),
                    "quantity": float(m.group(1)),
                }
            )
            continue
        m = re.search(patterns[1], line, re.I)
        if m:
            items.append(
                {
                    "manufacturer": m.group(1).strip(),
                    "model": m.group(2).strip(),
                    "quantity": float(m.group(3)),
                }
            )
    return items


def _get_service_level(db: Session, code: Optional[str]) -> Optional[Dict[str, Any]]:
    if not code:
        return None
    try:
        row = db.execute(
            text(
                "SELECT level_code, response_time, coefficient FROM service_level "
                "WHERE level_code ILIKE :c LIMIT 1"
            ),
            {"c": code},
        ).fetchone()
        if not row:
            row = db.execute(
                text(
                    "SELECT level_code, response_time, coefficient FROM service_level "
                    "WHERE CAST(level_code AS TEXT) ILIKE :c LIMIT 1"
                ),
                {"c": f"%{code}%"},
            ).fetchone()
        if row:
            return {
                "level_code": row[0],
                "response_time": row[1],
                "coefficient": float(row[2]) if row[2] is not None else 1.0,
            }
    except Exception as e:
        logger.warning("查询服务级别失败: %s", e)
    return None


def _build_maintenance_structured(
    matched_rows: List[Dict[str, Any]],
    service_level: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    devices = []
    total_base = 0.0
    unmatched = 0
    low_confidence = 0
    for r in matched_rows:
        qty = float(r.get("quantity") or 1)
        unit = float(r.get("price") or 0)
        subtotal = round(unit * qty, 2)
        total_base += subtotal
        mr = float(r.get("match_rate") or 0)
        if not r.get("matched_model"):
            unmatched += 1
        if mr and mr < LOW_MATCH_RATE_THRESHOLD:
            low_confidence += 1
        devices.append(
            {
                "manufacturer": r.get("manufacturer") or r.get("input_manufacturer") or "",
                "matched_model": r.get("matched_model"),
                "input_model": r.get("input_model"),
                "match_rate": mr,
                "device_price": r.get("device_price"),
                "rate": r.get("rate"),
                "price": unit,
                "quantity": qty,
                "subtotal": subtotal,
                "primary_category": r.get("primary_category"),
                "secondary_category": r.get("secondary_category"),
                "tertiary_category": r.get("tertiary_category"),
                "low_confidence": bool(mr and mr < LOW_MATCH_RATE_THRESHOLD),
                "unmatched": not bool(r.get("matched_model")),
            }
        )
    coef = float(service_level["coefficient"]) if service_level else 1.0
    total_adjusted = round(total_base * coef, 2)
    return {
        "quote_type": "maintenance",
        "caliber": "standard",
        "devices": devices,
        "total_base": round(total_base, 2),
        "total_adjusted": total_adjusted,
        "matched_service_level": service_level,
        "unmatched_count": unmatched,
        "low_confidence_count": low_confidence,
        "requires_confirmation": REQUIRE_MATCH_CONFIRMATION,
        "confirmed": False if REQUIRE_MATCH_CONFIRMATION else True,
        "export_formats": ["excel", "pdf"],
        "pricing_note": "维保单价 = 设备价格 × 费率 × 1.06；总价可乘服务级别系数",
    }


# ---------------------------------------------------------------------------
# Tool executors
# ---------------------------------------------------------------------------

def execute_tool(
    name: str,
    arguments: Dict[str, Any],
    db: Session,
    session: AgentSession,
    user_role: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        fn = TOOL_HANDLERS.get(name)
        if not fn:
            result = {"ok": False, "error": f"未知工具: {name}"}
        else:
            result = _json_safe(fn(arguments or {}, db, session))
        log_tool_call(
            session_id=session.session_id,
            tool_name=name,
            arguments=arguments or {},
            result=result if isinstance(result, dict) else {"ok": True},
            user_role=user_role,
        )
        return result if isinstance(result, dict) else {"ok": True, "data": result}
    except Exception as e:
        logger.exception("工具执行失败 %s: %s", name, e)
        err = {"ok": False, "error": str(e)}
        try:
            log_tool_call(
                session_id=session.session_id,
                tool_name=name,
                arguments=arguments or {},
                result=err,
                user_role=user_role,
            )
        except Exception:
            pass
        return err


def _search_products(args: Dict, db: Session, session: AgentSession) -> Dict:
    from app.models import DeviceInventory

    keyword = (args.get("keyword") or "").strip()
    source = args.get("source") or "hybrid"
    limit = int(args.get("limit") or 20)
    limit = max(1, min(limit, 50))
    if not keyword:
        return {"ok": False, "error": "keyword 不能为空"}

    q = db.query(DeviceInventory)
    if source == "datacenter":
        q = q.filter(
            or_(
                DeviceInventory.business_scenario.is_(None),
                DeviceInventory.business_scenario == "",
                ~DeviceInventory.business_scenario.ilike("%办公%"),
            )
        )
    elif source == "office":
        q = q.filter(DeviceInventory.business_scenario.ilike("%办公%"))

    q = q.filter(
        or_(
            DeviceInventory.model_number.ilike(f"%{keyword}%"),
            DeviceInventory.manufacturer.ilike(f"%{keyword}%"),
            DeviceInventory.manufacturer_name.ilike(f"%{keyword}%"),
            DeviceInventory.primary_category.ilike(f"%{keyword}%"),
        )
    )
    total = q.count()
    rows = q.limit(limit).all()
    data = []
    for d in rows:
        price = float(d.device_price) if d.device_price is not None else None
        data.append(
            {
                "manufacturer": d.manufacturer_name or d.manufacturer,
                "model": d.model_number,
                "primary_category": d.primary_category,
                "device_price": price,
                "business_scenario": d.business_scenario or "数据中心",
            }
        )
    session.quote_type = "product_query"
    return {"ok": True, "total": total, "count": len(data), "items": data}


def _list_service_levels(args: Dict, db: Session, session: AgentSession) -> Dict:
    try:
        rows = db.execute(
            text(
                "SELECT level_code, response_time, coefficient FROM service_level ORDER BY id LIMIT 50"
            )
        ).fetchall()
        items = [
            {
                "level_code": r[0],
                "response_time": r[1],
                "coefficient": float(r[2]) if r[2] is not None else 1.0,
            }
            for r in rows
        ]
        return {"ok": True, "items": items}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _describe_quote_type(args: Dict, db: Session, session: AgentSession) -> Dict:
    q = (args.get("quote_type") or "").strip().lower()
    if not q:
        return {"ok": True, "catalog": QUOTE_TYPE_CATALOG}
    for item in QUOTE_TYPE_CATALOG:
        if q == item["id"] or q in item["name"].lower() or item["name"] in (args.get("quote_type") or ""):
            return {"ok": True, "type": item}
    return {
        "ok": True,
        "message": "未精确匹配类型，返回完整目录",
        "catalog": QUOTE_TYPE_CATALOG,
    }


def _parse_bom_from_files(args: Dict, db: Session, session: AgentSession) -> Dict:
    max_rows = int(args.get("max_rows") or 200)
    if not session.files:
        return {"ok": False, "error": "当前会话没有上传附件，请先上传 Excel/文档"}
    all_items: List[Dict[str, Any]] = []
    notes: List[str] = []
    for f in session.files:
        lower = f.filename.lower()
        if lower.endswith((".xlsx", ".xls")):
            try:
                items = _parse_excel_bom(f.content, max_rows=max_rows)
                all_items.extend(items)
                notes.append(f"{f.filename}: 解析 {len(items)} 行")
            except Exception as e:
                notes.append(f"{f.filename}: Excel 解析失败 {e}")
        else:
            # 文本线索
            preview = f.text_preview or ""
            extracted = _extract_devices_from_text(preview)
            all_items.extend(extracted)
            notes.append(f"{f.filename}: 非表格附件，文本粗提取 {len(extracted)} 项")
    session.last_bom_items = all_items
    return {
        "ok": True,
        "count": len(all_items),
        "items": all_items[:max_rows],
        "notes": notes,
        "hint": "请调用 create_maintenance_quote 或 match_devices 继续",
    }


def _match_devices(args: Dict, db: Session, session: AgentSession) -> Dict:
    items = args.get("items") or []
    results = []
    for it in items:
        model = (it.get("model") or "").strip()
        if not model:
            continue
        mfr = (it.get("manufacturer") or "").strip()
        source = it.get("source") or "hybrid"
        m = matching.match_device(
            db,
            manufacturer=mfr,
            model=model,
            category=it.get("category"),
            source=source,
        )
        m["input_manufacturer"] = mfr
        m["input_model"] = model
        m["quantity"] = float(it.get("quantity") or 1)
        m["low_confidence"] = bool(
            m.get("matched_model")
            and float(m.get("match_rate") or 0) < LOW_MATCH_RATE_THRESHOLD
        )
        m["unmatched"] = not bool(m.get("matched_model"))
        results.append(m)
    return {"ok": True, "count": len(results), "results": results}


def _create_maintenance_quote(args: Dict, db: Session, session: AgentSession) -> Dict:
    items = args.get("items") or []
    if (not items) and args.get("use_last_bom") and session.last_bom_items:
        items = session.last_bom_items
    if not items:
        # 尝试从最近用户消息粗提取（由 runtime 也可预填 last_bom）
        return {
            "ok": False,
            "error": "缺少设备清单。请提供 items，或先 parse_bom_from_files / 在需求中列出型号。",
        }

    matched_rows = []
    for it in items:
        model = (it.get("model") or "").strip()
        if not model:
            continue
        mfr = (it.get("manufacturer") or "").strip()
        source = it.get("source") or "hybrid"
        m = matching.match_device(db, manufacturer=mfr, model=model, source=source)
        matched_rows.append(
            {
                **m,
                "input_manufacturer": mfr,
                "input_model": model,
                "quantity": float(it.get("quantity") or 1),
            }
        )

    sla = _get_service_level(db, args.get("service_level_code"))
    structured = _build_maintenance_structured(matched_rows, sla)
    session.quote_type = "maintenance"
    session.pending_quote = structured
    session.confirmed_quote = None if REQUIRE_MATCH_CONFIRMATION else structured
    session.last_bom_items = [
        {
            "manufacturer": r.get("input_manufacturer"),
            "model": r.get("input_model"),
            "quantity": r.get("quantity"),
        }
        for r in matched_rows
    ]
    return {
        "ok": True,
        "structured": structured,
        "summary": {
            "line_count": len(structured["devices"]),
            "total_base": structured["total_base"],
            "total_adjusted": structured["total_adjusted"],
            "unmatched_count": structured["unmatched_count"],
            "low_confidence_count": structured["low_confidence_count"],
            "requires_confirmation": structured["requires_confirmation"],
        },
        "ui_action": "show_structured_quote",
    }


def _confirm_pending_quote(args: Dict, db: Session, session: AgentSession) -> Dict:
    if not session.pending_quote:
        return {"ok": False, "error": "没有待确认的报价，请先生成报价"}
    session.pending_quote["confirmed"] = True
    session.confirmed_quote = session.pending_quote
    return {
        "ok": True,
        "message": "报价已确认，可以导出 Excel/PDF",
        "structured": session.confirmed_quote,
        "ui_action": "quote_confirmed",
    }


def _lenovo_quote(args: Dict, db: Session, session: AgentSession) -> Dict:
    from app.routers.lenovo_framework import _quote_one
    from app.schemas.lenovo_framework import LenovoQuoteRequest

    items = args.get("items") or []
    results = []
    devices = []
    total = 0.0
    for it in items:
        req = LenovoQuoteRequest(
            device_category=it.get("device_category") or "",
            brand=it.get("brand"),
            model=it.get("model") or "",
            sla=it.get("sla") or "",
            quantity=int(it.get("quantity") or 1),
            alias_key=it.get("alias_key"),
        )
        r = _quote_one(db, req)
        rd = r.model_dump() if hasattr(r, "model_dump") else dict(r)
        results.append(rd)
        unit = float(rd.get("unit_price") or 0)
        qty = int(rd.get("quantity") or 1)
        sub = float(rd.get("total_price") or unit * qty)
        total += sub
        devices.append(
            {
                "manufacturer": rd.get("matched_brand") or rd.get("brand") or "",
                "matched_model": rd.get("matched_model") or rd.get("model"),
                "match_rate": 100.0 if rd.get("status") == "ok" else 0.0,
                "device_price": None,
                "rate": None,
                "price": unit,
                "quantity": qty,
                "subtotal": sub,
                "primary_category": rd.get("matched_device_category") or rd.get("device_category"),
                "secondary_category": rd.get("end_type"),
                "tertiary_category": rd.get("sla"),
                "unmatched": rd.get("status") != "ok",
                "lenovo_status": rd.get("status"),
                "message": rd.get("message"),
            }
        )
    structured = {
        "quote_type": "lenovo",
        "caliber": "lenovo",
        "devices": devices,
        "total_base": round(total, 2),
        "total_adjusted": round(total, 2),
        "matched_service_level": None,
        "unmatched_count": sum(1 for d in devices if d.get("unmatched")),
        "low_confidence_count": 0,
        "requires_confirmation": REQUIRE_MATCH_CONFIRMATION,
        "confirmed": False if REQUIRE_MATCH_CONFIRMATION else True,
        "export_formats": ["excel", "pdf"],
        "pricing_note": "联想框架口径价格（工具计算结果）",
        "raw_results": results,
    }
    session.quote_type = "lenovo"
    session.pending_quote = structured
    session.confirmed_quote = None if REQUIRE_MATCH_CONFIRMATION else structured
    return {
        "ok": True,
        "structured": structured,
        "summary": {
            "line_count": len(devices),
            "total_base": structured["total_base"],
            "unmatched_count": structured["unmatched_count"],
            "requires_confirmation": structured["requires_confirmation"],
        },
        "ui_action": "show_structured_quote",
    }


def _list_job_positions(args: Dict, db: Session, session: AgentSession) -> Dict:
    from app.models.job_position import JobPosition

    keyword = (args.get("keyword") or "").strip()
    limit = int(args.get("limit") or 20)
    q = db.query(JobPosition)
    if keyword:
        q = q.filter(
            or_(
                JobPosition.position_name.ilike(f"%{keyword}%"),
                JobPosition.level_name.ilike(f"%{keyword}%"),
                JobPosition.category.ilike(f"%{keyword}%"),
            )
        )
    rows = q.order_by(JobPosition.id).limit(limit).all()
    return {
        "ok": True,
        "items": [
            {
                "id": r.id,
                "sequence_type": r.sequence_type,
                "category": r.category,
                "position_name": r.position_name,
                "level_name": r.level_name,
                "level_rank": r.level_rank,
            }
            for r in rows
        ],
    }


def _query_city_social(args: Dict, db: Session, session: AgentSession) -> Dict:
    from app.models.city_social_insurance import CitySocialInsurance

    city = (args.get("city") or "").strip()
    if not city:
        return {"ok": False, "error": "city 必填"}
    row = (
        db.query(CitySocialInsurance)
        .filter(CitySocialInsurance.city.ilike(f"%{city}%"))
        .first()
    )
    if not row:
        return {"ok": False, "error": f"未找到城市社保数据: {city}"}
    # 尽量兼容字段
    data = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    return {"ok": True, "city": data}


def _onsite_quote_estimate(args: Dict, db: Session, session: AgentSession) -> Dict:
    from app.models.job_position import JobPosition
    from app.routers.job_position import _query_salary_with_fallback

    city = (args.get("city") or "").strip()
    headcount = int(args.get("headcount") or 0)
    months = float(args.get("months") or 0)
    if not city or headcount <= 0 or months <= 0:
        return {"ok": False, "error": "需要 city、headcount、months，且均有效"}

    position_id = args.get("position_id")
    if not position_id and args.get("position_keyword"):
        kw = args["position_keyword"]
        pos = (
            db.query(JobPosition)
            .filter(
                or_(
                    JobPosition.position_name.ilike(f"%{kw}%"),
                    JobPosition.level_name.ilike(f"%{kw}%"),
                )
            )
            .first()
        )
        if not pos:
            return {"ok": False, "error": f"未找到岗位: {kw}，请先 list_job_positions"}
        position_id = pos.id

    if not position_id:
        return {"ok": False, "error": "需要 position_id 或 position_keyword"}

    pos = db.query(JobPosition).filter(JobPosition.id == position_id).first()
    if not pos:
        return {"ok": False, "error": "岗位不存在"}

    salary_result = _query_salary_with_fallback(db, position_id, city)
    # SalaryQueryResult may be pydantic
    if hasattr(salary_result, "model_dump"):
        sr = salary_result.model_dump()
    elif hasattr(salary_result, "dict"):
        sr = salary_result.dict()
    else:
        sr = dict(salary_result)

    monthly = float(sr.get("salary") or sr.get("monthly_salary") or 0)
    if monthly <= 0:
        return {
            "ok": False,
            "error": "该城市/岗位暂无薪资数据，无法估算",
            "salary_query": sr,
        }

    labor = round(monthly * headcount * months, 2)
    social_note = None
    social_employer = 0.0
    try:
        social = _query_city_social({"city": city}, db, session)
        if social.get("ok"):
            social_note = "已找到城市社保配置；精确五险一金请用驻场测算模型核对"
    except Exception:
        pass

    structured = {
        "quote_type": "onsite",
        "caliber": "onsite_estimate",
        "devices": [
            {
                "manufacturer": city,
                "matched_model": f"{pos.position_name} / {pos.level_name}",
                "match_rate": 100.0,
                "device_price": monthly,
                "rate": None,
                "price": monthly,
                "quantity": headcount * months,
                "subtotal": labor,
                "primary_category": "驻场服务",
                "secondary_category": pos.category,
                "tertiary_category": pos.sequence_type,
                "unmatched": False,
            }
        ],
        "total_base": labor,
        "total_adjusted": labor,
        "matched_service_level": None,
        "unmatched_count": 0,
        "low_confidence_count": 0,
        "requires_confirmation": REQUIRE_MATCH_CONFIRMATION,
        "confirmed": False if REQUIRE_MATCH_CONFIRMATION else True,
        "export_formats": ["excel", "pdf"],
        "pricing_note": "粗算：月薪 × 人数 × 月数；不含完整管理费/五险一金分项时请用测算模型精算",
        "slots": {
            "city": city,
            "position_id": position_id,
            "headcount": headcount,
            "months": months,
            "monthly_salary": monthly,
            "salary_source": sr.get("source") or sr.get("salary_source"),
            "social_note": social_note,
            "social_employer_estimate": social_employer,
        },
    }
    session.quote_type = "onsite"
    session.pending_quote = structured
    session.confirmed_quote = None if REQUIRE_MATCH_CONFIRMATION else structured
    session.slots.update(structured["slots"])
    return {
        "ok": True,
        "structured": structured,
        "summary": {
            "monthly_salary": monthly,
            "labor_total": labor,
            "requires_confirmation": structured["requires_confirmation"],
        },
        "ui_action": "show_structured_quote",
        "wizard_hint": "复杂分项请打开「驻场服务测算模型」",
    }


def _list_relocation_vehicles(args: Dict, db: Session, session: AgentSession) -> Dict:
    from app.models.relocation_vehicle import RelocationVehicle

    rows = db.query(RelocationVehicle).order_by(RelocationVehicle.id).limit(50).all()
    items = []
    for r in rows:
        data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        items.append(_json_safe(data))
    return {"ok": True, "items": items}


def _parse_price_number(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return None
    # 提取首个数字（支持 1200 / 1,200元 / ¥1200起）
    m = re.search(r"(\d+(?:\.\d+)?)", s.replace(",", ""))
    return float(m.group(1)) if m else None


def _relocation_quote_estimate(args: Dict, db: Session, session: AgentSession) -> Dict:
    from app.models.relocation_vehicle import RelocationVehicle

    kw = (args.get("vehicle_keyword") or "").strip()
    qty = float(args.get("quantity") or 0)
    if not kw or qty <= 0:
        return {"ok": False, "error": "需要 vehicle_keyword 与有效 quantity"}

    row = (
        db.query(RelocationVehicle)
        .filter(
            or_(
                RelocationVehicle.vehicle_name.ilike(f"%{kw}%"),
                RelocationVehicle.vehicle_category.ilike(f"%{kw}%"),
            )
        )
        .first()
    )

    if not row:
        return {"ok": False, "error": f"未找到车辆类型: {kw}，请先 list_relocation_vehicles"}

    data = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    unit = _parse_price_number(data.get("start_price"))
    if unit is None:
        unit = _parse_price_number(data.get("km_price"))
    if unit is None:
        return {
            "ok": False,
            "error": "该车辆记录无可用起步价/公里价，请用搬迁测算模型精算",
            "vehicle": _json_safe(data),
        }

    subtotal = round(unit * qty, 2)
    label = data.get("vehicle_name") or data.get("vehicle_category") or kw
    structured = {
        "quote_type": "relocation",
        "caliber": "relocation_estimate",
        "devices": [
            {
                "manufacturer": args.get("city") or "",
                "matched_model": str(label),
                "match_rate": 100.0,
                "device_price": unit,
                "rate": None,
                "price": unit,
                "quantity": qty,
                "subtotal": subtotal,
                "primary_category": "搬迁服务",
                "secondary_category": args.get("notes") or "",
                "tertiary_category": "",
                "unmatched": False,
            }
        ],
        "total_base": subtotal,
        "total_adjusted": subtotal,
        "matched_service_level": None,
        "unmatched_count": 0,
        "low_confidence_count": 0,
        "requires_confirmation": REQUIRE_MATCH_CONFIRMATION,
        "confirmed": False if REQUIRE_MATCH_CONFIRMATION else True,
        "export_formats": ["excel", "pdf"],
        "pricing_note": "粗算：车辆单价 × 数量/趟次；复杂路径/叠加价请用搬迁测算模型",
    }
    session.quote_type = "relocation"
    session.pending_quote = structured
    session.confirmed_quote = None if REQUIRE_MATCH_CONFIRMATION else structured
    return {
        "ok": True,
        "structured": structured,
        "vehicle": _json_safe(data),
        "summary": {"unit_price": unit, "quantity": qty, "total": subtotal},
        "ui_action": "show_structured_quote",
        "wizard_hint": "复杂场景请打开「搬迁服务测算模型」",
    }


TOOL_HANDLERS = {
    "search_products": _search_products,
    "list_service_levels": _list_service_levels,
    "describe_quote_type": _describe_quote_type,
    "parse_bom_from_files": _parse_bom_from_files,
    "match_devices": _match_devices,
    "create_maintenance_quote": _create_maintenance_quote,
    "confirm_pending_quote": _confirm_pending_quote,
    "lenovo_quote": _lenovo_quote,
    "list_job_positions": _list_job_positions,
    "query_city_social": _query_city_social,
    "onsite_quote_estimate": _onsite_quote_estimate,
    "list_relocation_vehicles": _list_relocation_vehicles,
    "relocation_quote_estimate": _relocation_quote_estimate,
}


def try_extract_bom_from_requirement(text: str) -> List[Dict[str, Any]]:
    return _extract_devices_from_text(text or "")
