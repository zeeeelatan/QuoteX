"""联想框架报价路由

URL 前缀: /lenovo

- /classification         机型分类 CRUD
- /pattern-rule           通配规则 CRUD
- /prices/tape            磁带库价格 CRUD
- /prices/network         网络价格 CRUD（含 FC/IB/网络/路由器/无线控制器）
- /prices/server          服务器价格 CRUD
- /prices/storage         存储价格 CRUD（L1/L2/M）
- /prices/minicomputer    小型机价格 CRUD
- /prices/inspection      巡检价格 CRUD
- /quote                  单条报价
- /bulk-quote             批量报价
"""
import re
from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, literal, or_, text
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lenovo_framework import (
    LenovoClassification,
    LenovoFrameworkModel,
    LenovoPatternRule,
    LenovoPriceInspection,
    LenovoPriceMinicomputer,
    LenovoPriceNetwork,
    LenovoPriceServer,
    LenovoPriceStorage,
    LenovoPriceTapeLibrary,
)
from app.schemas.lenovo_framework import (
    LenovoBulkQuoteRequest,
    LenovoBulkQuoteResponse,
    LenovoClassificationCreate,
    LenovoClassificationOut,
    LenovoFrameworkModelCreate,
    LenovoFrameworkModelOut,
    LenovoFrameworkModelsPage,
    LenovoPatternRuleCreate,
    LenovoPatternRuleOut,
    LenovoPriceInspectionCreate,
    LenovoPriceInspectionOut,
    LenovoPriceMiniCreate,
    LenovoPriceMiniOut,
    LenovoPriceNetworkCreate,
    LenovoPriceNetworkOut,
    LenovoPriceServerCreate,
    LenovoPriceServerOut,
    LenovoPriceStorageCreate,
    LenovoPriceStorageOut,
    LenovoPriceTapeCreate,
    LenovoPriceTapeOut,
    LenovoQuoteRequest,
    LenovoQuoteResult,
)

router = APIRouter(prefix="/lenovo", tags=["联想框架报价"])


# ============================================================
# 启动时自动 ALTER：旧库补 aliases 列
# ============================================================
def _ensure_columns():
    try:
        from app.database import engine
        with engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE lenovo_framework_models "
                "ADD COLUMN IF NOT EXISTS aliases JSONB DEFAULT '[]'::jsonb"
            ))
    except Exception:
        # 表可能还未 create_all；下次启动会再尝试
        pass


_ensure_columns()


# ============================================================
# 别名归一化（保守版：保留品牌前缀）
# ============================================================
def _normalize_model_py(s: Optional[str]) -> str:
    """型号归一化（Python 端）：去 "model" 词、去括号（半/全角）、去空格、去连字符、小写

    用于跨"括号字符 / 空格 / Model 标识"差异的同型号匹配，例：
      "TaiShan 200 (Model 2280)"   → "taishan2002280"
      "TaiShan 200（Model 2280）"   → "taishan2002280"
      "TaiShan 200 2280"           → "taishan2002280"
      "Dell-PowerEdge R630"        → "dellpoweredger630"
    """
    if not s:
        return ""
    s = str(s).strip().lower()
    s = re.sub(r"model\s*", "", s)   # 去 "Model " 标签
    s = re.sub(r"[\s()（）\-_/]+", "", s)
    return s


def _model_norm_pg_expr(col):
    """SQLAlchemy 表达式：在 PG 端把 model 字段归一化（与 _normalize_model_py 等价）"""
    e = func.lower(col)
    e = func.regexp_replace(e, r"model\s*", "", "g")
    e = func.regexp_replace(e, r"[\s()（）\-_/]+", "", "g")
    return e


