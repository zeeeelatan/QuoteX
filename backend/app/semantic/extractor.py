"""语义字段抽取器

把原始型号写法拆解为：品牌 / 设备类型 / 型号核心串 / 配置。
核心串(core)是后续相似度匹配的主键；品牌(brand)作独立校验维度。

设计要点：
- 纯规则 + 词典，确定性强、零延迟、可离线、批量不卡。
- 词典 = 种子常量(dictionaries.py) + 运行期从 semantic_noise_term 表加载的已审核动态词。
- 通过环境变量 ENABLE_SEMANTIC_MATCH 灰度开关，异常自动退回原逻辑（见 matching.py）。
"""
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Optional

from sqlalchemy.orm import Session

from app.semantic import dictionaries as D


@dataclass
class SemanticFields:
    brand: str = ""          # 标准化品牌名，如 "华为/HUAWEI"（供品牌校验）
    brand_raw: str = ""      # 命中的原始品牌词，如 "HUAWEI" / "华为"
    brand_source: str = ""   # 品牌来源: word(品牌词) / series(系列反推) / input(入参) / ""
    device_type: str = ""    # 设备类型词，如 "交换机"
    series: str = ""         # 系列名，如 "POWEREDGE"
    core: str = ""           # 型号核心串（系列已剥离），如 "S5720"  ← 匹配主键
    core_with_series: str = ""  # 保留系列名的核心串（弱信号，匹配兜底用）
    config: str = ""         # 被剥离的配置串（调试/审计用）
    raw: str = ""            # 原始输入

    def to_dict(self) -> dict:
        return {
            "brand": self.brand,
            "brand_raw": self.brand_raw,
            "brand_source": self.brand_source,
            "device_type": self.device_type,
            "series": self.series,
            "core": self.core,
            "config": self.config,
            "raw": self.raw,
        }


def is_semantic_enabled() -> bool:
    """语义匹配灰度开关，默认开启。设 ENABLE_SEMANTIC_MATCH=0 可关闭。"""
    return os.getenv("ENABLE_SEMANTIC_MATCH", "1").strip() not in ("0", "false", "False", "")


@lru_cache(maxsize=1)
def _dynamic_terms_cache_key() -> int:
    # 占位：lru_cache 需要可哈希 key；实际动态词按 db 实时查询并在调用层缓存。
    return 0


def _load_dynamic_type_terms(db: Optional[Session]) -> List[str]:
    """从 semantic_noise_term 表加载已审核通过(status='approved')的设备类型/噪声词。
    表不存在时（第1步尚未迁移）静默返回空列表，保证向后兼容。
    """
    if db is None:
        return []
    try:
        from app.models.semantic_noise_term import SemanticNoiseTerm
        rows = (
            db.query(SemanticNoiseTerm.term)
            .filter(SemanticNoiseTerm.status == "approved")
            .all()
        )
        return [r[0] for r in rows if r[0]]
    except Exception:
        return []


def _strip_config(s: str) -> tuple:
    """剥离配置参数：括号/反斜杠及其后内容、端口数、容量等。
    返回 (清洗后字符串, 被剥离的配置串)。

    经 634 条样本验证：型号核心总在最前，括号 ( （ 或反斜杠 \\ 一旦出现，
    其后基本都是硬件配置描述（CPU/内存/容量/端口）。因此从第一个 ( （ \\
    处整体截断，比逐段剥离更干净（可正确处理嵌套括号 R740(Intel(R)...) ）。
    """
    config_parts = []

    # 1) 从第一个 ( （ \ 处截断，其后视为配置
    m = re.search(r"[\(（\\]", s)
    if m:
        config_parts.append(s[m.start():])
        s = s[: m.start()]

    # 2) 端口数 48Ports / 24 Port
    s = re.sub(r"\d+\s*Ports?\b", lambda m: config_parts.append(m.group(0)) or " ", s, flags=re.I)

    # 3) 容量 2.4TB / 900GB / 512缓存
    s = re.sub(r"\d+(?:\.\d+)?\s*[TGM]B\b", lambda m: config_parts.append(m.group(0)) or " ", s, flags=re.I)
    s = re.sub(r"\d+\s*缓存", lambda m: config_parts.append(m.group(0)) or " ", s)

    return s, " ".join(config_parts).strip()


