"""
文档解析路由：将 Word (.docx)、PDF、图片等文件中的表格提取为结构化数据。
前端在上传非 Excel 文件时调用此接口，返回与前端 XLSX.js 解析 Excel 相同的
{ headers: [...], data: [...], sheets: [...] } 格式，以便无缝对接后续流程。
"""
import io
import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/document", tags=["文档解析"])

MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB

# Ollama 配置（用于 OCR 后处理）
OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_QUOTE_MODEL", "qwen:latest")


# ──────────────────────────────────────────────
#  响应模型
# ──────────────────────────────────────────────

class SheetData(BaseModel):
    """单个工作表/表格的数据"""
    name: str
    headers: List[str]
    data: List[Dict[str, Any]]

class ParseResponse(BaseModel):
    """文档解析统一响应"""
    success: bool
    file_type: str                     # docx / pdf / image
    sheets: List[SheetData]            # 可能包含多个表格
    selected_sheet: Optional[str] = None
    message: Optional[str] = None


# ──────────────────────────────────────────────
#  Word (.docx) 表格提取
# ──────────────────────────────────────────────

def _parse_docx(content: bytes) -> List[SheetData]:
    """从 .docx 文件中提取所有表格，每个表格作为一个 SheetData 返回。"""
    from docx import Document

    doc = Document(io.BytesIO(content))
    tables = doc.tables
    if not tables:
        raise HTTPException(status_code=400, detail="Word 文档中未找到任何表格，请确认文件包含表格数据。")

    sheets: List[SheetData] = []
    for idx, table in enumerate(tables):
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            rows.append(cells)

        if len(rows) < 2:
            continue  # 跳过只有 0-1 行的表格

        # 第一行作为表头
        headers = rows[0]
        # 去重空表头：如果表头为空，用 "列N" 代替
        headers = [h if h else f"列{i+1}" for i, h in enumerate(headers)]

        data = []
        for row_cells in rows[1:]:
            row_dict = {}
            has_data = False
            for col_idx, header in enumerate(headers):
                value = row_cells[col_idx] if col_idx < len(row_cells) else ""
                row_dict[header] = value
                if value:
                    has_data = True
            if has_data:
                data.append(row_dict)

        if data:
            sheet_name = f"表格{idx + 1}" if len(tables) > 1 else "表格"
            sheets.append(SheetData(name=sheet_name, headers=headers, data=data))

    if not sheets:
        raise HTTPException(status_code=400, detail="Word 文档中的表格为空或仅包含表头，无有效数据行。")

    return sheets


# ──────────────────────────────────────────────
#  PDF 表格提取（文本型 PDF）
# ──────────────────────────────────────────────

def _parse_pdf_tables(content: bytes) -> List[SheetData]:
    """从文本型 PDF 中提取表格。使用 pdfplumber 检测表格边界并提取。"""
    import pdfplumber

    pdf = pdfplumber.open(io.BytesIO(content))
    all_sheets: List[SheetData] = []
    table_counter = 0

    for page_idx, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        if not tables:
            continue

        for table in tables:
            if not table or len(table) < 2:
                continue

            table_counter += 1

            # 第一行作为表头
            raw_headers = table[0]
            headers = []
            for i, h in enumerate(raw_headers):
                h_clean = (h or "").strip().replace("\n", " ")
                headers.append(h_clean if h_clean else f"列{i+1}")

            data = []
            for row in table[1:]:
                row_dict = {}
                has_data = False
                for col_idx, header in enumerate(headers):
                    value = (row[col_idx] or "").strip().replace("\n", " ") if col_idx < len(row) else ""
                    row_dict[header] = value
                    if value:
                        has_data = True
                if has_data:
                    data.append(row_dict)

            if data:
                sheet_name = f"第{page_idx+1}页-表格{table_counter}"
                all_sheets.append(SheetData(name=sheet_name, headers=headers, data=data))

    pdf.close()

    # 如果 pdfplumber 未检测到表格，尝试从文本中推断
    if not all_sheets:
        all_sheets = _parse_pdf_text_fallback(content)

    if not all_sheets:
        raise HTTPException(
            status_code=400,
            detail="PDF 中未检测到表格。如果是扫描件/图片型 PDF，请尝试上传图片格式（PNG/JPG）。"
        )

    return all_sheets


