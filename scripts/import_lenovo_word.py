#!/usr/bin/env python3
r"""联想框架报价 Word 兜底通配规则导入脚本

输入文件: data/多品牌机型分类及价格清单（葛凡成提供）.docx

只导入 x86 服务器规则；存储部分按业务决定以新表 L1/L2/M 为准，
故 Word 中的"低端控制柜/中端控制柜/扩展柜"规则不入库。

通配语法支持：
- `*`  → `\w*` （匹配 0..N 个字母数字）
- `**` → `\w{2,}`
- `/` 在同一品牌端型内分隔多个 pattern
- `31*-36*` 自动展开为 31\w*, 32\w*, ..., 36\w*
- 括号中的"除XXX" 提取为 exclusion，落到 notes 字段（暂不做反向匹配）
"""
import os
import re
import sys
import zipfile
from typing import Iterable, List, Tuple
from xml.etree import ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from app.database import SessionLocal, engine, Base  # noqa: E402
from app.models.lenovo_framework import LenovoPatternRule  # noqa: E402

DEFAULT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "多品牌机型分类及价格清单（葛凡成提供）.docx",
)

WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _read_word_tables(path: str) -> List[List[List[str]]]:
    """读取 docx 中所有表格 → [tables[rows[cells]]]"""
    with zipfile.ZipFile(path) as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)

    def get_text(elem) -> str:
        return "".join(t.text or "" for t in elem.iter(f"{{{WORD_NS['w']}}}t"))

    tables: List[List[List[str]]] = []
    body = tree.getroot().find("w:body", WORD_NS)
    for tbl in body.findall("w:tbl", WORD_NS):
        rows: List[List[str]] = []
        for tr in tbl.findall("w:tr", WORD_NS):
            row = [get_text(tc) for tc in tr.findall("w:tc", WORD_NS)]
            rows.append(row)
        tables.append(rows)
    return tables


# ---------- 通配 → 正则 ----------

_PRIORITY_BASE = 100


def _wildcard_to_regex(token: str) -> str:
    r"""将单个 `*` 通配 token 转为正则片段（不加锚点）

    `*` → `\w*`， `**` → `\w{2,}`， `***` → `\w{3,}`
    其他字符用 re.escape
    """
    out = []
    i = 0
    while i < len(token):
        if token[i] == "*":
            # count consecutive *
            j = i
            while j < len(token) and token[j] == "*":
                j += 1
            n = j - i
            if n == 1:
                out.append(r"\w*")
            else:
                out.append(r"\w{" + str(n) + r",}")
            i = j
        else:
            out.append(re.escape(token[i]))
            i += 1
    return "".join(out)


def _expand_range(token: str) -> List[str]:
    """展开 `31*-36*` / `RH5***-8***` / `X36**-X37**` 形式的范围。

    返回元素是带 `*` 的字符串（后续再经 _wildcard_to_regex 处理）。
    """
    # HEAD_a? NUM_a TAIL_a - HEAD_b? NUM_b TAIL_b
    # 仅当两边 head 相同（或一边为空）时才展开
    m = re.match(r"^([A-Za-z]*)(\d+)(\*+)-([A-Za-z]*)(\d+)(\*+)$", token)
    if not m:
        return [token]
    head_a, num_a, tail_a, head_b, num_b, tail_b = m.groups()
    if head_a and head_b and head_a != head_b:
        return [token]
    head = head_a or head_b
    a = int(num_a)
    b = int(num_b)
    if a > b or len(num_a) != len(num_b):
        return [token]
    tail = tail_a if tail_a == tail_b else tail_a
    return [f"{head}{n}{tail}" for n in range(a, b + 1)]


_EXCLUDE_RE = re.compile(r"除\s*([A-Za-z0-9*]+)")


