"""add lenovo_framework_models table + service_level aliases column + initial data migration

This migration:
1. Creates the unified `lenovo_framework_models` table (model → end_type / sub_category
   matching source, used by 联想框架报价 pipeline).
2. Backfills two columns on `service_level` (`definition`, `aliases`) for SLA alias
   resolution (idempotent via ADD COLUMN IF NOT EXISTS).
3. Seeds `lenovo_framework_models` from 3 sources:
   - lenovo_classification (993 rows, end_type populated)
   - lenovo_pattern_rule expansion against device_inventory (~852 rows, end_type populated)
   - device_inventory direct import (~18000 rows, end_type=NULL, user fills in manually)

Revision ID: 004
Revises: 003
Create Date: 2026-06-03
"""
import re
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


# ============================================================
# Helpers
# ============================================================

def _table_exists(conn, table_name: str) -> bool:
    return conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=:t"
    ), {"t": table_name}).fetchone() is not None


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    return conn.execute(sa.text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table_name, "c": column_name}).fetchone() is not None


# ============================================================
# Data migration: lenovo_framework_models seed
# ============================================================
# (Logic mirrors scripts/migrate_lenovo_framework_models.py)

DC_TO_LENOVO_CATEGORY = {
    # 主机设备
    ("主机设备", "X86服务器"): ("服务器", None),
    ("主机设备", "小型机"): ("小型机", None),
    ("主机设备", "Power服务器"): ("小型机", None),
    ("主机设备", "ARM服务器"): ("服务器", None),
    ("主机设备", "刀箱"): ("服务器", None),
    # 存储设备
    ("存储设备", "SAN存储"): ("存储", None),
    ("存储设备", "NAS存储"): ("存储", None),
    ("存储设备", "统一存储"): ("存储", None),
    ("存储设备", "分布式存储"): ("存储", None),
    ("存储设备", "桌面NAS存储"): ("存储", None),
    ("存储设备", "存储扩展柜"): ("存储", None),
    ("存储设备", "磁带存储"): ("磁带库", None),
    ("存储设备", "SAN交换机"): ("光纤交换机", None),
    ("存储设备", "IB交换机"): ("IB交换机", None),
    # 网络设备
    ("网络设备", "以太网交换机"): ("网络设备", "网络交换机"),
    ("网络设备", "路由器"): ("网络设备", "路由器"),
    ("网络设备", "无线网络设备"): ("网络设备", "无线AP"),
}

PATTERN_BRAND_ALIASES = {
    "HP":           ["HP", "HPE", "惠普", "慧与"],
    "DELL":         ["DELL", "戴尔", "易安信", "EMC"],
    "IBM":          ["IBM", "国际商业机器"],
    "Lenovo":       ["Lenovo", "联想"],
    "H3C":          ["H3C", "新华三", "华三"],
    "HUAWEI":       ["HUAWEI", "Huawei", "华为"],
    "Inspur浪潮":   ["Inspur", "浪潮"],
    "曙光Sugon":    ["曙光", "Sugon"],
}

WIRELESS_CONTROLLER_HINTS = re.compile(r"(WX|^AC$|^WAC|Controller|控制器)", re.IGNORECASE)


def _resolve_wireless_sub(series):
    if series and WIRELESS_CONTROLLER_HINTS.search(series or ""):
        return "无线控制器"
    return "无线AP"