def _pop_terms(s: str, terms: List[str], glue_prefix: bool = False) -> tuple:
    """从字符串中剥离命中的词（长词优先，terms 须已按长度倒序）。
    返回 (剩余字符串, 命中词列表)。中文词直接替换，英文词按词边界替换。

    glue_prefix=True 时，英文词允许与后续字母数字粘连（仅要求前边界），
    用于剥离与型号粘连的系列前缀，如 "ThinkSystemSR650" → "SR650"。
    仅在剥离后仍剩余 ≥2 个字母数字时才生效，避免把整串吃光。
    """
    hit = []
    for t in terms:
        if not t:
            continue
        if re.search(r"[A-Za-z]", t):
            # 英文词：词边界匹配，避免 HP 误伤 HPStorage 之类（但允许 DELL-MD1420）
            pattern = r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])"
            new_s, n = re.subn(pattern, " ", s, flags=re.I)
            if not n and glue_prefix:
                # 粘连前缀：前有边界、后紧跟字母数字，且剥离后仍有实质残留
                glue_pat = r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?=[A-Za-z0-9])"
                cand, cn = re.subn(glue_pat, " ", s, count=1, flags=re.I)
                if cn and len(re.sub(r"[^A-Za-z0-9]", "", cand)) >= 2:
                    new_s, n = cand, cn
        else:
            # 中文词：直接子串替换
            if t in s:
                new_s, n = s.replace(t, " "), 1
            else:
                new_s, n = s, 0
        if n:
            hit.append(t)
            s = new_s
    return s, hit


def _normalize_core(s: str) -> str:
    """归一化型号核心串：压缩空白、去首尾分隔符。保留型号内部的 - _ / 数字字母。"""
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip(" -_/")
    return s


def _strip_config_tokens(s: str) -> str:
    """按 token 剥离纯配置词（INTEL/XEON/GB/SFF/TYPE...），不误伤型号核心。"""
    tokens = re.split(r"(\s+)", s)  # 保留分隔
    kept = []
    for tok in tokens:
        bare = re.sub(r"[^A-Za-z0-9]", "", tok).upper()
        if bare and bare in D.CONFIG_TOKENS:
            kept.append(" ")
        else:
            kept.append(tok)
    return "".join(kept)


def extract_fields(
    raw_model: str,
    raw_manufacturer: str = "",
    db: Optional[Session] = None,
    normalize_manufacturer=None,
) -> SemanticFields:
    """抽取语义字段。

    参数：
    - raw_model: 原始型号写法
    - raw_manufacturer: 入参品牌（Excel 品牌列，可空）
    - db: 数据库会话（用于查 manufacturer 字典表 + 动态词典）
    - normalize_manufacturer: 可选的品牌标准化函数（来自 matching，避免循环依赖）
    """
    fields = SemanticFields(raw=str(raw_model or ""))
    s = str(raw_model or "").strip()
    if not s:
        return fields

    # 0) 入参品牌优先记录（最可信）
    if raw_manufacturer and str(raw_manufacturer).strip():
        fields.brand_raw = str(raw_manufacturer).strip()
        fields.brand_source = "input"
        if normalize_manufacturer:
            try:
                fields.brand = normalize_manufacturer(raw_manufacturer, db=db)
            except Exception:
                fields.brand = fields.brand_raw
        else:
            fields.brand = fields.brand_raw

    # 1) 剥配置噪声（括号/反斜杠/端口/容量）
    s, fields.config = _strip_config(s)

    # 2) 剥设备类型词（中文复合词 + 修饰词）+ 动态审核词
    type_terms = D.DEVICE_TYPE_TERMS + _load_dynamic_type_terms(db)
    type_terms = sorted(set(type_terms), key=len, reverse=True)
    s, type_hits = _pop_terms(s, type_terms)
    if type_hits:
        fields.device_type = type_hits[0]
    s, _ = _pop_terms(s, D.MODIFIER_TERMS)

    # 3) 剥品牌词（中文 + 英文），并识别品牌
    s, cn_brand_hits = _pop_terms(s, D.BRAND_TERMS_CN)
    s, en_brand_hits = _pop_terms(s, D.BRAND_TERMS_EN)
    brand_word = (cn_brand_hits + en_brand_hits)[0] if (cn_brand_hits or en_brand_hits) else ""
    if brand_word and fields.brand_source != "input":
        fields.brand_raw = brand_word
        fields.brand_source = "word"
        if normalize_manufacturer:
            try:
                fields.brand = normalize_manufacturer(brand_word, db=db)
            except Exception:
                fields.brand = brand_word
        else:
            fields.brand = brand_word

    # 4) 剥系列名（记录，并在无品牌时用系列反推品牌作弱信号）
    #    先保存「含系列」的版本作为弱信号，再剥离得到默认核心串。
    s_with_series = s
    s, series_hits = _pop_terms(s, D.SERIES_TERMS, glue_prefix=True)
    if series_hits:
        fields.series = series_hits[0].upper()
        if not fields.brand:
            inferred = D.SERIES_BRAND_MAP.get(fields.series)
            if inferred:
                fields.brand = inferred
                fields.brand_source = "series"

    # 5) 剥剩余的纯配置 token，剩下即型号核心串
    fields.core = _normalize_core(_strip_config_tokens(s))
    if series_hits:
        # 含系列的弱信号核心串（如 DB 型号保留 "EliteBook X Flip" 的场景）
        fields.core_with_series = _normalize_core(_strip_config_tokens(s_with_series))

    # 兜底：若核心串被清空（如纯品牌+类型无型号），保留系列名作为弱核心
    if not fields.core and fields.series:
        fields.core = fields.series

    return fields
