#!/usr/bin/env python3
"""
一次性同步 2025 驻场岗位税前月薪系统上下限。

仅更新 job_position.system_salary_min / system_salary_max，不修改岗位、
城市薪资或其他业务数据。默认 dry-run，显式传入 --apply 才会提交。

容器内执行：
    python -m scripts.sync_job_position_salary_bounds_2025
    python -m scripts.sync_job_position_salary_bounds_2025 --apply
"""

import argparse
from decimal import Decimal
from typing import Dict, Tuple

from app.database import SessionLocal
from app.models.job_position import JobPosition


EXPECTED_POSITION_COUNT = 119

BOUND_DATA = [
    ('技术序列', '前端开发工程师', '初级 (Junior/P1-P2)', 5200, 19200),
    ('技术序列', '前端开发工程师', '中级 (Mid/P3-P4)', 8000, 28800),
    ('技术序列', '前端开发工程师', '高级 (Senior/P5-P6)', 11600, 42000),
    ('技术序列', '前端开发工程师', '专家/资深 (Expert/P7+)', 16800, 60000),
    ('技术序列', '后端开发工程师', '初级 (Junior/P1-P2)', 6000, 21600),
    ('技术序列', '后端开发工程师', '中级 (Mid/P3-P4)', 8800, 31200),
    ('技术序列', '后端开发工程师', '高级 (Senior/P5-P6)', 12800, 45600),
    ('技术序列', '后端开发工程师', '专家/资深 (Expert/P7+)', 18400, 66000),
    ('技术序列', '全栈开发工程师', '初级 (Junior/P1-P2)', 5600, 20400),
    ('技术序列', '全栈开发工程师', '中级 (Mid/P3-P4)', 8400, 30000),
    ('技术序列', '全栈开发工程师', '高级 (Senior/P5-P6)', 12000, 43200),
    ('技术序列', '全栈开发工程师', '专家/资深 (Expert/P7+)', 17600, 62400),
    ('技术序列', '移动开发工程师(iOS/Android)', '初级 (Junior/P1-P2)', 6000, 21600),
    ('技术序列', '移动开发工程师(iOS/Android)', '中级 (Mid/P3-P4)', 9600, 33600),
    ('技术序列', '移动开发工程师(iOS/Android)', '高级 (Senior/P5-P6)', 13600, 48000),
    ('技术序列', '移动开发工程师(iOS/Android)', '专家/资深 (Expert/P7+)', 18400, 66000),
    ('技术序列', '嵌入式开发工程师', '初级 (Junior/P1-P2)', 4800, 16800),
    ('技术序列', '嵌入式开发工程师', '中级 (Mid/P3-P4)', 6800, 24000),
    ('技术序列', '嵌入式开发工程师', '高级 (Senior/P5-P6)', 10000, 36000),
    ('技术序列', '嵌入式开发工程师', '专家/资深 (Expert/P7+)', 14000, 50400),
    ('技术序列', '测试/QA工程师', '初级 (Junior/P1-P2)', 3200, 12000),
    ('技术序列', '测试/QA工程师', '中级 (Mid/P3-P4)', 5200, 18000),
    ('技术序列', '测试/QA工程师', '高级 (Senior/P5-P6)', 7200, 26400),
    ('技术序列', '测试/QA工程师', '专家/资深 (Expert/P7+)', 10800, 38400),
    ('技术序列', '运维工程师', '初级 (Junior/P1-P2)', 2400, 10800),
    ('技术序列', '运维工程师', '中级 (Mid/P3-P4)', 3600, 16800),
    ('技术序列', '运维工程师', '高级 (Senior/P5-P6)', 5200, 24000),
    ('技术序列', '运维工程师', '专家/资深 (Expert/P7+)', 7600, 36000),
    ('技术序列', 'DevOps工程师', '初级 (Junior/P1-P2)', 3600, 15600),
    ('技术序列', 'DevOps工程师', '中级 (Mid/P3-P4)', 5200, 24000),
    ('技术序列', 'DevOps工程师', '高级 (Senior/P5-P6)', 7600, 36000),
    ('技术序列', 'DevOps工程师', '专家/资深 (Expert/P7+)', 10800, 50400),
    ('技术序列', '网络工程师', '初级 (Junior/P1-P2)', 2400, 10800),
    ('技术序列', '网络工程师', '中级 (Mid/P3-P4)', 3600, 16800),
    ('技术序列', '网络工程师', '高级 (Senior/P5-P6)', 5200, 24000),
    ('技术序列', '网络工程师', '专家/资深 (Expert/P7+)', 7600, 36000),
    ('技术序列', '桌面工程师', '初级 (Junior/P1-P2)', 1600, 8400),
    ('技术序列', '桌面工程师', '中级 (Mid/P3-P4)', 2400, 12000),
    ('技术序列', '桌面工程师', '高级 (Senior/P5-P6)', 4000, 18000),
    ('技术序列', '桌面工程师', '专家/资深 (Expert/P7+)', 5600, 26400),
    ('技术序列', '数据库工程师(DBA)', '初级 (Junior/P1-P2)', 4000, 14400),
    ('技术序列', '数据库工程师(DBA)', '中级 (Mid/P3-P4)', 6000, 21600),
    ('技术序列', '数据库工程师(DBA)', '高级 (Senior/P5-P6)', 9200, 32400),
    ('技术序列', '数据库工程师(DBA)', '专家/资深 (Expert/P7+)', 12800, 45600),
    ('技术序列', '数据工程师', '初级 (Junior/P1-P2)', 4800, 16800),
    ('技术序列', '数据工程师', '中级 (Mid/P3-P4)', 7200, 25200),
    ('技术序列', '数据工程师', '高级 (Senior/P5-P6)', 10000, 36000),
    ('技术序列', '数据工程师', '专家/资深 (Expert/P7+)', 14000, 50400),
    ('技术序列', '大数据工程师', '初级 (Junior/P1-P2)', 5200, 18000),
    ('技术序列', '大数据工程师', '中级 (Mid/P3-P4)', 7200, 26400),
    ('技术序列', '大数据工程师', '高级 (Senior/P5-P6)', 10800, 38400),
    ('技术序列', '大数据工程师', '专家/资深 (Expert/P7+)', 15200, 54000),
    ('技术序列', '数据分析师', '初级 (Junior/P1-P2)', 3600, 13200),
    ('技术序列', '数据分析师', '中级 (Mid/P3-P4)', 5200, 19200),
    ('技术序列', '数据分析师', '高级 (Senior/P5-P6)', 8000, 28800),
    ('技术序列', '数据分析师', '专家/资深 (Expert/P7+)', 11600, 42000),
    ('技术序列', '算法/机器学习工程师', '初级 (Junior/P1-P2)', 6800, 24000),
    ('技术序列', '算法/机器学习工程师', '中级 (Mid/P3-P4)', 10800, 38400),
    ('技术序列', '算法/机器学习工程师', '高级 (Senior/P5-P6)', 16000, 57600),
    ('技术序列', '算法/机器学习工程师', '专家/资深 (Expert/P7+)', 23600, 84000),
    ('技术序列', '系统架构师', '初级 (Junior/P1-P2)', 7200, 26400),
    ('技术序列', '系统架构师', '中级 (Mid/P3-P4)', 10800, 38400),
    ('技术序列', '系统架构师', '高级 (Senior/P5-P6)', 15200, 54000),
    ('技术序列', '系统架构师', '专家/资深 (Expert/P7+)', 22000, 78000),
    ('技术序列', '安全工程师', '初级 (Junior/P1-P2)', 4400, 15600),
    ('技术序列', '安全工程师', '中级 (Mid/P3-P4)', 6800, 24000),
    ('技术序列', '安全工程师', '高级 (Senior/P5-P6)', 10000, 36000),
    ('技术序列', '安全工程师', '专家/资深 (Expert/P7+)', 14000, 50400),
    ('技术序列', '云计算工程师', '初级 (Junior/P1-P2)', 3600, 16800),
    ('技术序列', '云计算工程师', '中级 (Mid/P3-P4)', 5600, 26400),
    ('技术序列', '云计算工程师', '高级 (Senior/P5-P6)', 8400, 38400),
    ('技术序列', '云计算工程师', '专家/资深 (Expert/P7+)', 11600, 54000),
    ('技术序列', 'UI/UX设计师', '初级 (Junior/P1-P2)', 3200, 12000),
    ('技术序列', 'UI/UX设计师', '中级 (Mid/P3-P4)', 5200, 18000),
    ('技术序列', 'UI/UX设计师', '高级 (Senior/P5-P6)', 7200, 26400),
    ('技术序列', 'UI/UX设计师', '专家/资深 (Expert/P7+)', 10800, 38400),
    ('技术序列', '产品经理', '初级 (Junior/P1-P2)', 4400, 15600),
    ('技术序列', '产品经理', '中级 (Mid/P3-P4)', 6800, 24000),
    ('技术序列', '产品经理', '高级 (Senior/P5-P6)', 10000, 36000),
    ('技术序列', '产品经理', '专家/资深 (Expert/P7+)', 15200, 54000),
    ('技术序列', '项目经理/技术项目经理', '初级 (Junior/P1-P2)', 4400, 15600),
    ('技术序列', '项目经理/技术项目经理', '中级 (Mid/P3-P4)', 6400, 22800),
    ('技术序列', '项目经理/技术项目经理', '高级 (Senior/P5-P6)', 9600, 33600),
    ('技术序列', '项目经理/技术项目经理', '专家/资深 (Expert/P7+)', 13600, 48000),
    ('技术序列', '存储工程师', '初级 (Junior/P1-P2)', 2400, 12000),
    ('技术序列', '存储工程师', '中级 (Mid/P3-P4)', 4400, 19200),
    ('技术序列', '存储工程师', '高级 (Senior/P5-P6)', 6400, 28800),
    ('技术序列', '存储工程师', '专家/资深 (Expert/P7+)', 9200, 42000),
    ('技术序列', '音视频工程师', '初级 (Junior/P1-P2)', 2000, 9600),
    ('技术序列', '音视频工程师', '中级 (Mid/P3-P4)', 3200, 14400),
    ('技术序列', '音视频工程师', '高级 (Senior/P5-P6)', 4800, 21600),
    ('技术序列', '音视频工程师', '专家/资深 (Expert/P7+)', 6400, 31200),
    ('管理序列', '研发经理/技术总监(涵盖前端/后端/全栈/移动/嵌入式团队)', '初级管理 (团队负责人/Team Lead)', 11600, 42000),
    ('管理序列', '研发经理/技术总监(涵盖前端/后端/全栈/移动/嵌入式团队)', '中级管理 (部门经理/Manager)', 18400, 66000),
    ('管理序列', '研发经理/技术总监(涵盖前端/后端/全栈/移动/嵌入式团队)', '高级管理 (总监/VP及以上)', 28400, 102000),
    ('管理序列', '测试经理/质量总监', '初级管理 (团队负责人/Team Lead)', 8400, 30000),
    ('管理序列', '测试经理/质量总监', '中级管理 (部门经理/Manager)', 13600, 48000),
    ('管理序列', '测试经理/质量总监', '高级管理 (总监/VP及以上)', 20000, 72000),
    ('管理序列', '运维经理/IT总监', '初级管理 (团队负责人/Team Lead)', 8400, 30000),
    ('管理序列', '运维经理/IT总监', '中级管理 (部门经理/Manager)', 13600, 48000),
    ('管理序列', '运维经理/IT总监', '高级管理 (总监/VP及以上)', 20800, 74400),
    ('管理序列', '数据团队经理/首席数据官(CDO)方向', '初级管理 (团队负责人/Team Lead)', 10000, 36000),
    ('管理序列', '数据团队经理/首席数据官(CDO)方向', '中级管理 (部门经理/Manager)', 16000, 57600),
    ('管理序列', '数据团队经理/首席数据官(CDO)方向', '高级管理 (总监/VP及以上)', 25200, 90000),
    ('管理序列', '安全经理/CISO方向', '初级管理 (团队负责人/Team Lead)', 9600, 33600),
    ('管理序列', '安全经理/CISO方向', '中级管理 (部门经理/Manager)', 15200, 54000),
    ('管理序列', '安全经理/CISO方向', '高级管理 (总监/VP及以上)', 23600, 84000),
    ('管理序列', '产品线负责人/产品总监(CPO方向)', '初级管理 (团队负责人/Team Lead)', 10000, 36000),
    ('管理序列', '产品线负责人/产品总监(CPO方向)', '中级管理 (部门经理/Manager)', 16000, 57600),
    ('管理序列', '产品线负责人/产品总监(CPO方向)', '高级管理 (总监/VP及以上)', 26400, 93600),
    ('管理序列', '设计经理/设计总监', '初级管理 (团队负责人/Team Lead)', 8000, 28800),
    ('管理序列', '设计经理/设计总监', '中级管理 (部门经理/Manager)', 12800, 45600),
    ('管理序列', '设计经理/设计总监', '高级管理 (总监/VP及以上)', 19600, 69600),
    ('管理序列', '高级项目经理/PMO负责人', '初级管理 (团队负责人/Team Lead)', 8000, 28800),
    ('管理序列', '高级项目经理/PMO负责人', '中级管理 (部门经理/Manager)', 12800, 45600),
    ('管理序列', '高级项目经理/PMO负责人', '高级管理 (总监/VP及以上)', 19600, 69600),
    ('管理序列', '技术总监/CTO', '初级管理 (团队负责人/Team Lead)', 13600, 48000),
    ('管理序列', '技术总监/CTO', '中级管理 (部门经理/Manager)', 22000, 78000),
    ('管理序列', '技术总监/CTO', '高级管理 (总监/VP及以上)', 33600, 120000),
]