def _split_patterns_from_cell(cell_text: str) -> Iterable[Tuple[str, List[str]]]:
    """切分单元格文本 → [(pattern_raw, exclusions)]

    工作策略：
    1) 抽取括号里的"除X"作为 exclusion；剥括号用空格替换
    2) 在 `*ProLiant` 这种粘连边界插入空格
    3) 用 `/` 切分；对每段尝试 `range` 展开
    4) 纯字母短 token (≤3) 视为系列前缀通配；长描述（ProLiant 等）跳过
    """
    exclusions = _EXCLUDE_RE.findall(cell_text)

    # 剥括号用空格替换（避免 "DL36*ProLiant" 粘连）
    text = re.sub(r"[（(][^（()）]*[)）]", " ", cell_text)
    text = re.sub(r"[，、\n]+", " ", text)
    text = text.replace("系列", " ")
    # 在 "*字母" 边界插入空格
    text = re.sub(r"(\*+)([A-Za-z])", r"\1 \2", text)

    raw_tokens = [t.strip() for t in re.split(r"\s+", text) if t.strip()]

    for tok in raw_tokens:
        # 跳过纯通配的孤立 token（如 'xSeries *' 拆出来的 '*'），它会把所有型号都匹中
        if set(tok) == {"*"}:
            continue
        # 纯字母 token（不含数字、*）
        if not re.search(r"[\d*]", tok):
            if len(tok) <= 3:
                # 短字母作为系列前缀（如 ML、BL、TS、HR、SE）
                yield tok + "*", exclusions
            # 长描述 ProLiant / BladeSystem / PowerEdge / ThinkSystem 等 跳过
            continue

        if "/" not in tok:
            for expanded in _expand_range(tok):
                yield expanded, exclusions
            continue

        # 形如 'DL12*/14*/16*/31*-36*' 或 'R2**/3**/4**/XR2/T***/C1100'
        first, *rest = tok.split("/")
        m = re.match(r"^([A-Za-z]+)(.*)$", first)
        head = m.group(1) if m else ""
        first_suffix = m.group(2) if m else first
        atoms = [first_suffix] + rest
        for a in atoms:
            a = a.strip()
            if not a or set(a) == {"*"}:
                continue
            # atom 自带字母前缀 → 不加 head（如 XR2、C1100）
            if re.match(r"^[A-Za-z]", a):
                for expanded in _expand_range(a):
                    if set(expanded) == {"*"}:
                        continue
                    yield expanded, exclusions
            else:
                for expanded in _expand_range(a):
                    yield head + expanded, exclusions


def _compile_pattern(raw_token: str) -> str:
    """raw token (含 `*`) → 完整正则字符串（带 ^ 锚点，忽略大小写另作处理）"""
    body = _wildcard_to_regex(raw_token)
    return "^" + body + r"$"


# ---------- 主导入 ----------

_X86_BRAND_ROW_OFFSET = 1   # x86服务器 块的起始行（跳过表头行 0）

def import_server_patterns(db, table):
    """table = 第一个 docx 表格（既含 x86 又含 存储）"""
    # 第 0 行是表头：（空）|低端|中端|高端
    # 之后是 x86服务器 行（col0='x86服务器'）+ 多个品牌行（col0 空，col1=品牌）
    # 然后是 存储 行（col0='存储' 或 col0 空 + col1=品牌, col2/3/4=控制柜分类）

    end_type_cols = {2: "低端", 3: "中端", 4: "高端"}
    in_storage = False
    count = 0
    skipped_storage = 0

    for r_idx, row in enumerate(table[1:], start=1):
        if not row:
            continue
        first = (row[0] or "").strip()
        second = (row[1] or "").strip() if len(row) > 1 else ""
        # 存储 section 的两种边界：col0='存储' 或 col1 出现 'XXX控制柜'/扩展柜
        if "存储" in first or "控制柜" in second or "扩展柜" in second:
            in_storage = True
        if in_storage:
            skipped_storage += 1
            continue

        # 品牌：跳过 'x86服务器' 标签自身
        brand = second
        if not brand or brand in {"x86服务器", "低端", "中端", "高端"}:
            continue

        for col_idx, end_type in end_type_cols.items():
            if col_idx >= len(row):
                continue
            cell_text = row[col_idx] or ""
            if not cell_text.strip():
                continue
            seen = set()
            for raw, exclusions in _split_patterns_from_cell(cell_text):
                if raw in seen:
                    continue
                seen.add(raw)
                regex = _compile_pattern(raw)
                # 验证 regex 可编译
                try:
                    re.compile(regex, re.IGNORECASE)
                except re.error:
                    print(f"  ⚠️  跳过非法正则: {brand}/{end_type}/{raw} -> {regex}")
                    continue
                db.add(LenovoPatternRule(
                    device_category="服务器",
                    brand=brand,
                    pattern_raw=raw,
                    pattern_regex=regex,
                    end_type=end_type,
                    priority=_PRIORITY_BASE,
                    notes=("除外: " + "/".join(exclusions)) if exclusions else None,
                ))
                count += 1
    print(f"[Word服务器规则] 导入 {count} 条；跳过存储 {skipped_storage} 行（以 Excel 新表为准）")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE
    if not os.path.exists(path):
        print(f"错误：文件不存在 {path}")
        sys.exit(1)

    print(f"=== 联想框架 Word 兜底规则导入 ===")
    print(f"Word: {path}")
    print()

    Base.metadata.create_all(bind=engine, tables=[
        Base.metadata.tables["lenovo_pattern_rule"],
    ])

    tables = _read_word_tables(path)
    if not tables:
        print("Word 内未发现表格")
        sys.exit(1)

    db = SessionLocal()
    try:
        db.query(LenovoPatternRule).delete()
        db.flush()
        import_server_patterns(db, tables[0])
        db.commit()
        print("\n✅ 导入完成")
    except Exception as e:
        db.rollback()
        print(f"\n❌ 导入失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
