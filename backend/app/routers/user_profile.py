from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.user_profile import (
    UserProfileCreate, UserProfileUpdate, UserProfileOut,
    CompanyInfoCreate, CompanyInfoUpdate, CompanyInfoOut,
    CustomerCreate, CustomerUpdate, CustomerOut
)
from app.models.user_profile import UserProfile, CompanyInfo, Customer
from app.database import get_db
from app.auth import get_current_user_required, get_current_user_id, get_current_user_profile

router = APIRouter(prefix="/user-profile", tags=["用户资料管理"])

# 未登录时返回的默认资料，避免前端 500
DEFAULT_PROFILE = UserProfileOut(
    id=0,
    name="访客",
    employee_id=None,
    department=None,
    position="",
    avatar=None,
    phone=None,
    email=None,
    email_verified=0,
    sales_region="east",
    currency="CNY",
    permission_level="普通报价师",
    tags=None,
    created_at=None,
    updated_at=None,
)


# ============ 用户资料 ============

@router.get("/", response_model=UserProfileOut)
def get_user_profile(
    user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取当前登录用户资料；未登录时返回默认访客资料，避免前端报错。"""
    if user_id is None:
        return DEFAULT_PROFILE
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            return DEFAULT_PROFILE
        return profile
    except Exception:
        return DEFAULT_PROFILE


@router.put("/", response_model=UserProfileOut)
def update_user_profile(
    profile_data: UserProfileUpdate,
    profile: UserProfile = Depends(get_current_user_profile),
    db: Session = Depends(get_db),
):
    """更新当前用户资料"""
    for k, v in profile_data.dict(exclude_unset=True).items():
        setattr(profile, k, v)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/", response_model=UserProfileOut)
def create_user_profile(profile: UserProfileCreate, db: Session = Depends(get_db)):
    """创建用户资料（内部/管理用；普通用户请使用 /auth/register）"""
    if profile.employee_id:
        existing = db.query(UserProfile).filter(UserProfile.employee_id == profile.employee_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="工号已存在")
    db_profile = UserProfile(
        name=profile.name,
        employee_id=profile.employee_id or None,
        department=profile.department,
        position=profile.position,
        avatar=profile.avatar,
        phone=profile.phone,
        email=profile.email,
        sales_region=profile.sales_region or "east",
        currency=profile.currency or "CNY",
        permission_level=profile.permission_level or "普通报价师",
        tags=profile.tags,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


# ============ 公司信息 ============

@router.get("/companies", response_model=List[CompanyInfoOut])
def list_companies(
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """获取当前用户的所有公司信息"""
    companies = db.query(CompanyInfo).filter(CompanyInfo.user_id == user_id).all()
    if not companies:
        default_company = CompanyInfo(
            user_id=user_id,
            company_name="北京智能科技有限公司",
            company_address="北京市海淀区科技园A座12层",
            company_website="https://www.aimatic-tech.com",
            is_default=1,
        )
        db.add(default_company)
        db.commit()
        db.refresh(default_company)
        companies = [default_company]
    return companies


@router.post("/companies", response_model=CompanyInfoOut)
def create_company(
    company: CompanyInfoCreate,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """创建公司信息（归属当前用户）"""
    db_company = CompanyInfo(
        user_id=user_id,
        company_name=company.company_name,
        company_address=company.company_address,
        company_website=company.company_website,
        company_logo=company.company_logo,
        is_default=company.is_default or 0,
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.put("/companies/{company_id}", response_model=CompanyInfoOut)
def update_company(
    company_id: int,
    company_data: CompanyInfoUpdate,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """更新公司信息（仅限当前用户）"""
    company = db.query(CompanyInfo).filter(CompanyInfo.id == company_id, CompanyInfo.user_id == user_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")

    for k, v in company_data.dict(exclude_unset=True).items():
        setattr(company, k, v)

    db.commit()
    db.refresh(company)
    return company


@router.delete("/companies/{company_id}")
def delete_company(
    company_id: int,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """删除公司信息（仅限当前用户）"""
    company = db.query(CompanyInfo).filter(CompanyInfo.id == company_id, CompanyInfo.user_id == user_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")

    db.delete(company)
    db.commit()
    return {"ok": True}


# ============ 客户信息 ============

@router.get("/customers", response_model=List[CustomerOut])
def list_customers(
    user_id: int = Depends(get_current_user_required),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取当前用户的客户列表"""
    query = db.query(Customer).filter(Customer.user_id == user_id)
    if search:
        query = query.filter(
            (Customer.customer_name.contains(search)) |
            (Customer.contact_person.contains(search)) |
            (Customer.contact_phone.contains(search))
        )
    return query.order_by(Customer.updated_at.desc()).all()


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """获取单个客户详情（仅限当前用户）"""
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.user_id == user_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


@router.post("/customers", response_model=CustomerOut)
def create_customer(
    customer: CustomerCreate,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """创建客户（归属当前用户）"""
    db_customer = Customer(
        user_id=user_id,
        customer_name=customer.customer_name,
        contact_person=customer.contact_person,
        contact_phone=customer.contact_phone,
        customer_address=customer.customer_address,
        tags=customer.tags,
        notes=customer.notes,
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """更新客户（仅限当前用户）"""
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.user_id == user_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    for k, v in customer_data.dict(exclude_unset=True).items():
        setattr(customer, k, v)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """删除客户（仅限当前用户）"""
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.user_id == user_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    db.delete(customer)
    db.commit()
    return {"ok": True}


@router.post("/customers/batch")
def batch_create_customers(
    customers: List[CustomerCreate],
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """批量创建客户（归属当前用户）"""
    created = []
    for c in customers:
        db_customer = Customer(
            user_id=user_id,
            customer_name=c.customer_name,
            contact_person=c.contact_person,
            contact_phone=c.contact_phone,
            customer_address=c.customer_address,
            tags=c.tags,
            notes=c.notes,
        )
        db.add(db_customer)
        created.append(db_customer)
    db.commit()
    for c in created:
        db.refresh(c)
    return {"ok": True, "created_count": len(created)}