def normalize_alias(s: Optional[str]) -> str:
    """归一化「原始品牌型号」字符串作为 alias 比对键

    - lowercase
    - 把 - _ / 等分隔符替换为空格
    - 合并连续空白
    - 不剥离品牌（按整体存储，保守策略）

    例：
      "Dell-PowerEdge R630"   → "dell powerEdge r630"
      "DELL   R630"           → "dell r630"
      "戴尔 PowerEdge R630"    → "戴尔 powerEdge r630"
    """
    if not s:
        return ""
    s = str(s).strip().lower()
    s = re.sub(r"[-_/\\]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


# ============================================================
# 通用 CRUD 工厂
# ============================================================

def _make_crud(prefix: str, Model, SchemaCreate, SchemaOut, order_col=None):
    sub = APIRouter(prefix=prefix)

    @sub.get("/", response_model=List[SchemaOut])
    def list_all(db: Session = Depends(get_db)):
        q = db.query(Model)
        if order_col is not None:
            q = q.order_by(order_col)
        else:
            q = q.order_by(Model.id.asc())
        return q.all()

    @sub.post("/", response_model=SchemaOut)
    def create(payload: SchemaCreate, db: Session = Depends(get_db)):
        obj = Model(**payload.model_dump())
        db.add(obj)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"创建失败：{e}")
        db.refresh(obj)
        return obj

    @sub.put("/{item_id}", response_model=SchemaOut)
    def update(item_id: int, payload: SchemaCreate, db: Session = Depends(get_db)):
        obj = db.query(Model).filter(Model.id == item_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="记录不存在")
        for k, v in payload.model_dump().items():
            setattr(obj, k, v)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"更新失败：{e}")
        db.refresh(obj)
        return obj

    @sub.delete("/{item_id}")
    def delete(item_id: int, db: Session = Depends(get_db)):
        obj = db.query(Model).filter(Model.id == item_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="记录不存在")
        db.delete(obj)
        db.commit()
        return {"ok": True}

    @sub.delete("/")
    def delete_all(db: Session = Depends(get_db)):
        n = db.query(Model).delete()
        db.commit()
        return {"ok": True, "deleted": n}

    return sub


# 挂载各 CRUD
router.include_router(_make_crud(
    "/classification", LenovoClassification, LenovoClassificationCreate, LenovoClassificationOut,
    order_col=LenovoClassification.device_category.asc(),
))
router.include_router(_make_crud(
    "/pattern-rule", LenovoPatternRule, LenovoPatternRuleCreate, LenovoPatternRuleOut,
    order_col=LenovoPatternRule.brand.asc(),
))
router.include_router(_make_crud(
    "/prices/tape", LenovoPriceTapeLibrary, LenovoPriceTapeCreate, LenovoPriceTapeOut,
))
router.include_router(_make_crud(
    "/prices/network", LenovoPriceNetwork, LenovoPriceNetworkCreate, LenovoPriceNetworkOut,
))
router.include_router(_make_crud(
    "/prices/server", LenovoPriceServer, LenovoPriceServerCreate, LenovoPriceServerOut,
))
router.include_router(_make_crud(
    "/prices/storage", LenovoPriceStorage, LenovoPriceStorageCreate, LenovoPriceStorageOut,
))
router.include_router(_make_crud(
    "/prices/minicomputer", LenovoPriceMinicomputer, LenovoPriceMiniCreate, LenovoPriceMiniOut,
))
router.include_router(_make_crud(
    "/prices/inspection", LenovoPriceInspection, LenovoPriceInspectionCreate, LenovoPriceInspectionOut,
))


# ============================================================
# 报价主入口
# ============================================================

# 网络大类的子类 → 价格表 device_category 的映射
_NETWORK_PRICE_CATEGORY = {
    "光纤交换机": "FC光纤交换机",
    "IB交换机": "IB光纤交换机",
    # 网络设备的 sub_category 直接作为价格表 device_category 使用
}


def _normalize_brand(brand: Optional[str]) -> str:
    return (brand or "").strip().lower()


