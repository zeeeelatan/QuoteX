#!/usr/bin/env python3
"""
增量同步 2025 驻场岗位省会城市薪资。

新版工作簿中，技术序列补充 7 个省会城市，管理序列补充 4 个省会城市。
这些城市与已有城市档位完全一致，脚本按岗位 ID 复制对应档位，只新增
或更新目标城市，不清空岗位表。
默认为 dry-run，显式传入 --apply 才会提交。

容器内执行：
    python -m scripts.sync_job_position_capital_salaries_2025
    python -m scripts.sync_job_position_capital_salaries_2025 --apply
"""

import argparse
from decimal import Decimal

from app.database import SessionLocal
from app.models.job_position import JobPosition, JobPositionSalary


EXPECTED_TECHNICAL_POSITION_COUNT = 92
EXPECTED_MANAGEMENT_POSITION_COUNT = 27

# 序列: {目标城市: (省份, 新版工作簿中与其数值完全一致的已有城市)}
TARGET_CITY_PROFILES = {
    "技术序列": {
        "长春市": ("吉林", "石家庄市"),
        "呼和浩特市": ("内蒙古", "太原市"),
        "兰州市": ("甘肃", "石家庄市"),
        "拉萨市": ("西藏", "石家庄市"),
        "西宁市": ("青海", "石家庄市"),
        "银川市": ("宁夏", "石家庄市"),
        "乌鲁木齐市": ("新疆", "石家庄市"),
    },
    "管理序列": {
        "兰州市": ("甘肃", "成都市"),
        "西宁市": ("青海", "成都市"),
        "银川市": ("宁夏", "成都市"),
        "乌鲁木齐市": ("新疆", "成都市"),
    },
}


def sync_capital_salaries(apply_changes: bool) -> int:
    db = SessionLocal()
    try:
        created = 0
        updated = 0
        unchanged = 0
        expected_total = 0

        for sequence_type, city_profiles in TARGET_CITY_PROFILES.items():
            expected_count = (
                EXPECTED_TECHNICAL_POSITION_COUNT
                if sequence_type == "技术序列"
                else EXPECTED_MANAGEMENT_POSITION_COUNT
            )
            source_cities = {source for _, source in city_profiles.values()}
            source_rows = (
                db.query(JobPositionSalary)
                .join(JobPosition, JobPosition.id == JobPositionSalary.position_id)
                .filter(
                    JobPosition.sequence_type == sequence_type,
                    JobPositionSalary.city.in_(source_cities),
                )
                .all()
            )
            source_map = {
                (row.city, row.position_id): Decimal(row.salary)
                for row in source_rows
            }

            for source_city in source_cities:
                count = sum(1 for city, _ in source_map if city == source_city)
                if count != expected_count:
                    print(
                        f"源城市 {source_city} {sequence_type}数据不完整："
                        f"期望 {expected_count}，实际 {count}"
                    )
                    db.rollback()
                    return 1

            position_ids = [
                row[0]
                for row in (
                    db.query(JobPosition.id)
                    .filter(JobPosition.sequence_type == sequence_type)
                    .order_by(JobPosition.id)
                    .all()
                )
            ]
            if len(position_ids) != expected_count:
                print(
                    f"{sequence_type}岗位数异常：期望 "
                    f"{expected_count}，实际 {len(position_ids)}"
                )
                db.rollback()
                return 1

            expected_total += expected_count * len(city_profiles)
            for target_city, (province, source_city) in city_profiles.items():
                existing = {
                    row.position_id: row
                    for row in (
                        db.query(JobPositionSalary)
                        .join(JobPosition, JobPosition.id == JobPositionSalary.position_id)
                        .filter(
                            JobPosition.sequence_type == sequence_type,
                            JobPositionSalary.city == target_city,
                        )
                        .all()
                    )
                }
                for position_id in position_ids:
                    expected_salary = source_map[(source_city, position_id)]
                    record = existing.get(position_id)
                    if record is None:
                        db.add(
                            JobPositionSalary(
                                position_id=position_id,
                                province=province,
                                city=target_city,
                                salary=expected_salary,
                            )
                        )
                        created += 1
                    elif (
                        Decimal(record.salary) != expected_salary
                        or record.province != province
                    ):
                        record.salary = expected_salary
                        record.province = province
                        updated += 1
                    else:
                        unchanged += 1

        print(f"本次校验数据：{expected_total} 条")
        print(f"待新增：{created} 条")
        print(f"待更新：{updated} 条")
        print(f"无需更新：{unchanged} 条")

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
    parser = argparse.ArgumentParser(
        description="增量同步 2025 驻场岗位省会城市薪资"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="提交更新；不传时仅执行 dry-run",
    )
    args = parser.parse_args()
    return sync_capital_salaries(apply_changes=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