def _seed_lenovo_framework_models(conn):
    """三源合并去重，插入 lenovo_framework_models。"""
    rows = []

    # ── 1) lenovo_classification ─────────────────────────────────────
    if _table_exists(conn, "lenovo_classification"):
        result = conn.execute(sa.text("""
            SELECT id, device_category, brand, series, model, mt_code,
                   end_type, sub_category, notes
              FROM lenovo_classification
        """))
        for r in result:
            rows.append({
                "device_category": r.device_category,
                "brand": r.brand, "series": r.series, "model": r.model,
                "mt_code": r.mt_code, "end_type": r.end_type,
                "sub_category": r.sub_category,
                "source": "classification", "source_ref_id": r.id, "notes": r.notes,
            })

    # ── 2) lenovo_pattern_rule expansion against device_inventory ───
    if _table_exists(conn, "lenovo_pattern_rule") and _table_exists(conn, "device_inventory"):
        rules = conn.execute(sa.text("""
            SELECT id, device_category, brand, pattern_raw, pattern_regex, end_type, notes
              FROM lenovo_pattern_rule
        """)).fetchall()
        for rule in rules:
            aliases = PATTERN_BRAND_ALIASES.get(rule.brand, [rule.brand])
            brand_cond_parts = []
            params = {}
            for i, a in enumerate(aliases):
                key = f"b{i}"
                brand_cond_parts.append(f"manufacturer ILIKE :{key}")
                params[key] = f"%{a}%"
            brand_cond = "(" + " OR ".join(brand_cond_parts) + ")"
            tertiary_filter = ""
            if rule.device_category == "服务器":
                tertiary_filter = "AND secondary_category = '主机设备'"
            elif rule.device_category == "存储":
                tertiary_filter = "AND secondary_category = '存储设备'"
            elif rule.device_category == "磁带库":
                tertiary_filter = "AND tertiary_category = '磁带存储'"
            elif rule.device_category == "小型机":
                tertiary_filter = "AND tertiary_category IN ('小型机','Power服务器')"
            try:
                candidates = conn.execute(sa.text(f"""
                    SELECT id, manufacturer, model_number, device_series
                      FROM device_inventory
                     WHERE primary_category = '硬件'
                       {tertiary_filter}
                       AND {brand_cond}
                       AND model_number IS NOT NULL
                       AND TRIM(model_number) <> ''
                """), params).fetchall()
            except Exception:
                continue
            excl_set = set()
            if rule.notes and "除外:" in rule.notes:
                excl_part = rule.notes.split("除外:", 1)[1].strip()
                excl_set = {x.strip().upper() for x in re.split(r"[/、,]+", excl_part) if x.strip()}
            try:
                regex = re.compile(rule.pattern_regex, re.IGNORECASE)
            except re.error:
                continue
            for c in candidates:
                model_raw = (c.model_number or "").strip()
                model_norm = model_raw.replace(" ", "")
                if not model_norm or not regex.match(model_norm):
                    continue
                if model_norm.upper() in excl_set or model_raw.upper() in excl_set:
                    continue
                rows.append({
                    "device_category": rule.device_category,
                    "brand": c.manufacturer, "series": c.device_series, "model": model_raw,
                    "mt_code": None, "end_type": rule.end_type, "sub_category": None,
                    "source": "pattern_expanded", "source_ref_id": rule.id,
                    "notes": f"来自通配 '{rule.pattern_raw}'",
                })

    # ── 3) device_inventory direct import (end_type stays NULL) ────
    if _table_exists(conn, "device_inventory"):
        dc_rows = conn.execute(sa.text("""
            SELECT id, manufacturer, model_number, device_series,
                   secondary_category, tertiary_category
              FROM device_inventory
             WHERE primary_category = '硬件'
               AND model_number IS NOT NULL
               AND TRIM(model_number) <> ''
        """)).fetchall()
        for r in dc_rows:
            key = ((r.secondary_category or "").strip(), (r.tertiary_category or "").strip())
            if key not in DC_TO_LENOVO_CATEGORY:
                continue
            device_category, sub_category = DC_TO_LENOVO_CATEGORY[key]
            if key[1] == "无线网络设备":
                sub_category = _resolve_wireless_sub(r.device_series)
            rows.append({
                "device_category": device_category,
                "brand": r.manufacturer, "series": r.device_series,
                "model": r.model_number.strip(),
                "mt_code": None, "end_type": None, "sub_category": sub_category,
                "source": "dc_inventory", "source_ref_id": r.id,
                "notes": f"来自 device_inventory.{key[0]}.{key[1]}",
            })

    # ── Dedup ──────────────────────────────────────────────────────
    priority = {"classification": 0, "pattern_expanded": 1, "dc_inventory": 2}

    def sort_key(r):
        return (priority.get(r["source"], 99), 0 if r["end_type"] else 1)

    rows.sort(key=sort_key)
    seen = {}
    for r in rows:
        model_lower = (r["model"] or "").strip().lower()
        if not model_lower:
            continue
        dedup_key = (
            r["device_category"],
            (r["brand"] or "").strip().lower(),
            model_lower,
        )
        if dedup_key in seen:
            continue
        seen[dedup_key] = r

    deduped = list(seen.values())
    if not deduped:
        return 0

    # ── Bulk insert ────────────────────────────────────────────────
    insert_sql = sa.text("""
        INSERT INTO lenovo_framework_models
            (device_category, brand, series, model, mt_code,
             end_type, sub_category, source, source_ref_id, notes, aliases)
        VALUES (:device_category, :brand, :series, :model, :mt_code,
                :end_type, :sub_category, :source, :source_ref_id, :notes, '[]'::jsonb)
        ON CONFLICT (device_category, brand, model) DO NOTHING
    """)
    inserted = 0
    batch = []
    for r in deduped:
        batch.append(r)
        if len(batch) >= 500:
            conn.execute(insert_sql, batch)
            inserted += len(batch)
            batch = []
    if batch:
        conn.execute(insert_sql, batch)
        inserted += len(batch)
    return inserted


