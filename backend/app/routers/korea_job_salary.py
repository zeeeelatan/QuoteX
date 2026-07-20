from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.korea_job_salary import KoreaJobSalary
from app.schemas.korea_job_salary import (
    KoreaJobSalaryCreate,
    KoreaJobSalaryOut,
    KoreaJobSalaryUpdate,
)


router = APIRouter(prefix="/korea-job-salaries", tags=["韩国驻场岗位薪资"])


def _normalized(value: str) -> str:
    return value.strip()


def _duplicate_exists(
    db: Session,
    city: str,
    position_name: str,
    exclude_id: Optional[int] = None,
) -> bool:
    query = db.query(KoreaJobSalary).filter(
        KoreaJobSalary.city == city,
        KoreaJobSalary.position_name == position_name,
    )
    if exclude_id is not None:
        query = query.filter(KoreaJobSalary.id != exclude_id)
    return query.first() is not None


@router.get("/", response_model=List[KoreaJobSalaryOut])
def list_korea_job_salaries(
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(KoreaJobSalary)
    if active_only:
        query = query.filter(KoreaJobSalary.is_active.is_(True))
    return query.order_by(KoreaJobSalary.city, KoreaJobSalary.position_name).all()


@router.get("/options", response_model=List[KoreaJobSalaryOut])
def list_korea_job_salary_options(db: Session = Depends(get_db)):
    return (
        db.query(KoreaJobSalary)
        .filter(KoreaJobSalary.is_active.is_(True))
        .order_by(KoreaJobSalary.city, KoreaJobSalary.position_name)
        .all()
    )


@router.post("/", response_model=KoreaJobSalaryOut, status_code=201)
def create_korea_job_salary(payload: KoreaJobSalaryCreate, db: Session = Depends(get_db)):
    city = _normalized(payload.city)
    position_name = _normalized(payload.position_name)
    if _duplicate_exists(db, city, position_name):
        raise HTTPException(status_code=409, detail="该城市和岗位的韩国薪资已存在")

    record = KoreaJobSalary(
        city=city,
        position_name=position_name,
        monthly_salary_krw=payload.monthly_salary_krw,
        notes=payload.notes,
        is_active=payload.is_active,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=KoreaJobSalaryOut)
def update_korea_job_salary(
    record_id: int,
    payload: KoreaJobSalaryUpdate,
    db: Session = Depends(get_db),
):
    record = db.query(KoreaJobSalary).filter(KoreaJobSalary.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="韩国岗位薪资不存在")

    updates = payload.model_dump(exclude_unset=True)
    city = _normalized(updates.get("city", record.city))
    position_name = _normalized(updates.get("position_name", record.position_name))
    if _duplicate_exists(db, city, position_name, exclude_id=record_id):
        raise HTTPException(status_code=409, detail="该城市和岗位的韩国薪资已存在")

    updates["city"] = city
    updates["position_name"] = position_name
    for key, value in updates.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_korea_job_salary(record_id: int, db: Session = Depends(get_db)):
    record = db.query(KoreaJobSalary).filter(KoreaJobSalary.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="韩国岗位薪资不存在")
    db.delete(record)
    db.commit()
    return {"message": "删除成功"}