def _match_end_type(
    db: Session,
    device_category: str,
    brand: Optional[str],
    model: str,
    alias_key: Optional[str] = None,
) -> Tuple[Optional[LenovoFrameworkModel], Optional[LenovoPatternRule], str]:
    """端型判定：alias 快查 → 新机型库精确 → 新机型库前缀 → pattern_rule 兜底。

    返回 (framework_model, pattern_rule, method)
    method ∈ {alias, exact, prefix, pattern_fallback, none}

    设计要点：
    - **alias 快查**：用户历史确认过的「原始品牌型号 → 标准记录」对照，置信度最高，前置
    - 主表 lenovo_framework_models（dc_inventory + classification + pattern_expanded 合并）
    - 优先有 end_type 的记录（dc_inventory 来源的 end_type 可能为空）
    - 严格前缀匹配替代原"双向 ilike 模糊"，降低跨型号脏命中
    - pattern_rule 仅作 fallback，命中后 method='pattern_fallback' 提示用户加入机型库
    """
    model = (model or "").strip()
    if not model:
        return None, None, "none"

    # ============ 0) Alias 快查（用户已确认过的对应关系最优先） ============
    if alias_key:
        key_norm = normalize_alias(alias_key)
        if len(key_norm) >= 3:
            # JSONB contains：aliases @> '["xxx"]'
            row = db.query(LenovoFrameworkModel).filter(
                LenovoFrameworkModel.device_category == device_category,
                LenovoFrameworkModel.aliases.contains([key_norm]),
            ).first()
            if row:
                return row, None, "alias"

    # 用空格归一化处理 "DL580 Gen8" / "DL580Gen8" 这类
    model_lower = model.lower()
    model_nospace = model_lower.replace(" ", "")

    # 排序：有 end_type 的优先（NULL 排后面）
    end_type_priority = LenovoFrameworkModel.end_type.is_(None).asc()

    # ============ 1) 归一化精确（最强匹配） ============
    # 同时铺平 "(Model 2280)" / "（Model 2280）" / "2280" 这类字面差异，
    # 并优先返回 end_type 不为空的记录（避免命中 dc_inventory 留空版本）
    norm_input = _normalize_model_py(model)
    if norm_input and len(norm_input) >= 3:
        norm_base = db.query(LenovoFrameworkModel).filter(
            LenovoFrameworkModel.device_category == device_category,
            _model_norm_pg_expr(LenovoFrameworkModel.model) == norm_input,
        )
        if brand:
            b = brand.strip().lower()
            # 1.a) brand 包含 + 归一化精确（端型优先）
            row = norm_base.filter(
                func.lower(LenovoFrameworkModel.brand).ilike(f"%{b}%")
            ).order_by(end_type_priority).first()
            if row:
                return row, None, "exact"
        # 1.b) 不带 brand 限制（端型优先）
        row = norm_base.order_by(end_type_priority).first()
        if row:
            return row, None, "exact"

    # ============ 1.5) lower(model) 严格相等（仅当归一化命中不到的兜底） ============
    exact_base = db.query(LenovoFrameworkModel).filter(
        LenovoFrameworkModel.device_category == device_category,
        func.lower(LenovoFrameworkModel.model) == model_lower,
    )
    if brand:
        b = brand.strip().lower()
        row = exact_base.filter(
            func.lower(LenovoFrameworkModel.brand).ilike(f"%{b}%")
        ).order_by(end_type_priority).first()
        if row:
            return row, None, "exact"
    row = exact_base.order_by(end_type_priority).first()
    if row:
        return row, None, "exact"

    # ============ 2) 严格前缀匹配 ============
    # 关系：DB.model 是 input 的前缀（input='DL580 Gen8' 命中 DB='DL580'）
    # 限制 DB.model 长度 >= 4 字符，避免太短前缀误命中
    prefix_base = db.query(LenovoFrameworkModel).filter(
        LenovoFrameworkModel.device_category == device_category,
        func.char_length(LenovoFrameworkModel.model) >= 4,
        literal(model_lower).ilike(func.concat(func.lower(LenovoFrameworkModel.model), "%")),
    ).order_by(
        func.char_length(LenovoFrameworkModel.model).desc(),  # 最长前缀优先
        end_type_priority,
    )
    if brand:
        b = brand.strip().lower()
        row = prefix_base.filter(
            func.lower(LenovoFrameworkModel.brand).ilike(f"%{b}%")
        ).first()
        if row:
            return row, None, "prefix"
    row = prefix_base.first()
    if row:
        return row, None, "prefix"

    # ============ 3) Pattern 兜底（仅对 pattern 表有数据的大类） ============
    if brand:
        b = brand.strip().lower()
        rules = db.query(LenovoPatternRule).filter(
            LenovoPatternRule.device_category == device_category,
            func.lower(LenovoPatternRule.brand).ilike(f"%{b}%"),
        ).order_by(
            func.char_length(LenovoPatternRule.pattern_raw).desc(),
            LenovoPatternRule.priority.asc(),
        ).all()
        for rule in rules:
            try:
                # pattern 是基于"无空格 model"设计的，先归一化输入
                if not re.match(rule.pattern_regex, model_nospace, re.IGNORECASE):
                    continue
            except re.error:
                continue
            # 排除列表
            if rule.notes and "除外:" in rule.notes:
                excl_part = rule.notes.split("除外:", 1)[1].strip()
                excl_list = [x.strip().upper() for x in re.split(r"[/、,]+", excl_part) if x.strip()]
                if model_nospace.upper() in excl_list or model.upper() in excl_list:
                    continue
            return None, rule, "pattern_fallback"

    return None, None, "none"


