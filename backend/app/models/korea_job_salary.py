from sqlalchemy import Boolean, Column, DateTime, DECIMAL, Integer, String, UniqueConstraint, func

from app.database import Base


class KoreaJobSalary(Base):
    """韩国驻场岗位月薪（KRW）。"""

    __tablename__ = "korea_job_salary"
    __table_args__ = (
        UniqueConstraint("city", "position_name", name="uq_korea_job_salary_city_position"),
    )

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(50), nullable=False, index=True)
    position_name = Column(String(128), nullable=False, index=True)
    monthly_salary_krw = Column(DECIMAL(14, 2), nullable=False)
    notes = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