def _parse_pdf_text_fallback(content: bytes) -> List[SheetData]:
    """
    当 pdfplumber 表格检测失败时，尝试从 PDF 纯文本中按行分割来恢复表格结构。
    适用于没有明确表格边界但数据呈行列式排列的 PDF。
    """
    import pdfplumber

    pdf = pdfplumber.open(io.BytesIO(content))
    all_text_lines: List[str] = []
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text_lines.extend(text.strip().split("\n"))
    pdf.close()

    if not all_text_lines:
        return []

    # 尝试检测制表符或多空格分割的表格行
    table_rows: List[List[str]] = []
    for line in all_text_lines:
        line = line.strip()
        if not line:
            continue
        # 尝试按制表符分割
        if "\t" in line:
            cells = [c.strip() for c in line.split("\t")]
        else:
            # 按2个及以上连续空格分割
            cells = [c.strip() for c in re.split(r"\s{2,}", line)]

        if len(cells) >= 2:
            table_rows.append(cells)

    if len(table_rows) < 2:
        return []

    # 统一列数为最常见的列数
    col_counts = {}
    for row in table_rows:
        n = len(row)
        col_counts[n] = col_counts.get(n, 0) + 1
    most_common_cols = max(col_counts, key=col_counts.get)

    # 过滤出列数匹配的行
    filtered_rows = [r for r in table_rows if len(r) == most_common_cols]
    if len(filtered_rows) < 2:
        return []

    headers = filtered_rows[0]
    headers = [h if h else f"列{i+1}" for i, h in enumerate(headers)]

    data = []
    for row in filtered_rows[1:]:
        row_dict = {}
        has_data = False
        for col_idx, header in enumerate(headers):
            value = row[col_idx] if col_idx < len(row) else ""
            row_dict[header] = value
            if value:
                has_data = True
        if has_data:
            data.append(row_dict)

    if data:
        return [SheetData(name="文本提取", headers=headers, data=data)]

    return []


# ──────────────────────────────────────────────
#  图片 OCR 表格提取
# ──────────────────────────────────────────────

def _ocr_available() -> bool:
    """检查 RapidOCR 是否已安装。"""
    try:
        from rapidocr_onnxruntime import RapidOCR  # noqa: F401
        return True
    except ImportError:
        return False


def _parse_image_ocr(content: bytes, filename: str) -> List[SheetData]:
    """
    使用 RapidOCR 识别图片中的文字，然后尝试用 LLM 将其结构化为表格。
    如果 RapidOCR 未安装，返回友好提示。
    """
    if not _ocr_available():
        raise HTTPException(
            status_code=400,
            detail="图片 OCR 功能尚未启用（缺少 rapidocr-onnxruntime 依赖）。请先安装：pip install rapidocr-onnxruntime"
        )

    from rapidocr_onnxruntime import RapidOCR

    ocr = RapidOCR()
    result, _ = ocr(content)

    if not result:
        raise HTTPException(status_code=400, detail="图片中未识别到任何文字内容。")

    # result 格式: [[box, text, score], ...]
    # 按 y 坐标排序，分组为行
    ocr_lines = _group_ocr_to_lines(result)

    if not ocr_lines:
        raise HTTPException(status_code=400, detail="图片中未识别到有效的表格结构。")

    # 尝试直接从 OCR 行中恢复表格结构
    sheets = _ocr_lines_to_table(ocr_lines)

    # 如果直接恢复失败，尝试用 LLM 结构化
    if not sheets:
        raw_text = "\n".join([" | ".join(line) for line in ocr_lines])
        sheets = _llm_structure_text(raw_text, filename)

    if not sheets:
        raise HTTPException(status_code=400, detail="未能从图片中提取出有效的表格数据。")

    return sheets


