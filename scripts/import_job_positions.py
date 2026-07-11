#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入驻场岗位职级及城市薪资数据到数据库（清空重导）
数据源：《IT岗位技术与管理序列分级表_含薪资》Excel
用法：
    IMPORT_EXCEL_FILE=/path/to/file.xlsx python scripts/import_job_positions.py
"""
import sys
import os

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_path)

from app.database import engine, SessionLocal, Base
from app.models.job_position import JobPosition, JobPositionSalary
from app.routers.job_position import _parse_workbook, _import_records


def main():
    excel_path = os.getenv(
        "IMPORT_EXCEL_FILE",
        "./data/IT岗位技术与管理序列分级表_含薪资_更新.xlsx",
    )
    if not os.path.exists(excel_path):
        print(f"文件不存在: {excel_path}")
        sys.exit(1)

    print(f"正在读取Excel文件: {excel_path}")
    with open(excel_path, "rb") as f:
        file_bytes = f.read()

    records = _parse_workbook(file_bytes)
    print(f"解析到 {len(records)} 个岗位职级")
    total_salaries = sum(len(r["salaries"]) for r in records)
    print(f"解析到 {total_salaries} 条城市薪资")

    # 确保表存在
    Base.metadata.create_all(bind=engine, tables=[
        JobPosition.__table__, JobPositionSalary.__table__,
    ])

    db = SessionLocal()
    try:
        stats = _import_records(db, records)
        print(f"导入完成: {stats['position_count']} 个岗位职级, {stats['salary_count']} 条城市薪资")

        # 校验统计
        pos_count = db.query(JobPosition).count()
        sal_count = db.query(JobPositionSalary).count()
        print(f"数据库现有: job_position={pos_count}, job_position_salary={sal_count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
