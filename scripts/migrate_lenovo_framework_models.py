"""联想框架机型库迁移脚本

将 3 个来源的数据合并到 lenovo_framework_models：
  1. lenovo_classification        → source='classification'           （已有 end_type）
  2. lenovo_pattern_rule 展开     → source='pattern_expanded'         （end_type 取自 pattern）
  3. device_inventory             → source='dc_inventory'             （end_type 留空，除非和上面去重命中）
  4. office_device_inventory      → 不导入（不在联想框架覆盖范围）

去重策略：
  (device_category, lower(brand), lower(model)) 唯一。
  优先级：classification > pattern_expanded > dc_inventory，
  已存在则保留先到记录（已有 end_type 优先），不被后到的 NULL end_type 覆盖。

dry_run=True 时：只输出统计 + 抽样，不写库。
"""
import os
import re
import sys

# 兼容直接从仓库根目录运行：python scripts/migrate_lenovo_framework_models.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.database import engine, Base, SessionLocal
from app.models.lenovo_framework import (
    LenovoClassification,
    LenovoPatternRule,
    LenovoFrameworkModel,
)


# ============================================================
# dc_inventory secondary/tertiary → 联想 device_category 映射
# ============================================================

# (secondary, tertiary) → device_category（无 sub_category 时只填大类）
DC_TO_LENOVO_CATEGORY = {
    # 主机设备
    ("主机设备", "X86服务器"): ("服务器", None),
    ("主机设备", "小型机"): ("小型机", None),
    ("主机设备", "Power服务器"): ("小型机", None),  # IBM Power 业内归小机
    ("主机设备", "ARM服务器"): ("服务器", None),    # end_type 留空
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
    # 无线网络设备需要按 series 二次拆分
    ("网络设备", "无线网络设备"): ("网络设备", "无线AP"),  # 默认 AP，下面再覆盖
}

# 跳过的（不导入）：
SKIPPED = {
    ("主机设备", "Alpha服务器"),
    ("主机设备", "大型机"),
    ("主机设备", "MIPS服务器"),
    ("存储设备", "存储网关"),
    ("存储设备", "光盘存储"),
    ("网络设备", "负载均衡"),
    ("网络设备", "程控交换机"),
    ("网络设备", "光端机"),
    ("网络设备", "光传送"),
    ("网络设备", "光接入"),
    ("网络设备", "物联网控制器"),
}


# 无线设备里 series 判定为"无线控制器"的关键词
WIRELESS_CONTROLLER_HINTS = re.compile(
    r"(WX|^AC$|^WAC|Controller|控制器)",
    re.IGNORECASE,
)


def _resolve_wireless_sub(series: str | None) -> str:
    """无线网络设备 sub_category 判定"""
    if series and WIRELESS_CONTROLLER_HINTS.search(series or ""):
        return "无线控制器"
    return "无线AP"


def _norm(s: str | None) -> str:
    return (s or "").strip().lower()


# ============================================================
# 数据加载
# ============================================================

def load_from_classification(db: Session) -> list[dict]:
    """从 lenovo_classification 加载"""
    rows = db.query(LenovoClassification).all()
    out = []
    for r in rows:
        out.append({
            "device_category": r.device_category,
            "brand": r.brand,
            "series": r.series,
            "model": r.model,
            "mt_code": r.mt_code,
            "end_type": r.end_type,
            "sub_category": r.sub_category,
            "source": "classification",
            "source_ref_id": r.id,
            "notes": r.notes,
        })
    return out


# pattern_rule.brand → dc_inventory.manufacturer 可能的别名（每条都是 ILIKE '%xxx%' 之一）
PATTERN_BRAND_ALIASES = {
    "HP": ["HP", "HPE", "惠普", "慧与"],
    "DELL": ["DELL", "戴尔", "易安信", "EMC"],
    "IBM": ["IBM", "国际商业机器"],
    "Lenovo": ["Lenovo", "联想"],
    "H3C": ["H3C", "新华三", "华三"],
    "HUAWEI": ["HUAWEI", "Huawei", "华为"],
    "Inspur浪潮": ["Inspur", "浪潮"],
    "曙光Sugon": ["曙光", "Sugon"],
}


def _brand_alias_filter(brand: str) -> tuple[str, dict]:
    """生成 brand alias OR ILIKE 条件 + 参数字典"""
    aliases = PATTERN_BRAND_ALIASES.get(brand, [brand])
    conds = []
    params = {}
    for i, a in enumerate(aliases):
        key = f"b{i}"
        conds.append(f"manufacturer ILIKE :{key}")
        params[key] = f"%{a}%"
    return "(" + " OR ".join(conds) + ")", params


