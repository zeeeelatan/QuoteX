#!/usr/bin/env python3
"""增量同步国际驻场岗位薪资矩阵，默认仅同步韩国。"""

import argparse
import json
from decimal import Decimal
from pathlib import Path

from app.database import SessionLocal
from app.models.international_quote import InternationalJobSalary


DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "data"
    / "international_salary_matrix.json"
)
DEFAULT_COUNTRIES = {"korea"}


def sync_salary_matrix(apply_changes: bool, country_codes: set[str]) -> int:
    matrix = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    locations = [
        location
        for location in matrix["locations"]
        if location["country_code"] in country_codes
    ]
    missing_codes = country_codes - {location["country_code"] for location in locations}
    if missing_codes:
        print(f"薪资矩阵缺少国家：{', '.join(sorted(missing_codes))}")
        return 1

    expected = len(locations) * len(matrix["positions"])
    db = SessionLocal()
    try:
        existing_rows = (
            db.query(InternationalJobSalary)
            .filter(InternationalJobSalary.country_code.in_(country_codes))
            .all()
        )
        existing = {
            (
                row.country_code,
                row.region,
                row.city,
                row.sequence_type,
                row.position_name,
                row.level_name,
            ): row
            for row in existing_rows
        }

        created = 0
        updated = 0
        unchanged = 0
        location_indexes = [
            (index, location)
            for index, location in enumerate(matrix["locations"])
            if location["country_code"] in country_codes
        ]
        source_note = f"来源：{matrix['source']}"

        for position in matrix["positions"]:
            for index, location in location_indexes:
                salary = Decimal(str(position["salaries"][index]))
                key = (
                    location["country_code"],
                    location["region"],
                    location["city"],
                    position["sequence_type"],
                    position["position_name"],
                    position["level_name"],
                )
                payload = {
                    **location,
                    "sequence_type": position["sequence_type"],
                    "category": position["category"],
                    "position_name": position["position_name"],
                    "level_name": position["level_name"],
                    "level_rank": position["level_rank"],
                    "monthly_salary": salary,
                    "notes": source_note,
                    "is_active": True,
                }
                record = existing.get(key)
                if record is None:
                    db.add(InternationalJobSalary(**payload))
                    created += 1
                    continue

                changed = any(
                    (
                        Decimal(record.monthly_salary) != salary,
                        record.country_name != location["country_name"],
                        record.currency != location["currency"],
                        record.category != position["category"],
                        record.level_rank != position["level_rank"],
                        record.notes != source_note,
                        not record.is_active,
                    )
                )
                if changed:
                    for field, value in payload.items():
                        setattr(record, field, value)
                    updated += 1
                else:
                    unchanged += 1

        print(f"本次校验数据：{expected} 条")
        print(f"待新增：{created} 条")
        print(f"待更新：{updated} 条")
        print(f"无需更新：{unchanged} 条")
        if created + updated + unchanged != expected:
            db.rollback()
            print("同步计数不一致，已终止。")
            return 1

        if apply_changes:
            db.commit()
            print("已提交更新。")
        else:
            db.rollback()
            print("dry-run 完成，未修改数据库。")
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="增量同步国际驻场岗位薪资矩阵")
    parser.add_argument(
        "--country",
        action="append",
        dest="countries",
        help="指定国家代码，可重复传入；默认仅同步 korea",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="提交更新；不传时仅执行 dry-run",
    )
    args = parser.parse_args()
    return sync_salary_matrix(
        apply_changes=args.apply,
        country_codes=set(args.countries or DEFAULT_COUNTRIES),
    )


if __name__ == "__main__":
    raise SystemExit(main())
