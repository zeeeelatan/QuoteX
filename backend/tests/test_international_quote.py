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

    assert len(COUNTRY_DEFAULTS) == 16
    assert len(matrix["locations"]) == 49
    assert len(matrix["positions"]) == 119
    assert all(len(position["salaries"]) == 49 for position in matrix["positions"])
    assert len(matrix["locations"]) * len(matrix["positions"]) == 5831
    assert {item["country_code"] for item in matrix["locations"]} == {
        item["country_code"] for item in COUNTRY_DEFAULTS
    }
