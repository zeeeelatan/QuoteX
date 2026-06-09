"""词典挖掘器

从 manual_matching_override 已确认记录中挖掘「设备类型/噪声词」候选：
对每条记录，原始型号去掉(匹配型号核心 + 品牌词)后剩下的 token 即噪声候选，
按频次累计写入 semantic_noise_term 表（status='pending'，待人工审核）。

闭环：用户每确认一条手动匹配，都为词典贡献样本，词典越用越准。
"""
import re
from collections import Counter
from typing import Dict

from sqlalchemy.orm import Session

from app.models.manual_matching_override import ManualMatchingOverride
from app.models.semantic_noise_term import SemanticNoiseTerm
from app.semantic import dictionaries as D


def _norm(s: str) -> str:
    return re.sub(r"[\s\-_/]+", "", str(s or "")).upper()


def _brand_words() -> set:
    words = set()
    for w in D.BRAND_TERMS_CN + D.BRAND_TERMS_EN:
        words.add(w.upper())
    return words


# 已在种子词典/配置词集里的词，挖掘时跳过（避免重复提示已能处理的词）
def _seed_terms() -> set:
    seed = set()
    for t in (D.DEVICE_TYPE_TERMS + D.MODIFIER_TERMS + D.SERIES_TERMS
              + D.BRAND_TERMS_CN + D.BRAND_TERMS_EN):
        seed.add(t.upper())
    seed |= {c.upper() for c in D.CONFIG_TOKENS}
    return seed


# 英文候选最低频次（中文设备类型词较可信，阈值更低）
_MIN_FREQ_EN = 4
_MIN_FREQ_CN = 2


def mine_terms(db: Session) -> Dict[str, int]:
    """执行一次挖掘，返回摘要统计。"""
    brand_words = _brand_words()
    seed = _seed_terms()

    records = (
        db.query(ManualMatchingOverride)
        .filter(ManualMatchingOverride.is_confirmed == True)
        .all()
    )

    cn_counter: Counter = Counter()
    en_counter: Counter = Counter()

    for r in records:
        om = r.original_model or ""
        core_n = _norm(r.matched_model_number)

        # 中文连续片段 → 设备类型/噪声候选
        for seg in re.findall(r"[一-龥]+", om):
            if seg.upper() in seed:
                continue
            cn_counter[seg] += 1

        # 英文 token（≥2 字母）→ 系列/类型候选，排除品牌与型号核心
        for seg in re.findall(r"[A-Za-z]{2,}", om):
            u = seg.upper()
            if u in brand_words or u in seed:
                continue
            if core_n and _norm(u) and _norm(u) in core_n:
                continue  # 属于型号核心串，不是噪声
            en_counter[u] += 1

    candidates = []
    for term, freq in cn_counter.items():
        if freq >= _MIN_FREQ_CN:
            candidates.append((term, freq, "device_type", "cn"))
    for term, freq in en_counter.items():
        if freq >= _MIN_FREQ_EN:
            # 英文候选统一作设备类型/噪声词消费（采纳后进剥离词典）
            candidates.append((term, freq, "device_type", "en"))

    new_cnt, upd_cnt = 0, 0
    for term, freq, term_type, lang in candidates:
        existing = (
            db.query(SemanticNoiseTerm)
            .filter(SemanticNoiseTerm.term == term)
            .first()
        )
        if existing:
            # 已存在：仅刷新频次，不改变人工审核状态
            if existing.frequency != freq:
                existing.frequency = freq
                upd_cnt += 1
        else:
            db.add(SemanticNoiseTerm(
                term=term, term_type=term_type, lang=lang,
                frequency=freq, status="pending", source="miner",
            ))
            new_cnt += 1
    db.commit()

    total_pending = (
        db.query(SemanticNoiseTerm)
        .filter(SemanticNoiseTerm.status == "pending")
        .count()
    )
    return {
        "scanned_records": len(records),
        "new_candidates": new_cnt,
        "updated_candidates": upd_cnt,
        "total_pending": total_pending,
    }