def _normalize_end_type_for_pricing(device_category: str, end_type: str) -> str:
    """端型在价格表中的规范化。

    - 磁带库：'低端磁带机'/'低端磁带库' 已在导入时统一成 '低端/中端/高端'
    - 其他大类：返回原值
    """
    return end_type


def _resolve_network_target_category(device_category: str, sub_category: Optional[str]) -> Optional[str]:
    if device_category == "光纤交换机":
        return "FC光纤交换机"
    if device_category == "IB交换机":
        return "IB光纤交换机"
    if device_category == "网络设备":
        # sub_category 必须有值，例如 网络交换机 / 路由器 / 无线控制器 / 无线AP
        return sub_category
    return None


def _sla_candidates(db: Session, raw_sla: str) -> List[str]:
    """根据 service_level 别名展开 SLA 候选写法。

    返回值首个永远是原始输入；命中标准行时把该行的 response_time + 所有
    aliases 全部加入候选（去重）。
    """
    raw = (raw_sla or "").strip()
    candidates: List[str] = [raw] if raw else []
    try:
        from .service_level import resolve_sla  # 局部导入避免循环
        lvl = resolve_sla(db, raw)
        if lvl:
            if lvl.response_time and lvl.response_time not in candidates:
                candidates.append(lvl.response_time)
            for a in (lvl.aliases or []):
                a = (a or "").strip()
                if a and a not in candidates:
                    candidates.append(a)
    except Exception:
        pass
    return candidates


def _find_first(query_factory, candidates: List[str]):
    """挨个用 candidates 尝试查询，返回第一个命中。"""
    for sla in candidates:
        row = query_factory(sla)
        if row:
            return row, sla
    return None, None


