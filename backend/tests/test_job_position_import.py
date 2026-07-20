from io import BytesIO

from openpyxl import Workbook

from app.routers.job_position import _parse_workbook
from scripts.sync_job_position_salary_bounds_2025 import (
    EXPECTED_POSITION_COUNT,
    _source_map,
)


BASE_HEADERS = [
    "序号",
    "岗位类别",
    "岗位名称",
    "技术级别",
    "级别核心要求(含建议认证)",
    "适用认证参考",
    "工作内容",
    "工作产出/交付物",
    "KPI考核点及标准参考值",
]


def _workbook_bytes() -> bytes:
    workbook = Workbook()
    workbook.remove(workbook.active)

    for sheet_name, sequence_type in (
        ("技术序列分级详情", "技术序列"),
        ("管理序列分级详情", "管理序列"),
    ):
        sheet = workbook.create_sheet(sheet_name)
        sheet.append([f"{sequence_type}岗位分级详情"])
        sheet.append([None] * 9 + ["北京", None, None])
        headers = list(BASE_HEADERS)
        if sequence_type == "管理序列":
            headers[1] = "管理方向"
            headers[3] = "管理级别"
        sheet.append(headers + ["北京市", "系统取值最大值", "系统取值最小值"])
        sheet.append(
            [
                1,
                "研发类" if sequence_type == "技术序列" else "研发管理",
                "前端开发工程师" if sequence_type == "技术序列" else "研发经理",
                "初级 (Junior/P1-P2)" if sequence_type == "技术序列" else "初级管理 (Team Lead)",
                "核心要求",
                "认证参考",
                "工作内容",
                "交付物",
                "KPI",
                16000,
                19200,
                5200,
            ]
        )

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def test_parse_workbook_imports_system_salary_bounds():
    records = _parse_workbook(_workbook_bytes())

    assert len(records) == 2
    assert records[0]["system_salary_max"] == 19200
    assert records[0]["system_salary_min"] == 5200
    assert records[0]["salaries"] == [
        {"province": "北京", "city": "北京市", "salary": 16000.0}
    ]
    assert all(
        salary["city"] not in {"系统取值最大值", "系统取值最小值"}
        for record in records
        for salary in record["salaries"]
    )


def test_salary_bounds_sync_source_is_complete():
    source = _source_map()

    assert len(source) == EXPECTED_POSITION_COUNT == 119
    assert source[("前端开发工程师", "初级 (Junior/P1-P2)")][1:] == (5200, 19200)
    assert source[("技术总监/CTO", "高级管理 (总监/VP及以上)")][1:] == (
        33600,
        120000,
    )
