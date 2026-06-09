"""语义匹配回归评测脚本

以 manual_matching_override 表「已确认」记录为黄金集，评测自动匹配
（跳过手动覆盖，_skip_manual_override=True）在「语义抽取开/关」两种模式下
命中正确型号的比例，量化语义改造的收益。

用法：
    cd backend && python -m scripts.eval_semantic_matching
    cd backend && python -m scripts.eval_semantic_matching --show-regress 40
"""
import argparse
import os
import re
import sys

# 允许从 backend 目录直接运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.manual_matching_override import ManualMatchingOverride
from app import matching


def norm(s: str) -> str:
    return re.sub(r"[\s\-_/]+", "", str(s or "")).upper()


def is_hit(predicted: str, expected: str) -> bool:
    """命中判定：预测型号与期望型号去分隔符后互为子串即算命中。"""
    p, e = norm(predicted), norm(expected)
    if not p or not e:
        return False
    return p == e or p in e or e in p


def run(mode_on: bool, records, db):
    os.environ["ENABLE_SEMANTIC_MATCH"] = "1" if mode_on else "0"
    hits, results = 0, []
    for r in records:
        res = matching.match_device(
            db=db,
            manufacturer=r.original_manufacturer or "",
            model=r.original_model or "",
            category=None,
            source=r.data_source or "datacenter",
            _skip_manual_override=True,
        )
        predicted = res.get("matched_model") or ""
        ok = is_hit(predicted, r.matched_model_number)
        if ok:
            hits += 1
        results.append((r, predicted, ok))
    return hits, results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show-regress", type=int, default=0,
                    help="打印关→开后由命中变未命中(回归)及由未命中变命中(改善)的样例数")
    ap.add_argument("--sample", type=int, default=0,
                    help="随机抽样 N 条评测（0=全量）。设备库很大时用于快速出信号")
    ap.add_argument("--seed", type=int, default=42, help="抽样随机种子")
    args = ap.parse_args()

    db = SessionLocal()
    records = (
        db.query(ManualMatchingOverride)
        .filter(ManualMatchingOverride.is_confirmed == True)
        .all()
    )
    if args.sample and args.sample < len(records):
        import random
        random.seed(args.seed)
        records = random.sample(records, args.sample)
    n = len(records)
    print(f"黄金集（已确认手动匹配）: {n} 条\n")

    off_hits, off_res = run(False, records, db)
    on_hits, on_res = run(True, records, db)

    print(f"{'语义关闭(基线)':<16} 命中 {off_hits}/{n} = {off_hits / n * 100:.1f}%")
    print(f"{'语义开启':<18} 命中 {on_hits}/{n} = {on_hits / n * 100:.1f}%")
    delta = (on_hits - off_hits) / n * 100
    print(f"{'净提升':<18} {delta:+.1f} pp（{on_hits - off_hits:+d} 条）\n")

    # 对比逐条变化
    improved, regressed = [], []
    for (r, p_off, ok_off), (_, p_on, ok_on) in zip(off_res, on_res):
        if (not ok_off) and ok_on:
            improved.append((r, p_off, p_on))
        elif ok_off and (not ok_on):
            regressed.append((r, p_off, p_on))

    print(f"改善(关漏→开中): {len(improved)} 条 | 回归(关中→开漏): {len(regressed)} 条")

    if args.show_regress:
        k = args.show_regress
        print(f"\n── 改善样例 TOP{k} ──")
        for r, p_off, p_on in improved[:k]:
            print(f"  [{(r.original_manufacturer or '')[:6]:6}] {r.original_model[:38]:38} 期望:{r.matched_model_number[:18]:18} 关:{p_off[:14]:14} 开:{p_on}")
        if regressed:
            print(f"\n── 回归样例（需关注）TOP{k} ──")
            for r, p_off, p_on in regressed[:k]:
                print(f"  [{(r.original_manufacturer or '')[:6]:6}] {r.original_model[:38]:38} 期望:{r.matched_model_number[:18]:18} 关:{p_off[:14]:14} 开:{p_on}")

    db.close()


if __name__ == "__main__":
    main()