def _lookup_price(
    db: Session,
    device_category: str,
    end_type: str,
    sub_category: Optional[str],
    req: LenovoQuoteRequest,
) -> Tuple[Optional[object], Optional[str]]:
    """根据大类查价。

    返回 (price_row, error_message)
    """
    candidates = _sla_candidates(db, req.sla)
    if not candidates:
        return None, "缺少 SLA"

    if device_category == "磁带库":
        if not req.drive_config:
            return None, "磁带库需要 drive_config (LTO5/6/7/8)"
        row, _ = _find_first(
            lambda sla: db.query(LenovoPriceTapeLibrary).filter_by(
                end_type=end_type, drive_config=req.drive_config.strip(), sla=sla
            ).first(),
            candidates,
        )
        return row, None

    if device_category in ("光纤交换机", "IB交换机", "网络设备"):
        target = _resolve_network_target_category(device_category, sub_category)
        if not target:
            return None, "网络设备需要 sub_category（网络交换机/路由器/无线AP/无线控制器）"
        row, _ = _find_first(
            lambda sla: db.query(LenovoPriceNetwork).filter_by(
                device_category=target, end_type=end_type, sla=sla
            ).first(),
            candidates,
        )
        return row, None

    if device_category == "服务器":
        missing = [k for k in ("includes_ssd", "package_type", "includes_disk")
                   if getattr(req, k) is None]
        if missing:
            return None, f"服务器需要参数:{', '.join(missing)}"
        row, _ = _find_first(
            lambda sla: db.query(LenovoPriceServer).filter_by(
                end_type=end_type,
                includes_ssd=req.includes_ssd,
                package_type=req.package_type.strip(),
                sla=sla,
                includes_disk=req.includes_disk,
            ).first(),
            candidates,
        )
        return row, None

    if device_category == "存储":
        if req.includes_disk_no_return is None:
            return None, "存储需要 includes_disk_no_return"
        row, _ = _find_first(
            lambda sla: db.query(LenovoPriceStorage).filter_by(
                end_type=end_type, sla=sla, includes_disk_no_return=req.includes_disk_no_return
            ).first(),
            candidates,
        )
        return row, None

    if device_category == "小型机":
        if req.includes_disk is None:
            return None, "小型机需要 includes_disk"
        row, _ = _find_first(
            lambda sla: db.query(LenovoPriceMinicomputer).filter_by(
                end_type=end_type, sla=sla, includes_disk=req.includes_disk
            ).first(),
            candidates,
        )
        return row, None

    return None, f"不支持的设备大类:{device_category}"


def _quote_one(db: Session, req: LenovoQuoteRequest) -> LenovoQuoteResult:
    qty = max(1, int(req.quantity or 1))
    base = LenovoQuoteResult(
        status="unmatched",
        device_category=req.device_category,
        brand=req.brand,
        model=req.model,
        sla=req.sla,
        quantity=qty,
    )

    # cls/method 闭包外可见，用于后续 message 生成
    matched_cls: Optional[LenovoFrameworkModel] = None
    matched_method: str = "none"

    # 用户手动锁定端型 → 跳过自动端型识别，直接按指定端型查价
    if req.force_end_type:
        base.end_type = req.force_end_type.strip()
        base.match_method = "manual"
        base.sub_category = req.sub_category
        # 同时给出输入 brand/model 便于前端继续展示
        base.matched_brand = req.brand
        base.matched_model = req.model
        base.matched_device_category = req.device_category
    else:
        cls, rule, method = _match_end_type(
            db, req.device_category, req.brand, req.model, alias_key=req.alias_key
        )
        matched_cls = cls
        matched_method = method
        base.match_method = method
        if cls:
            base.end_type = cls.end_type
            base.sub_category = cls.sub_category
            base.matched_classification_id = cls.id
            base.matched_brand = cls.brand
            base.matched_model = cls.model
            base.matched_device_category = cls.device_category
        elif rule:
            base.end_type = rule.end_type
            base.matched_pattern_id = rule.id
            # 通配规则下 sub_category 由调用方显式传入
            base.sub_category = req.sub_category
            # 通配命中：把通配 raw 写入便于前端展示
            base.matched_brand = rule.brand
            base.matched_model = rule.pattern_raw
            base.matched_device_category = rule.device_category
        else:
            # 不命中：仍把输入 model 透传回去，前端可显示"未命中"
            base.matched_brand = req.brand
            base.matched_model = req.model
            base.matched_device_category = None

    if not base.end_type:
        # 区分两种"无端型"
        if matched_cls is not None:
            # 已在机型库命中型号，但 end_type 留空（dc_inventory 来源）
            base.status = "need_end_type"
            base.message = "已识别型号，但端型待人工指定（可在表格中点击「端型」列选择）"
        else:
            base.message = "无法判定端型：机型库和通配规则均未命中"
        return base

    # 查价
    end_type_norm = _normalize_end_type_for_pricing(req.device_category, base.end_type)
    price_row, err = _lookup_price(db, req.device_category, end_type_norm, base.sub_category, req)
    if err:
        base.status = "no_price"
        base.message = err
        return base
    if price_row is None:
        base.status = "no_price"
        base.message = f"未找到对应价格（{req.device_category} / {end_type_norm} / {req.sla}）"
        return base

    base.status = "ok"
    base.unit_price = Decimal(price_row.price)
    base.total_price = (base.unit_price * qty).quantize(Decimal("0.01"))
    base.price_table_row_id = price_row.id
    # pattern 兜底命中：附加"建议沉淀到机型库"提示，前端可用此触发"加入机型库"按钮
    if matched_method == "pattern_fallback":
        base.message = "通配规则兜底命中，建议将此型号沉淀到机型库以提升下次准确性"
    base.price_notes = getattr(price_row, "notes", None)
    return base