# ============================================================
# Upgrade / Downgrade
# ============================================================

def upgrade() -> None:
    conn = op.get_bind()

    # ── 1) lenovo_framework_models 主表 ───────────────────────────
    if not _table_exists(conn, "lenovo_framework_models"):
        op.create_table(
            "lenovo_framework_models",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("device_category", sa.String(32), nullable=False),
            sa.Column("brand", sa.String(128), nullable=True),
            sa.Column("series", sa.String(128), nullable=True),
            sa.Column("model", sa.String(255), nullable=False),
            sa.Column("mt_code", sa.String(64), nullable=True),
            sa.Column("end_type", sa.String(16), nullable=True),
            sa.Column("sub_category", sa.String(32), nullable=True),
            sa.Column("source", sa.String(32), nullable=False, server_default="manual"),
            sa.Column("source_ref_id", sa.Integer, nullable=True),
            sa.Column("aliases", JSONB, nullable=True, server_default=sa.text("'[]'::jsonb")),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True),
                      server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.UniqueConstraint("device_category", "brand", "model", name="uq_lenovo_models"),
        )
        op.create_index("ix_lenovo_framework_models_device_category",
                        "lenovo_framework_models", ["device_category"])
        op.create_index("ix_lenovo_framework_models_brand",
                        "lenovo_framework_models", ["brand"])
        op.create_index("ix_lenovo_framework_models_model",
                        "lenovo_framework_models", ["model"])
        op.create_index("ix_lenovo_models_lookup",
                        "lenovo_framework_models", ["device_category", "model"])
    else:
        # 表已存在（_ensure_columns 兜底过）→ 确保 aliases 列存在
        if not _column_exists(conn, "lenovo_framework_models", "aliases"):
            op.add_column("lenovo_framework_models",
                          sa.Column("aliases", JSONB, nullable=True,
                                    server_default=sa.text("'[]'::jsonb")))

    # ── 2) service_level 加 definition + aliases（SLA 别名解析需要）─
    if _table_exists(conn, "service_level"):
        if not _column_exists(conn, "service_level", "definition"):
            op.add_column("service_level", sa.Column("definition", sa.Text, nullable=True))
        if not _column_exists(conn, "service_level", "aliases"):
            op.add_column("service_level", sa.Column("aliases", JSONB,
                          nullable=True, server_default=sa.text("'[]'::jsonb")))

    # ── 3) Seed lenovo_framework_models ───────────────────────────
    # 仅在表为空时种子，避免重复跑（dev/staging 重复 upgrade 不污染）
    existing = conn.execute(sa.text(
        "SELECT COUNT(*) FROM lenovo_framework_models"
    )).scalar() or 0
    if existing == 0:
        n = _seed_lenovo_framework_models(conn)
        print(f"[004] Seeded {n} rows into lenovo_framework_models")
    else:
        print(f"[004] lenovo_framework_models already has {existing} rows, skip seed")


def downgrade() -> None:
    conn = op.get_bind()
    if _table_exists(conn, "lenovo_framework_models"):
        op.drop_index("ix_lenovo_models_lookup", table_name="lenovo_framework_models")
        op.drop_index("ix_lenovo_framework_models_model", table_name="lenovo_framework_models")
        op.drop_index("ix_lenovo_framework_models_brand", table_name="lenovo_framework_models")
        op.drop_index("ix_lenovo_framework_models_device_category", table_name="lenovo_framework_models")
        op.drop_table("lenovo_framework_models")
    # 注意：service_level 的 definition / aliases 列不回滚（保留用户数据）
