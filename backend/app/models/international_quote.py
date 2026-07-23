from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    DECIMAL,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)

from app.database import Base


class InternationalCountryRule(Base):
    __tablename__ = "international_country_rule"

    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(32), nullable=False, unique=True, index=True)
    country_name = Column(String(64), nullable=False)
    default_city = Column(String(64), nullable=False)
    currency = Column(String(8), nullable=False)
    currency_symbol = Column(String(12), nullable=False)
    currency_precision = Column(Integer, nullable=False, default=2)
    exchange_rate_cny = Column(DECIMAL(18, 8), nullable=False)
    exchange_rate_date = Column(Date, nullable=False)
    eor_rate = Column(DECIMAL(8, 4), nullable=False, default=12)
    management_rate = Column(DECIMAL(8, 4), nullable=False, default=12)
    profit_rate = Column(DECIMAL(8, 4), nullable=False, default=8)
    vat_rate = Column(DECIMAL(8, 4), nullable=False, default=6)
    local_vat_rate = Column(DECIMAL(8, 4), nullable=False, default=0)
    local_vat_enabled = Column(Boolean, nullable=False, default=False)
    effective_label = Column(String(128), nullable=False)
    employee_profile = Column(String(200), nullable=False)
    parameter_config = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class InternationalJobSalary(Base):
    __tablename__ = "international_job_salary"
    __table_args__ = (
        UniqueConstraint(
            "country_code",
            "region",
            "city",
            "sequence_type",
            "position_name",
            "level_name",
            name="uq_international_salary_location_position_level",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(32), nullable=False, index=True)
    country_name = Column(String(64), nullable=False)
    region = Column(String(128), nullable=False, default="")
    city = Column(String(64), nullable=False, index=True)
    currency = Column(String(8), nullable=False)
    sequence_type = Column(String(32), nullable=False)
    category = Column(String(64), nullable=False)
    position_name = Column(String(128), nullable=False, index=True)
    level_name = Column(String(128), nullable=False)
    level_rank = Column(Integer, nullable=False)
    monthly_salary = Column(DECIMAL(18, 2), nullable=False)
    notes = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
