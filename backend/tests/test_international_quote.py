import json
from pathlib import Path

import pytest

from app.international_quote_rules import COUNTRY_DEFAULTS, calculate_employer_rules


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """These rule and seed-shape tests do not require a database connection."""
    yield


@pytest.mark.parametrize(
    ("country_code", "salary", "parameters", "expected_total"),
    [
        ("france", 2500, {}, 1028),
        ("korea", 5640000, {}, 571558),
        ("hong_kong", 25000, {}, 1750),
        ("hong_kong", 40000, {"employees_compensation_insurance": 2000}, 3500),
        ("netherlands", 3500, {}, 1012.2),
        ("spain", 2500, {}, 803.75),
        ("hungary", 600000, {}, 78000),
        ("turkey", 60000, {}, 14250),
        ("uae", 15000, {}, 1549.5),
        ("japan", 350000, {}, 56351),
        ("vietnam", 15000000, {}, 3525000),
        ("thailand", 30000, {}, 910),
        ("malaysia", 5000, {}, 797.5),
        ("singapore", 6000, {}, 1061.25),
        ("norway", 50000, {}, 8300),
        ("finland", 4000, {}, 795.6),
        ("russia", 120000, {}, 36240),
        ("germany", 4500, {}, 1077.75),
        ("switzerland", 8000, {}, 950.85),
    ],
)
def test_country_employer_rule_samples(country_code, salary, parameters, expected_total):
    result = calculate_employer_rules(country_code, salary, parameters)
    assert result["employer_total"] == expected_total


def test_international_salary_matrix_is_complete():
    data_file = Path(__file__).resolve().parents[1] / "app" / "data" / "international_salary_matrix.json"
    matrix = json.loads(data_file.read_text(encoding="utf-8"))

    assert len(COUNTRY_DEFAULTS) == 18
    assert len(matrix["locations"]) == 54
    assert len(matrix["positions"]) == 119
    assert all(len(position["salaries"]) == 54 for position in matrix["positions"])
    assert len(matrix["locations"]) * len(matrix["positions"]) == 6426
    matrix_country_codes = {item["country_code"] for item in matrix["locations"]}
    countries_with_salary_matrix = {
        item["country_code"]
        for item in COUNTRY_DEFAULTS
        if item["country_code"] != "hong_kong"
    }
    assert matrix_country_codes == countries_with_salary_matrix

    korea_locations = [
        item for item in matrix["locations"] if item["country_code"] == "korea"
    ]
    assert [item["city"] for item in korea_locations] == [
        "首尔",
        "釜山",
        "仁川",
        "水原",
        "春川",
    ]


def test_hong_kong_employees_compensation_insurance_is_clamped():
    below_minimum = calculate_employer_rules(
        "hong_kong", 25000, {"employees_compensation_insurance": 100}
    )
    above_maximum = calculate_employer_rules(
        "hong_kong", 25000, {"employees_compensation_insurance": 5000}
    )

    assert below_minimum["employer_total"] == 1750
    assert above_maximum["employer_total"] == 3250


def test_hong_kong_insurance_parameter_metadata():
    hong_kong = next(
        item for item in COUNTRY_DEFAULTS if item["country_code"] == "hong_kong"
    )
    insurance = hong_kong["parameter_config"][0]

    assert insurance["default"] == 500
    assert insurance["min"] == 500
    assert insurance["max"] == 2000
    assert insurance["suffix"] == "HKD/月"