def _group_ocr_to_lines(ocr_result: list) -> List[List[str]]:
    """将 OCR 识别结果按 y 坐标分组为行。"""
    if not ocr_result:
        return []

    # 提取每个文本块的 y 中心坐标和 x 坐标
    items = []
    for box, text, score in ocr_result:
        if not text or not text.strip():
            continue
        # box 是 4 个角点 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        y_center = (box[0][1] + box[2][1]) / 2
        x_center = (box[0][0] + box[1][0]) / 2
        items.append({"text": text.strip(), "y": y_center, "x": x_center})

    if not items:
        return []

    # 按 y 排序
    items.sort(key=lambda i: i["y"])

    # 分组：y 坐标差在阈值内的视为同一行
    lines: List[List[dict]] = []
    current_line: List[dict] = [items[0]]

    for item in items[1:]:
        if abs(item["y"] - current_line[-1]["y"]) < 15:  # 15px 阈值
            current_line.append(item)
        else:
            lines.append(current_line)
            current_line = [item]
    lines.append(current_line)

    # 每行内按 x 排序，提取文本
    result = []
    for line in lines:
        line.sort(key=lambda i: i["x"])
        result.append([i["text"] for i in line])

    return result


def _ocr_lines_to_table(ocr_lines: List[List[str]]) -> List[SheetData]:
    """尝试将 OCR 分行结果直接恢复为表格（当列数一致时）。"""
    if len(ocr_lines) < 2:
        return []

    # 检查列数是否基本一致
    col_counts = [len(line) for line in ocr_lines]
    most_common = max(set(col_counts), key=col_counts.count)

    if most_common < 2:
        return []

    # 过滤列数匹配的行
    filtered = [line for line in ocr_lines if len(line) == most_common]
    if len(filtered) < 2:
        return []

    headers = filtered[0]
    headers = [h if h else f"列{i+1}" for i, h in enumerate(headers)]

    data = []
    for row in filtered[1:]:
        row_dict = {}
        has_data = False
        for col_idx, header in enumerate(headers):
            value = row[col_idx] if col_idx < len(row) else ""
            row_dict[header] = value
            if value:
                has_data = True
        if has_data:
            data.append(row_dict)

    if data:
        return [SheetData(name="OCR识别", headers=headers, data=data)]
    return []


# ──────────────────────────────────────────────
#  扫描型 PDF → 图片 → OCR
# ──────────────────────────────────────────────

def _pdf2image_available() -> bool:
    """检查 pdf2image 是否已安装。"""
    try:
        from pdf2image import convert_from_bytes  # noqa: F401
        return True
    except ImportError:
        return False


def _parse_scanned_pdf(content: bytes, filename: str) -> List[SheetData]:
    """将扫描型 PDF 转为图片，再用 OCR 识别。"""
    if not _pdf2image_available():
        raise HTTPException(
            status_code=400,
            detail="扫描型 PDF 解析需要安装 pdf2image 和系统依赖 poppler-utils。"
        )
    if not _ocr_available():
        raise HTTPException(
            status_code=400,
            detail="图片 OCR 功能尚未启用（缺少 rapidocr-onnxruntime 依赖）。"
        )

    from pdf2image import convert_from_bytes
    from rapidocr_onnxruntime import RapidOCR

    images = convert_from_bytes(content, dpi=200)
    ocr = RapidOCR()

    all_ocr_lines: List[List[str]] = []
    for img in images:
        # PIL Image → bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        result, _ = ocr(img_bytes)
        if result:
            lines = _group_ocr_to_lines(result)
            all_ocr_lines.extend(lines)

    if not all_ocr_lines:
        raise HTTPException(status_code=400, detail="扫描型 PDF 中未识别到文字内容。")

    sheets = _ocr_lines_to_table(all_ocr_lines)
    if not sheets:
        raw_text = "\n".join([" | ".join(line) for line in all_ocr_lines])
        sheets = _llm_structure_text(raw_text, filename)

    if not sheets:
        raise HTTPException(status_code=400, detail="未能从扫描型 PDF 中提取出有效的表格数据。")

    return sheets


