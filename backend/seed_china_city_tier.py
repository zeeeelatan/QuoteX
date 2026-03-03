#!/usr/bin/env python3
"""
一键将「中国城市分级表.xlsx」导入数据库。
用法: cd backend && python seed_china_city_tier.py [Excel路径]
默认路径: ./data/中国城市分级表.xlsx
"""
import sys
import os

# 确保能导入 app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from app.database import SessionLocal
from app.models.china_city_tier import ChinaCityTier

DEFAULT_PATH = os.getenv("IMPORT_EXCEL_FILE", "./data/中国城市分级表.xlsx")


def _safe_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None


def _safe_int(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _row_val(row, name: str, idx: int):
    if name in row.index:
        v = row[name]
    elif idx < len(row):
        v = row.iloc[idx]
    else:
        return None
    if name == "序号":
        return _safe_int(v)
    return _safe_str(v)


def run(excel_path: str = DEFAULT_PATH):
    if not os.path.isfile(excel_path):
        print(f"文件不存在: {excel_path}")
        sys.exit(1)
    df = pd.read_excel(excel_path, header=0)
    records = []
    for idx, row in df.iterrows():
        city_name = _row_val(row, "城市名称", 3)
        if not city_name:
            continue
        records.append({
            "seq_no": _row_val(row, "序号", 0),
            "city_tier": _row_val(row, "城市等级", 1),
            "tier_code": _row_val(row, "城市等级代码", 2),
            "city_name": city_name,
            "province": _row_val(row, "所属省份", 4),
            "admin_level": _row_val(row, "行政级别", 5),
            "is_provincial_capital": _row_val(row, "是否省会", 6),
            "is_gdp_trillion": _row_val(row, "GDP万亿城市", 7),
            "logistics_hub_level": _row_val(row, "物流枢纽等级", 8),
            "remarks": _row_val(row, "备注", 9),
        })
    db = SessionLocal()
    try:
        db.query(ChinaCityTier).delete()
        for r in records:
            db.add(ChinaCityTier(**r))
        db.commit()
        print(f"成功导入 {len(records)} 条中国城市分级数据。")
    except Exception as e:
        db.rollback()
        print(f"导入失败: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    run(path)