def load_from_pattern_expanded(db: Session) -> list[dict]:
    """从 lenovo_pattern_rule 展开：对每条 pattern，去 device_inventory 找 model 命中 pattern_regex 的"""
    rules = db.query(LenovoPatternRule).all()
    out = []
    expanded_by_rule: dict[str, int] = {}

    for rule in rules:
        brand_cond, params = _brand_alias_filter(rule.brand)
        # 只看相关大类对应的 dc tertiary（避免拉太多无关数据）
        # 服务器 → 主机设备/X86服务器/小型机/...；这里偷懒：服务器大类去主机设备拉
        tertiary_filter = ""
        if rule.device_category == "服务器":
            tertiary_filter = "AND secondary_category = '主机设备'"
        elif rule.device_category == "存储":
            tertiary_filter = "AND secondary_category = '存储设备'"
        elif rule.device_category == "磁带库":
            tertiary_filter = "AND tertiary_category = '磁带存储'"
        elif rule.device_category == "小型机":
            tertiary_filter = "AND tertiary_category IN ('小型机','Power服务器')"
        # 网络/光纤/IB 暂不处理（pattern 主要覆盖服务器）

        sql = text(f"""
            SELECT id, manufacturer, model_number, device_series
            FROM device_inventory
            WHERE primary_category = '硬件'
              {tertiary_filter}
              AND {brand_cond}
              AND model_number IS NOT NULL
              AND TRIM(model_number) <> ''
        """)
        candidates = db.execute(sql, params).fetchall()

        # 排除列表（pattern 通常会带"除外:"）
        excl_set: set[str] = set()
        if rule.notes and "除外:" in rule.notes:
            excl_part = rule.notes.split("除外:", 1)[1].strip()
            excl_set = {
                x.strip().upper()
                for x in re.split(r"[/、,]+", excl_part) if x.strip()
            }

        # Python 端 regex 匹配（dc.model_number 通常带空格，要先去空格）
        try:
            regex = re.compile(rule.pattern_regex, re.IGNORECASE)
        except re.error as e:
            print(f"  ⚠️ pattern '{rule.pattern_raw}' regex 错误: {e}")
            continue

        matched_count = 0
        for row in candidates:
            model_raw = (row.model_number or "").strip()
            model_norm = model_raw.replace(" ", "")
            if not model_norm:
                continue
            if not regex.match(model_norm):
                continue
            if model_norm.upper() in excl_set or model_raw.upper() in excl_set:
                continue
            out.append({
                "device_category": rule.device_category,
                "brand": row.manufacturer,
                "series": row.device_series,
                "model": model_raw,
                "mt_code": None,
                "end_type": rule.end_type,
                "sub_category": None,
                "source": "pattern_expanded",
                "source_ref_id": rule.id,
                "notes": f"来自通配 '{rule.pattern_raw}'",
            })
            matched_count += 1

        if matched_count > 0:
            expanded_by_rule[rule.pattern_raw] = matched_count

    if expanded_by_rule:
        print(f"  ✓ 命中通配的规则数：{len(expanded_by_rule)}")
        # 抽样前 5 个
        for raw, cnt in list(expanded_by_rule.items())[:5]:
            print(f"     {raw:20s} → {cnt} 条")
    return out


def load_from_dc_inventory(db: Session) -> list[dict]:
    """从 device_inventory 按映射表导入（end_type 留空）"""
    out = []
    skip_seen = 0

    # 一次性拿出所有 hardware 行
    sql = text("""
        SELECT id, manufacturer, model_number, device_series,
               secondary_category, tertiary_category
        FROM device_inventory
        WHERE primary_category = '硬件'
          AND model_number IS NOT NULL
          AND TRIM(model_number) <> ''
    """)
    rows = db.execute(sql).fetchall()
    for r in rows:
        sec = (r.secondary_category or "").strip()
        ter = (r.tertiary_category or "").strip()
        key = (sec, ter)
        if key in SKIPPED:
            skip_seen += 1
            continue
        if key not in DC_TO_LENOVO_CATEGORY:
            # 不在主流大类（如 主机设备/其它子类、安全设备 等），跳过
            continue
        device_category, sub_category = DC_TO_LENOVO_CATEGORY[key]

        # 无线网络设备特殊：按 series 二次拆分
        if ter == "无线网络设备":
            sub_category = _resolve_wireless_sub(r.device_series)

        out.append({
            "device_category": device_category,
            "brand": r.manufacturer,
            "series": r.device_series,
            "model": r.model_number.strip(),
            "mt_code": None,
            "end_type": None,  # 留空，由用户报价时手动选择
            "sub_category": sub_category,
            "source": "dc_inventory",
            "source_ref_id": r.id,
            "notes": f"来自 device_inventory.{sec}.{ter}",
        })
    return out


