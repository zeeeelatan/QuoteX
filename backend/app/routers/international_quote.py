from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.international_quote_rules import calculate_employer_rules
from app.models.international_quote import InternationalCountryRule, InternationalJobSalary
from app.schemas.international_quote import (
    InternationalCalculationOut,
    InternationalCalculationRequest,
    InternationalCountryRuleOut,
    InternationalCountryRuleUpdate,
    InternationalJobSalaryCreate,
    InternationalJobSalaryOut,
    InternationalJobSalaryUpdate,
)


router = APIRouter(prefix="/international-quote", tags=["国际驻场报价"])


@router.get("/countries", response_model=List[InternationalCountryRuleOut])
def list_countries(active_only: bool = Query(True), db: Session = Depends(get_db)):
    query = db.query(InternationalCountryRule)
    if active_only:
        query = query.filter(InternationalCountryRule.is_active.is_(True))
    return query.order_by(InternationalCountryRule.id).all()


@router.put("/countries/{country_code}", response_model=InternationalCountryRuleOut)
def update_country(country_code: str, payload: InternationalCountryRuleUpdate, db: Session = Depends(get_db)):
    record = db.query(InternationalCountryRule).filter(InternationalCountryRule.country_code == country_code).first()
    if record is None:
        raise HTTPException(status_code=404, detail="国家报价规则不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.get("/salaries", response_model=List[InternationalJobSalaryOut])
def list_salaries(
    country_code: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    active_only: bool = Query(False),
    limit: int = Query(500, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(InternationalJobSalary)
    if country_code:
        query = query.filter(InternationalJobSalary.country_code == country_code)
    if city:
        query = query.filter(InternationalJobSalary.city == city)
    if keyword:
        query = query.filter(InternationalJobSalary.position_name.ilike(f"%{keyword}%"))
    if active_only:
        query = query.filter(InternationalJobSalary.is_active.is_(True))
    return query.order_by(
        InternationalJobSalary.country_code,
        InternationalJobSalary.city,
        InternationalJobSalary.sequence_type,
        InternationalJobSalary.position_name,
        InternationalJobSalary.level_rank,
    ).offset(offset).limit(limit).all()


@router.get("/salaries/options", response_model=List[InternationalJobSalaryOut])
def salary_options(country_code: str, city: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(InternationalJobSalary).filter(
        InternationalJobSalary.country_code == country_code,
        InternationalJobSalary.is_active.is_(True),
    )
    if city:
        query = query.filter(InternationalJobSalary.city == city)
    return query.order_by(
        InternationalJobSalary.city,
        InternationalJobSalary.sequence_type,
        InternationalJobSalary.position_name,
        InternationalJobSalary.level_rank,
    ).all()


@router.post("/salaries", response_model=InternationalJobSalaryOut, status_code=201)
def create_salary(payload: InternationalJobSalaryCreate, db: Session = Depends(get_db)):
    record = InternationalJobSalary(**payload.model_dump())
    db.add(record)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="该国家、地区、城市、岗位和级别的薪资已存在")
    db.refresh(record)
    return record


@router.put("/salaries/{record_id}", response_model=InternationalJobSalaryOut)
def update_salary(record_id: int, payload: InternationalJobSalaryUpdate, db: Session = Depends(get_db)):
    record = db.query(InternationalJobSalary).filter(InternationalJobSalary.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="国际岗位薪资不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="该国家、地区、城市、岗位和级别的薪资已存在")
    db.refresh(record)
    return record


@router.delete("/salaries/{record_id}")
def delete_salary(record_id: int, db: Session = Depends(get_db)):
    record = db.query(InternationalJobSalary).filter(InternationalJobSalary.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="国际岗位薪资不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}


@router.post("/calculate", response_model=InternationalCalculationOut)
def calculate(payload: InternationalCalculationRequest):
    try:
        return calculate_employer_rules(payload.country_code, payload.monthly_salary, payload.parameters)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
