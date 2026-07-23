from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.international_quote_rules import country_seed_rows
from app.models.international_quote import InternationalCountryRule, InternationalJobSalary


DATA_FILE = Path(__file__).resolve().parent / "data" / "international_salary_matrix.json"


def ensure_international_quote_data(db: Session) -> None:
    existing_codes = {
        code for (code,) in db.query(InternationalCountryRule.country_code).all()
    }
    for payload in country_seed_rows():
        if payload["country_code"] not in existing_codes:
            db.add(InternationalCountryRule(**payload))
    db.flush()

    if db.query(InternationalJobSalary.id).first() is not None:
        db.commit()
        return

    matrix = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    locations = matrix["locations"]
    batch = []
    for position in matrix["positions"]:
        for location, salary in zip(locations, position["salaries"]):
            batch.append(
                {
                    **location,
                    "sequence_type": position["sequence_type"],
                    "category": position["category"],
                    "position_name": position["position_name"],
                    "level_name": position["level_name"],
                    "level_rank": position["level_rank"],
                    "monthly_salary": salary,
                    "notes": f"来源：{matrix['source']}",
                    "is_active": True,
                }
            )
            if len(batch) >= 1000:
                db.bulk_insert_mappings(InternationalJobSalary, batch)
                batch.clear()
    if batch:
        db.bulk_insert_mappings(InternationalJobSalary, batch)
    db.commit()
