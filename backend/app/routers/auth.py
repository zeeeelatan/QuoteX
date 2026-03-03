"""用户注册与登录"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_profile import UserProfile
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_profile,
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """用户自主注册"""
    existing = db.query(UserProfile).filter(UserProfile.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被使用")

    profile = UserProfile(
        username=data.username,
        password_hash=hash_password(data.password),
        name=data.name,
        email=data.email or "",
        employee_id=None,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    # 补全工号便于兼容旧逻辑
    if not profile.employee_id:
        profile.employee_id = f"U{profile.id}"
        db.commit()
        db.refresh(profile)

    token = create_access_token(profile.id)
    return TokenResponse(
        access_token=token,
        user_id=profile.id,
        username=profile.username or "",
        name=profile.name,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    profile = db.query(UserProfile).filter(UserProfile.username == data.username).first()
    if not profile or not profile.password_hash:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(data.password, profile.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(profile.id)
    return TokenResponse(
        access_token=token,
        user_id=profile.id,
        username=profile.username or "",
        name=profile.name,
    )


@router.get("/me", response_model=TokenResponse)
def me(profile: UserProfile = Depends(get_current_user_profile)):
    """获取当前登录用户信息（需携带有效 token）"""
    return TokenResponse(
        access_token="",  # 前端继续使用原有 token
        user_id=profile.id,
        username=profile.username or "",
        name=profile.name,
    )