# ============================================================
# 统一机型库 list / CRUD
# 注：必须先注册 upsert（更具体路径），再注册 PUT/DELETE /{item_id}，
# 才能避免 {item_id} 通配捕获 "upsert" 字符串。
# ============================================================

@router.get("/framework-models/", response_model=LenovoFrameworkModelsPage)
def list_framework_models(
    keyword: str = Query("", description="按 model / brand / series / mt_code 模糊匹配"),
    device_category: Optional[str] = Query(None),
    source: Optional[str] = Query(None, description="classification / pattern_expanded / dc_inventory / user_confirmed / manual"),
    has_end_type: Optional[bool] = Query(None, description="True=只看有端型，False=只看端型为空"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(LenovoFrameworkModel)
    if device_category:
        q = q.filter(LenovoFrameworkModel.device_category == device_category)
    if source:
        q = q.filter(LenovoFrameworkModel.source == source)
    if has_end_type is True:
        q = q.filter(LenovoFrameworkModel.end_type.isnot(None))
    elif has_end_type is False:
        q = q.filter(LenovoFrameworkModel.end_type.is_(None))
    kw = (keyword or "").strip()
    if kw:
        like = f"%{kw}%"
        q = q.filter(
            or_(
                LenovoFrameworkModel.model.ilike(like),
                LenovoFrameworkModel.brand.ilike(like),
                LenovoFrameworkModel.series.ilike(like),
                LenovoFrameworkModel.mt_code.ilike(like),
            )
        )
    total = q.count()
    rows = (
        q.order_by(LenovoFrameworkModel.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": rows}


@router.post("/framework-models/", response_model=LenovoFrameworkModelOut)
def create_framework_model(payload: LenovoFrameworkModelCreate, db: Session = Depends(get_db)):
    obj = LenovoFrameworkModel(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"创建失败：{e}")
    db.refresh(obj)
    return obj


class FrameworkModelUpsertReq(BaseModel):
    """用户在前端手动确认端型后，回写到机型库"""
    device_category: str
    brand: Optional[str] = None
    model: str
    end_type: str
    sub_category: Optional[str] = None
    notes: Optional[str] = None
    # 用户希望记忆的「原始品牌型号」（raw 字符串），归一化后追加到 aliases 数组
    alias_raw: Optional[str] = None


@router.post("/framework-models/upsert")
def upsert_framework_model(req: FrameworkModelUpsertReq, db: Session = Depends(get_db)):
    """upsert（device_category, lower(brand), lower(model)）→ 写入或更新 end_type

    用户在表格里手动选了端型后调用此接口，把"确认结果"沉淀到机型库，
    下次同型号自动报价就能直接命中。
    """
    model = (req.model or "").strip()
    if not model:
        raise HTTPException(status_code=400, detail="model 不能为空")
    brand = (req.brand or "").strip() or None
    cat = req.device_category.strip()

    # 按 (device_category, lower(brand), lower(model)) 找已有记录
    q = db.query(LenovoFrameworkModel).filter(
        LenovoFrameworkModel.device_category == cat,
        func.lower(LenovoFrameworkModel.model) == model.lower(),
    )
    if brand:
        existing = q.filter(
            func.lower(LenovoFrameworkModel.brand).ilike(f"%{brand.lower()}%")
        ).first() or q.first()
    else:
        existing = q.first()

    # 归一化即将追加的 alias_raw（如果有且长度足够）
    alias_norm = normalize_alias(req.alias_raw) if req.alias_raw else ""
    if alias_norm and len(alias_norm) < 3:
        alias_norm = ""  # 太短的拒绝，避免脏数据

    if existing:
        existing.end_type = req.end_type.strip()
        if req.sub_category:
            existing.sub_category = req.sub_category.strip()
        # source 标记为 user_confirmed，便于审计
        existing.source = "user_confirmed"
        if req.notes:
            existing.notes = req.notes
        if alias_norm:
            existing_aliases = list(existing.aliases or [])
            if alias_norm not in existing_aliases:
                existing_aliases.append(alias_norm)
                existing.aliases = existing_aliases
        db.commit()
        db.refresh(existing)
        return {"action": "updated", "id": existing.id, "alias_added": bool(alias_norm)}

    obj = LenovoFrameworkModel(
        device_category=cat,
        brand=brand,
        model=model,
        end_type=req.end_type.strip(),
        sub_category=req.sub_category.strip() if req.sub_category else None,
        source="user_confirmed",
        notes=req.notes,
        aliases=[alias_norm] if alias_norm else [],
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"action": "created", "id": obj.id, "alias_added": bool(alias_norm)}


@router.put("/framework-models/{item_id}", response_model=LenovoFrameworkModelOut)
def update_framework_model(
    item_id: int, payload: LenovoFrameworkModelCreate, db: Session = Depends(get_db)
):
    obj = db.query(LenovoFrameworkModel).filter(LenovoFrameworkModel.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="记录不存在")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"更新失败：{e}")
    db.refresh(obj)
    return obj


@router.delete("/framework-models/{item_id}")
def delete_framework_model(item_id: int, db: Session = Depends(get_db)):
    obj = db.query(LenovoFrameworkModel).filter(LenovoFrameworkModel.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(obj)
    db.commit()
    return {"ok": True}


@router.get("/framework-models/stats")
def framework_models_stats(db: Session = Depends(get_db)):
    """统计：总数、按 source / device_category / has_end_type 分布"""
    from sqlalchemy import case
    total = db.query(LenovoFrameworkModel).count()
    by_source = dict(
        db.query(LenovoFrameworkModel.source, func.count())
        .group_by(LenovoFrameworkModel.source).all()
    )
    by_category = dict(
        db.query(LenovoFrameworkModel.device_category, func.count())
        .group_by(LenovoFrameworkModel.device_category).all()
    )
    with_end = db.query(LenovoFrameworkModel).filter(
        LenovoFrameworkModel.end_type.isnot(None)
    ).count()
    return {
        "total": total,
        "with_end_type": with_end,
        "without_end_type": total - with_end,
        "by_source": by_source,
        "by_category": by_category,
    }


@router.get("/end-types", response_model=List[str])
def list_end_types(
    device_category: str = Query(..., description="设备大类"),
    db: Session = Depends(get_db),
):
    """返回该设备大类下所有可用端型（合并 classification 表 + 对应价格表，按业务顺序排序）"""
    cat = device_category.strip()
    end_types: set[str] = set()

    # 来源 1：分类表
    rows = db.query(LenovoClassification.end_type).filter(
        LenovoClassification.device_category == cat
    ).distinct().all()
    end_types.update(r[0] for r in rows if r[0])

    # 来源 2：对应的价格表（防止分类表里缺漏的端型）
    price_model = None
    if cat == "磁带库":
        price_model = LenovoPriceTapeLibrary
    elif cat == "服务器":
        price_model = LenovoPriceServer
    elif cat == "存储":
        price_model = LenovoPriceStorage
    elif cat == "小型机":
        price_model = LenovoPriceMinicomputer
    elif cat in ("光纤交换机", "IB交换机", "网络设备"):
        price_model = LenovoPriceNetwork

    if price_model is not None:
        rows = db.query(price_model.end_type).distinct().all()
        end_types.update(r[0] for r in rows if r[0])

    # 按业务习惯排序：低端 < 中端 < 高端 < 超高端 < L1 < L2 < M
    order = ["低端", "中端", "高端", "超高端", "L1", "L2", "M"]

    def sort_key(et: str):
        return (order.index(et) if et in order else 99, et)

    return sorted(end_types, key=sort_key)


def _search_framework_models(
    keyword: str,
    device_category: Optional[str],
    limit: int,
    db: Session,
):
    """共享：在 lenovo_framework_models 中模糊查询。

    device_category 作为「软过滤」：优先在该大类内查；若该大类查无结果
    （常见于前端自动识别的大类不准，如把存储识别成服务器），则放宽大类再查一次，
    避免把本应能模糊命中的型号（如 AS13000 系列）误隐藏。
    """
    keyword = (keyword or "").strip()

    def _run(cat: Optional[str]):
        q = db.query(LenovoFrameworkModel)
        if cat:
            q = q.filter(LenovoFrameworkModel.device_category == cat)
        if keyword:
            kw = f"%{keyword}%"
            q = q.filter(
                or_(
                    LenovoFrameworkModel.model.ilike(kw),
                    LenovoFrameworkModel.brand.ilike(kw),
                    LenovoFrameworkModel.series.ilike(kw),
                )
            )
        # 有端型的优先（dc_inventory 留空的排在后面）
        return q.order_by(
            LenovoFrameworkModel.end_type.is_(None).asc(),
            LenovoFrameworkModel.id.asc(),
        ).limit(limit).all()

    rows = _run(device_category)
    if not rows and device_category:
        # 指定大类查无结果 → 放宽大类兜底，避免大类识别错误导致漏检
        rows = _run(None)
    return rows


@router.get("/search-models")
def search_models(
    keyword: str = Query("", description="按 model / brand / series 模糊匹配"),
    device_category: Optional[str] = Query(None, description="可选，按设备大类过滤"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """供前端「联想匹配型号」搜索弹窗使用：在统一机型库中查询。"""
    rows = _search_framework_models(keyword, device_category, limit, db)
    # 兼容前端字段（兼容 LenovoClassificationOut 的 device_category / brand / series / model / end_type / sub_category）
    return [
        {
            "id": r.id,
            "device_category": r.device_category,
            "brand": r.brand,
            "series": r.series,
            "model": r.model,
            "mt_code": r.mt_code,
            "end_type": r.end_type,
            "sub_category": r.sub_category,
            "source": r.source,
            "notes": r.notes,
        }
        for r in rows
    ]


# 向后兼容：旧前端仍可能调 /search-classification（实际上现在已经查的是新表）
@router.get("/search-classification")
def search_classification_legacy(
    keyword: str = Query(""),
    device_category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """已弃用，逻辑等同 /search-models。保留以避免老版前端 404。"""
    return search_models(keyword=keyword, device_category=device_category, limit=limit, db=db)


@router.post("/quote", response_model=LenovoQuoteResult)
def quote(req: LenovoQuoteRequest, db: Session = Depends(get_db)):
    return _quote_one(db, req)


@router.post("/bulk-quote", response_model=LenovoBulkQuoteResponse)
def bulk_quote(req: LenovoBulkQuoteRequest, db: Session = Depends(get_db)):
    return LenovoBulkQuoteResponse(results=[_quote_one(db, item) for item in req.items])