# ============================================================
# 主流程：合并 + 去重 + dry-run / 入库
# ============================================================

def dedupe(rows: list[dict]) -> list[dict]:
    """同 (device_category, lower(brand), lower(model)) 去重。
    优先保留：有 end_type 的、source 优先级（classification > pattern_expanded > dc_inventory）。
    """
    priority = {"classification": 0, "pattern_expanded": 1, "dc_inventory": 2}

    def sort_key(r):
        return (
            priority.get(r["source"], 99),
            0 if r["end_type"] else 1,  # 有 end_type 排前面
        )

    rows_sorted = sorted(rows, key=sort_key)
    seen = {}
    for r in rows_sorted:
        key = (r["device_category"], _norm(r["brand"]), _norm(r["model"]))
        if not r["model"] or not key[2]:
            continue
        if key in seen:
            continue
        seen[key] = r
    return list(seen.values())


def main(dry_run: bool = True):
    db = SessionLocal()
    try:
        # 表存在性：自动 create_all
        Base.metadata.create_all(bind=engine, tables=[LenovoFrameworkModel.__table__])

        print("=" * 70)
        print("📦 联想框架机型库 - 数据迁移")
        print("=" * 70)

        # 1. 从 classification
        rows_cls = load_from_classification(db)
        print(f"\n[1/3] lenovo_classification        → {len(rows_cls)} 条")

        # 2. 从 pattern_expanded
        rows_pat = load_from_pattern_expanded(db)
        print(f"[2/3] lenovo_pattern_rule 展开     → {len(rows_pat)} 条")

        # 3. 从 dc_inventory
        rows_dc = load_from_dc_inventory(db)
        print(f"[3/3] device_inventory（按映射表） → {len(rows_dc)} 条")

        all_rows = rows_cls + rows_pat + rows_dc
        deduped = dedupe(all_rows)

        print(f"\n→ 合并前 {len(all_rows)} 条，去重后 {len(deduped)} 条\n")

        # 按 source 拆分统计
        by_source: dict[str, int] = {}
        for r in deduped:
            by_source[r["source"]] = by_source.get(r["source"], 0) + 1
        print("📊 入库后预期 source 分布：")
        for k, v in sorted(by_source.items()):
            print(f"     {k:22s} {v:6d}")

        # end_type 缺失统计
        missing_endtype = [r for r in deduped if not r["end_type"]]
        print(f"\n⚠️  end_type 留空 → 待人工：{len(missing_endtype)} 条 "
              f"({len(missing_endtype) * 100 // max(len(deduped), 1)}%)")

        # 按 device_category 拆分
        print("\n📊 按设备大类分布（含/不含 end_type）：")
        cat_stat: dict[str, dict[str, int]] = {}
        for r in deduped:
            c = cat_stat.setdefault(r["device_category"], {"with": 0, "without": 0})
            c["with" if r["end_type"] else "without"] += 1
        for k in sorted(cat_stat.keys()):
            v = cat_stat[k]
            total = v["with"] + v["without"]
            print(f"     {k:12s} 总 {total:5d} / 已有端型 {v['with']:5d} / 待人工 {v['without']:5d}")

        # 抽样
        print("\n🔍 抽样 10 条（混合来源）：")
        import random
        for r in random.sample(deduped, min(10, len(deduped))):
            print(f"     [{r['source']:18s}] {r['device_category']:8s} | "
                  f"{(r['brand'] or '-')[:14]:14s} | {r['model'][:30]:30s} | "
                  f"end_type={r['end_type'] or '(空)'}")

        if dry_run:
            print("\n💡 dry_run=True，未写入数据库。")
            print("   确认无误后运行: python scripts/migrate_lenovo_framework_models.py --commit")
            return

        # 正式入库
        print("\n💾 写入数据库...")
        db.query(LenovoFrameworkModel).delete()
        db.flush()
        for r in deduped:
            db.add(LenovoFrameworkModel(**r))
        db.commit()
        print(f"✅ 已写入 {len(deduped)} 条")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--commit", action="store_true", help="正式写库（默认 dry-run）")
    args = p.parse_args()
    main(dry_run=not args.commit)