# ──────────────────────────────────────────────
#  LLM 结构化后处理
# ──────────────────────────────────────────────

def _call_ollama(system_prompt: str, user_msg: str, timeout: int = 90) -> Optional[str]:
    """
    统一调用本地 Ollama LLM。
    返回模型回复文本，失败返回 None。
    """
    import requests as req

    url = f"{OLLAMA_BASE.rstrip('/')}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        "stream": False,
    }

    try:
        resp = req.post(url, json=payload, timeout=timeout)
        if resp.status_code != 200:
            logger.warning("Ollama 调用失败: status=%s", resp.status_code)
            return None
        data = resp.json()
        return (data.get("message") or {}).get("content", "").strip()
    except Exception as e:
        logger.warning("Ollama 调用异常: %s", e)
        return None


def _extract_json_from_llm(text: str) -> Optional[dict]:
    """从 LLM 回复中提取 JSON 对象（兼容 markdown 代码块包裹）。"""
    if not text:
        return None
    # 去除可能的 markdown 代码块标记
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # 尝试从文本中提取第一个 JSON 对象
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def _llm_structure_text(raw_text: str, filename: str) -> List[SheetData]:
    """
    调用本地 Ollama LLM 将 OCR 原始文本结构化为表格 JSON。
    仅在直接表格恢复失败时使用。
    """
    system_prompt = """你是一个专业的设备维保报价文档解析助手。用户会给你一段从图片或扫描件中 OCR 识别出的原始文本。

你的任务是：
1. 判断文本中是否包含表格数据（设备清单、报价单、维保需求等）
2. 如果包含，将其整理为一个 JSON 对象，格式为：
   {"headers": ["列名1", "列名2", ...], "data": [{"列名1": "值1", "列名2": "值2", ...}, ...]}
3. 如果不包含表格数据，返回：{"headers": [], "data": []}

常见的列名包括但不限于：
- 设备相关：厂商/品牌、设备型号、产品名称、序列号、设备分类、配置信息
- 数量相关：数量、台数
- 地址相关：城市、机房地址、安装地点
- 服务相关：服务级别、服务周期、服务范围
- 价格相关：单价、报价、设备原值
- 其他：备注、特殊需求

要求：
- 只返回纯 JSON，不要包含任何解释文字或 markdown 代码块标记
- 保持原始数据准确，不要编造或修改数据
- 修正明显的 OCR 识别错误（如数字 0 和字母 O 混淆、l 和 1 混淆等）
- 如果有多个表格，只返回与设备/报价最相关的那个"""

    user_msg = f"以下是从文件「{filename}」中 OCR 识别出的文本内容：\n\n{raw_text[:8000]}"

    content = _call_ollama(system_prompt, user_msg, timeout=90)
    parsed = _extract_json_from_llm(content)

    if parsed:
        headers = parsed.get("headers", [])
        rows = parsed.get("data", [])
        if headers and rows:
            return [SheetData(name="LLM结构化", headers=headers, data=rows)]

    return []


