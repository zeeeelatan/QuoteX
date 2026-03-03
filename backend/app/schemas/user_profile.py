from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# 用户资料
class UserProfileBase(BaseModel):
    name: str
    employee_id: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[int] = 0
    sales_region: Optional[str] = 'east'
    currency: Optional[str] = 'CNY'
    permission_level: Optional[str] = '普通报价师'
    tags: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    sales_region: Optional[str] = None
    currency: Optional[str] = None
    tags: Optional[str] = None


class UserProfileOut(UserProfileBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 公司信息
class CompanyInfoBase(BaseModel):
    company_name: str
    company_address: Optional[str] = None
    company_website: Optional[str] = None
    company_logo: Optional[str] = None
    is_default: Optional[int] = 0


class CompanyInfoCreate(CompanyInfoBase):
    user_id: Optional[int] = 1


class CompanyInfoUpdate(BaseModel):
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_website: Optional[str] = None
    company_logo: Optional[str] = None
    is_default: Optional[int] = None


class CompanyInfoOut(CompanyInfoBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 客户信息
class CustomerBase(BaseModel):
    customer_name: str
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    customer_address: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    user_id: Optional[int] = None


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    customer_address: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class CustomerOut(CustomerBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