PositionKey = Tuple[str, str]


def _source_map() -> Dict[PositionKey, tuple]:
    if len(BOUND_DATA) != EXPECTED_POSITION_COUNT:
        raise ValueError(
            f"源数据条数异常：期望 {EXPECTED_POSITION_COUNT}，实际 {len(BOUND_DATA)}"
        )

    result: Dict[PositionKey, tuple] = {}
    for sequence_type, position_name, level_name, salary_min, salary_max in BOUND_DATA:
        key = (position_name, level_name)
        if key in result:
            raise ValueError(f"源数据存在重复岗位：{position_name} - {level_name}")
        if salary_min < 0 or salary_max < 0 or salary_min > salary_max:
            raise ValueError(f"源数据上下限异常：{position_name} - {level_name}")
        result[key] = (sequence_type, Decimal(salary_min), Decimal(salary_max))
    return result


def sync_salary_bounds(apply_changes: bool) -> int:
    source = _source_map()
    db = SessionLocal()
    try:
        positions = db.query(JobPosition).all()
        position_map: Dict[PositionKey, JobPosition] = {}
        duplicate_keys = []

        for position in positions:
            key = (position.position_name, position.level_name)
            if key in position_map:
                duplicate_keys.append(key)
            else:
                position_map[key] = position

        if duplicate_keys:
            print("正式库存在重复岗位，已中止：")
            for position_name, level_name in duplicate_keys[:10]:
                print(f"  - {position_name} - {level_name}")
            db.rollback()
            return 1

        missing_keys = sorted(set(source) - set(position_map))
        if missing_keys:
            print(
                f"正式库缺少 {len(missing_keys)} 个岗位，未执行任何更新。"
                "请先同步完整岗位职级数据："
            )
            for position_name, level_name in missing_keys[:20]:
                print(f"  - {position_name} - {level_name}")
            db.rollback()
            return 1

        changes = []
        for key, (expected_sequence, salary_min, salary_max) in source.items():
            position = position_map[key]
            if position.sequence_type != expected_sequence:
                print(
                    f"岗位序列不一致，已中止：{position.position_name} - "
                    f"{position.level_name}，正式库={position.sequence_type}，"
                    f"源数据={expected_sequence}"
                )
                db.rollback()
                return 1

            current_min = (
                Decimal(position.system_salary_min)
                if position.system_salary_min is not None
                else None
            )
            current_max = (
                Decimal(position.system_salary_max)
                if position.system_salary_max is not None
                else None
            )
            if current_min != salary_min or current_max != salary_max:
                changes.append((position, current_min, current_max, salary_min, salary_max))

        print(f"源数据岗位数：{len(source)}")
        print(f"正式库匹配岗位数：{len(source)}")
        print(f"需要更新：{len(changes)}")
        print(f"无需更新：{len(source) - len(changes)}")

        for position, old_min, old_max, new_min, new_max in changes[:10]:
            print(
                f"  - {position.position_name} - {position.level_name}: "
                f"{old_min}/{old_max} -> {new_min}/{new_max}"
            )

        if not apply_changes:
            print("当前为 dry-run，未写入数据库。传入 --apply 后执行正式同步。")
            db.rollback()
            return 0

        for position, _, _, salary_min, salary_max in changes:
            position.system_salary_min = salary_min
            position.system_salary_max = salary_max

        db.flush()

        for position, _, _, salary_min, salary_max in changes:
            if (
                Decimal(position.system_salary_min) != salary_min
                or Decimal(position.system_salary_max) != salary_max
            ):
                raise RuntimeError(
                    f"写入校验失败：{position.position_name} - {position.level_name}"
                )

        db.commit()
        print(f"同步完成：已更新 {len(changes)} 个岗位薪资上下限。")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"同步失败，事务已回滚：{exc}")
        return 1
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="同步 2025 驻场岗位薪资上下限")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="提交更新；省略时仅执行 dry-run",
    )
    args = parser.parse_args()
    return sync_salary_bounds(apply_changes=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())

