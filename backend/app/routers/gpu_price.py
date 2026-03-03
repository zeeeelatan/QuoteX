from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import pandas as pd
import io
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.models.gpu_price import GPUPrice
from app.schemas.gpu_price import GPUPriceCreate, GPUPriceOut


router = APIRouter(prefix="/gpu_prices", tags=["GPU价格管理"])


@router.get("/", response_model=List[GPUPriceOut])
def list_gpu_prices(db: Session = Depends(get_db)):
    return db.query(GPUPrice).order_by(GPUPrice.id.desc()).all()


@router.post("/import")
async def import_gpu_prices(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # 读取 Excel（支持 .xls/.xlsx），尽量兼容多 sheet
        raw = await file.read()
        bio = io.BytesIO(raw)
        filename = (file.filename or '').lower()
        ext = filename.split('.')[-1] if '.' in filename else ''

        df = None
        # 优先按扩展名解析
        if ext in {"xlsx", "xlsm", "xltx", "xltm"}:
            try:
                df = pd.read_excel(bio, engine='openpyxl')
            except Exception:
                bio.seek(0)
                xls = pd.ExcelFile(bio)
                frames = [xls.parse(sheet_name) for sheet_name in xls.sheet_names]
                df = pd.concat(frames, ignore_index=True)
        elif ext == 'xls':
            try:
                df = pd.read_excel(bio, engine='xlrd')
            except Exception:
                bio.seek(0)
                df = pd.read_excel(bio)
        else:
            try:
                xls = pd.ExcelFile(bio)
                frames = [xls.parse(sheet_name) for sheet_name in xls.sheet_names]
                df = pd.concat(frames, ignore_index=True)
            except Exception:
                bio.seek(0)
                df = pd.read_excel(bio)
        if df is None:
            raise HTTPException(status_code=400, detail="无法解析Excel，请确认文件格式是否为 .xls/.xlsx")

        # 确保数据库表包含新增列
        try:
            alter_sqls = [
                "ALTER TABLE gpu_price ADD COLUMN IF NOT EXISTS manufacturer VARCHAR;",
                "ALTER TABLE gpu_price ADD COLUMN IF NOT EXISTS series VARCHAR;",
                "ALTER TABLE gpu_price ADD COLUMN IF NOT EXISTS gpu_memory VARCHAR;",
                "ALTER TABLE gpu_price ADD COLUMN IF NOT EXISTS gpu_interface_type VARCHAR;",
                "ALTER TABLE gpu_price ADD COLUMN IF NOT EXISTS sales_status VARCHAR;",
            ]
            for sql in alter_sqls:
                db.execute(text(sql))
            db.commit()
        except Exception:
            db.rollback()

        # 兼容列名
        cn2field = {
            '序号': 'id',
            '厂商': 'manufacturer',
            '系列': 'series',
            'GPU卡价格': 'gpu_price',
            'GPU卡费率': 'gpu_rate',
            '备件维修费': 'spare_repair_cost',
            '人工维修费': 'labor_repair_cost',
            '维保服务费': 'service_fee',
            '型号': 'model',
            'GPU型号': 'model',
            'GPU卡显存': 'gpu_memory',
            'GPU卡接口类型': 'gpu_interface_type',
            '销售情况': 'sales_status',
            '销售情况：值为禁售卡、非禁售卡': 'sales_status',
        }

        df = df.rename(columns=cn2field)
        keep_cols = [
            'manufacturer', 'series', 'model', 'gpu_memory', 'gpu_interface_type', 'sales_status',
            'gpu_price', 'gpu_rate', 'spare_repair_cost', 'labor_repair_cost', 'service_fee'
        ]
        df = df[[c for c in keep_cols if c in df.columns]].copy()

        # 规范数据类型；费率从百分数转小数
        def to_float(x):
            try:
                s = (
                    str(x)
                    .replace(',', '')
                    .replace('%', '')
                    .replace('¥', '')
                    .replace('￥', '')
                    .strip()
                )
                return float(s) if s not in (None, "", "nan") else 0.0
            except Exception:
                return 0.0

        for col in ['gpu_price', 'spare_repair_cost', 'labor_repair_cost', 'service_fee']:
            if col in df.columns:
                df[col] = df[col].apply(to_float)

        if 'gpu_rate' in df.columns:
            def to_rate(v: float) -> float:
                return (v / 100.0) if v is not None and v > 1 else (v or 0.0)
            df['gpu_rate'] = df['gpu_rate'].apply(to_float).apply(to_rate)

        # 校验必填字段与自动计算
        required_text_cols = ['manufacturer', 'series', 'model', 'gpu_memory', 'gpu_interface_type', 'sales_status']
        required_num_cols = ['gpu_price', 'gpu_rate', 'labor_repair_cost']

        def norm_str(x):
            return (str(x).strip() if x is not None else '')

        corrections = []
        errors = []
        valid_records = []
        for idx, row in df.iterrows():
            record = {col: row.get(col) for col in keep_cols}
            missing_text = [c for c in required_text_cols if not norm_str(record.get(c))]
            missing_num = [c for c in required_num_cols if record.get(c) in (None, '') or not isinstance(record.get(c), (int, float))]
            if missing_text or missing_num:
                errors.append({
                    'row_index': int(idx) + 2,
                    'missing_text': missing_text,
                    'missing_num': missing_num
                })
                continue

            price = float(record.get('gpu_price') or 0)
            rate = float(record.get('gpu_rate') or 0)
            labor = float(record.get('labor_repair_cost') or 0)

            calc_spare = round(price * rate, 2)
            given_spare = float(record.get('spare_repair_cost') or 0)
            if abs(given_spare - calc_spare) > 0.01:
                corrections.append({'row_index': int(idx) + 2, 'field': 'spare_repair_cost', 'old': given_spare, 'new': calc_spare})
                record['spare_repair_cost'] = calc_spare
            else:
                record['spare_repair_cost'] = given_spare

            calc_service = round(float(record['spare_repair_cost']) + labor, 2)
            given_service = float(record.get('service_fee') or 0)
            if abs(given_service - calc_service) > 0.01:
                corrections.append({'row_index': int(idx) + 2, 'field': 'service_fee', 'old': given_service, 'new': calc_service})
                record['service_fee'] = calc_service
            else:
                record['service_fee'] = given_service

            for c in required_text_cols:
                record[c] = norm_str(record.get(c))

            valid_records.append(record)

        # 清空并重导
        db.query(GPUPrice).delete()
        db.commit()

        objs = [GPUPrice(**r) for r in valid_records]
        if objs:
            db.bulk_save_objects(objs)
            db.commit()

        return {
            "ok": True,
            "inserted_count": len(objs),
            "skipped_count": len(errors),
            "corrected_count": len(corrections),
            "corrections": corrections[:50],
            "errors": errors[:50]
        }
    except HTTPException:
        raise
    except Exception as e:
        # 返回明确错误信息，方便排查
        raise HTTPException(status_code=500, detail=f"导入失败: {type(e).__name__}: {e}")


@router.get("/template")
def download_gpu_price_template(fmt: str = Query("xlsx", pattern="^(xlsx|csv)$")):
    # 固定表头模板
    columns = ['序号','厂商','系列','型号','GPU卡显存','GPU卡接口类型','销售情况：值为禁售卡、非禁售卡','GPU卡价格','GPU卡费率','备件维修费','人工维修费','维保服务费']
    df = pd.DataFrame(columns=columns)
    if fmt == 'csv':
        content = df.to_csv(index=False).encode('utf-8-sig')
        bio = io.BytesIO(content)
        bio.seek(0)
        return StreamingResponse(
            bio,
            media_type='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename="gpu_price_template.csv"'}
        )
    # 默认尝试导出 xlsx；若依赖缺失则回退 csv
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='模板')
        output.seek(0)
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="gpu_price_template.xlsx"'}
        )
    except Exception:
        # 回退为 CSV，保证接口不报错
        content = df.to_csv(index=False).encode('utf-8-sig')
        bio = io.BytesIO(content)
        bio.seek(0)
        return StreamingResponse(
            bio,
            media_type='text/csv; charset=utf-8',
            headers={'Content-Disposition': 'attachment; filename="gpu_price_template.csv"'}
        )


@router.delete("/clear")
def clear_gpu_prices(db: Session = Depends(get_db)):
    db.query(GPUPrice).delete()
    db.commit()
    return {"ok": True}



