from io import BytesIO

from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.china_city_tier import ChinaCityTier
from app.models.city_social_insurance import CitySocialInsurance
from app.models.job_position import JobPosition, JobPositionSalary
from app.routers.job_position import _parse_workbook, _query_salary_with_fallback


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


def test_parse_workbook_ignores_legacy_salary_bound_columns():
    records = _parse_workbook(_workbook_bytes())

    assert len(records) == 2
    assert "system_salary_max" not in records[0]
    assert "system_salary_min" not in records[0]
    assert records[0]["salaries"] == [
        {"province": "北京", "city": "北京市", "salary": 16000.0}
    ]
    assert all(
        salary["city"] not in {"系统取值最大值", "系统取值最小值"}
        for record in records
        for salary in record["salaries"]
    )
def test_salary_fallback_uses_provincial_capital_from_social_insurance_city():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        bind=engine,
        tables=[
            JobPosition.__table__,
            JobPositionSalary.__table__,
            ChinaCityTier.__table__,
            CitySocialInsurance.__table__,
        ],
    )
    db = sessionmaker(bind=engine)()
    try:
        position = JobPosition(
            sequence_type="技术序列",
            category="运维类",
            position_name="桌面工程师",
            level_name="初级 (Junior/P1-P2)",
            level_rank=1,
        )
        db.add(position)
        db.flush()
        db.add_all(
            [
                JobPositionSalary(
                    position_id=position.id,
                    province="内蒙古",
                    city="呼和浩特市",
                    salary=6000,
                ),
                JobPositionSalary(
                    position_id=position.id,
                    province="北京",
                    city="北京市",
                    salary=12000,
                ),
                JobPositionSalary(
                    position_id=position.id,
                    province="上海",
                    city="上海市",
                    salary=14000,
                ),
                CitySocialInsurance(
                    province="内蒙古自治区",
                    city="阿拉善盟",
                    upper_limit=10000,
                    lower_limit=1000,
                    calc_base=1000,
                ),
            ]
        )
        db.commit()

        result = _query_salary_with_fallback(db, position.id, "阿拉善盟")

        assert result.salary == 6000
        assert result.source == "provincial_capital"
        assert result.source_city == "呼和浩特市"
    finally:
        db.close()
        engine.dispose()