def _llm_standardize_fields(headers: List[str], data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    使用 LLM 对已解析的表格进行字段标准化：
    - 将非标准列名映射为系统标准字段名
    - 修正 OCR 导致的数据错误
    - 标准化厂商名称
    """
    # 系统标准字段定义
    standard_fields = [
        "厂商", "设备/软件型号", "设备/软件分类", "配置信息",
        "设备数量", "城市", "机房地址", "服务级别", "服务周期",
        "服务周期单位", "服务范围", "单价", "备注", "设备原值单价",
        "特殊需求", "易损件类型"
    ]

    system_prompt = f"""你是一个数据清洗和标准化助手，专门处理设备维保报价系统的数据。

用户会给你一个表格的列名列表和前几行数据样本。你的任务是：

1. **字段映射**：将用户的列名映射为系统标准字段名。标准字段名列表如下：
   {json.dumps(standard_fields, ensure_ascii=False)}

2. **数据清洗**：对数据中明显的 OCR 错误进行修正，例如：
   - 数字 0 和字母 O 混淆
   - 数字 1 和字母 l/I 混淆
   - 厂商名称标准化（如 "HP" → "惠普", "DELL" → "戴尔", "Huawei" → "华为"）

请返回一个 JSON 对象，格式：
{{
  "field_mapping": {{"原列名1": "标准字段名或null", "原列名2": "标准字段名或null", ...}},
  "cleaned_data": [{{"标准字段名1": "清洗后的值", ...}}, ...],
  "notes": "清洗说明（可选）"
}}

要求：
- 只返回纯 JSON，不加任何额外文字或 markdown 标记
- 如果某列无法映射到标准字段，其 field_mapping 值设为 null
- cleaned_data 中只包含映射成功的字段
- 不要编造数据，保持原始值（仅修正明显错误）"""

    # 取前5行作为样本
    sample_data = data[:5]
    user_msg = f"""表格列名：{json.dumps(headers, ensure_ascii=False)}

数据样本（前{len(sample_data)}行）：
{json.dumps(sample_data, ensure_ascii=False, indent=2)}"""

    content = _call_ollama(system_prompt, user_msg, timeout=90)
    return _extract_json_from_llm(content)


# ──────────────────────────────────────────────
#  主接口
# ──────────────────────────────────────────────

@router.post("/parse", response_model=ParseResponse)
async def parse_document(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None),
):
    """
    解析上传的文档文件，提取其中的表格数据。

    支持格式：
    - .docx  —— Word 文档中的表格
    - .pdf   —— 文本型 PDF 中的表格（自动检测是否为扫描型）
    - .png / .jpg / .jpeg / .bmp / .tiff —— 图片中的表格（需 OCR 依赖）

    返回统一的 { headers, data, sheets } 格式，与前端 XLSX.js 解析结果兼容。
    """
    filename = file.filename or "unknown"
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件过大（上限 {MAX_FILE_SIZE // 1024 // 1024}MB）")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="上传的文件为空")

    lower = filename.lower()
    file_type = "unknown"
    sheets: List[SheetData] = []

    try:
        if lower.endswith(".docx"):
            file_type = "docx"
            sheets = _parse_docx(content)

        elif lower.endswith(".doc"):
            raise HTTPException(
                status_code=400,
                detail=".doc 格式暂不支持，请将文件另存为 .docx 后重新上传。"
            )

        elif lower.endswith(".pdf"):
            file_type = "pdf"
            try:
                sheets = _parse_pdf_tables(content)
            except HTTPException:
                # 文本型 PDF 解析失败，尝试作为扫描型处理
                if _ocr_available() and _pdf2image_available():
                    sheets = _parse_scanned_pdf(content, filename)
                else:
                    raise

        elif lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp")):
            file_type = "image"
            sheets = _parse_image_ocr(content, filename)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式：{filename}。支持的格式：.docx, .pdf, .png, .jpg, .jpeg, .bmp, .tiff"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("文档解析失败: %s", filename)
        raise HTTPException(status_code=500, detail=f"文件解析过程出错：{str(e)}")

    # 默认选中第一个表格
    selected = sheets[0].name if sheets else None
    if sheet_name:
        for s in sheets:
            if s.name == sheet_name:
                selected = s.name
                break

    return ParseResponse(
        success=True,
        file_type=file_type,
        sheets=sheets,
        selected_sheet=selected,
        message=f"成功从 {file_type.upper()} 文件中提取了 {len(sheets)} 个表格，共 {sum(len(s.data) for s in sheets)} 行数据。"
    )


class StandardizeRequest(BaseModel):
    """字段标准化请求"""
    headers: List[str]
    data: List[Dict[str, Any]]


class StandardizeResponse(BaseModel):
    """字段标准化响应"""
    success: bool
    field_mapping: Dict[str, Optional[str]]  # 原列名 → 标准字段名
    standardized_headers: List[str]           # 标准化后的表头
    standardized_data: List[Dict[str, Any]]   # 标准化后的数据
    notes: Optional[str] = None
    message: Optional[str] = None


@router.post("/standardize", response_model=StandardizeResponse)
async def standardize_fields(req: StandardizeRequest):
    """
    使用 LLM 对已解析的表格进行字段标准化和数据清洗。
    
    功能：
    - 将非标准列名映射为系统标准字段（如 "品牌" → "厂商"、"型号" → "设备/软件型号"）
    - 修正 OCR 导致的数据错误
    - 标准化厂商名称（如 "HP" → "惠普"）
    
    可在前端解析完成后可选调用，提升数据质量。
    """
    if not req.headers or not req.data:
        raise HTTPException(status_code=400, detail="请求中缺少 headers 或 data")

    result = _llm_standardize_fields(req.headers, req.data)
    if not result:
        # LLM 不可用或解析失败，返回原始数据
        return StandardizeResponse(
            success=False,
            field_mapping={h: None for h in req.headers},
            standardized_headers=req.headers,
            standardized_data=req.data,
            message="LLM 服务不可用或无法解析结果，返回原始数据。"
        )

    field_mapping = result.get("field_mapping", {})
    cleaned_data = result.get("cleaned_data", [])
    notes = result.get("notes", "")

    # 构建标准化表头
    standardized_headers = []
    for h in req.headers:
        mapped = field_mapping.get(h)
        standardized_headers.append(mapped if mapped else h)

    # 如果 LLM 返回了清洗后的数据，使用它；否则根据 field_mapping 重映射原数据
    if cleaned_data and len(cleaned_data) > 0:
        final_data = cleaned_data
        # 如果 LLM 只返回了样本数据的清洗结果，对剩余行应用 field_mapping 转换
        if len(cleaned_data) < len(req.data):
            for row in req.data[len(cleaned_data):]:
                new_row = {}
                for h, v in row.items():
                    mapped_h = field_mapping.get(h, h)
                    if mapped_h:
                        new_row[mapped_h] = v
                final_data.append(new_row)
    else:
        # 仅做字段名映射，不修改数据
        final_data = []
        for row in req.data:
            new_row = {}
            for h, v in row.items():
                mapped_h = field_mapping.get(h, h)
                if mapped_h:
                    new_row[mapped_h] = v
            final_data.append(new_row)

    return StandardizeResponse(
        success=True,
        field_mapping=field_mapping,
        standardized_headers=standardized_headers,
        standardized_data=final_data,
        notes=notes,
        message=f"字段标准化完成。{sum(1 for v in field_mapping.values() if v)}/{len(field_mapping)} 个字段已映射。"
    )


@router.get("/supported-formats")
def get_supported_formats():
    """返回当前支持的文件格式列表，以及各格式的能力状态。"""
    ocr_ready = _ocr_available()
    pdf2img_ready = _pdf2image_available()

    return {
        "formats": [
            {
                "extension": ".xlsx / .xls",
                "name": "Excel 电子表格",
                "status": "ready",
                "description": "前端直接解析，无需后端",
            },
            {
                "extension": ".docx",
                "name": "Word 文档",
                "status": "ready",
                "description": "提取文档中的所有表格",
            },
            {
                "extension": ".pdf",
                "name": "PDF 文档",
                "status": "ready",
                "description": "提取文本型 PDF 中的表格" + ("；支持扫描型 PDF（OCR）" if ocr_ready and pdf2img_ready else ""),
            },
            {
                "extension": ".png / .jpg / .jpeg",
                "name": "图片文件",
                "status": "ready" if ocr_ready else "not_installed",
                "description": "OCR 识别图片中的表格" if ocr_ready else "需安装 rapidocr-onnxruntime 依赖",
            },
        ]
    }
