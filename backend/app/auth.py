"""JWT 认证：创建/校验 token，获取当前用户"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_profile import UserProfile

# 从环境变量读取密钥，默认仅开发用
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def _truncate_password_72(password: str) -> str:
    """bcrypt 只接受最多 72 字节，超出需截断"""
    b = password.encode("utf-8")
    if len(b) <= 72:
        return password
    return b[:72].decode("utf-8", errors="replace")


def hash_password(password: str) -> str:
    return pwd_context.hash(_truncate_password_72(password))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_truncate_password_72(plain), hashed)


def create_access_token(subject: int) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        return int(sub) if sub else None
    except jwt.PyJWTError:
        return None


def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[int]:
    """从 Bearer token 解析出 user_id，未携带或无效时返回 None"""
    if not credentials or credentials.credentials is None:
        return None
    return decode_token(credentials.credentials)


def get_current_user_required(
    user_id: Optional[int] = Depends(get_current_user_id),
) -> int:
    """要求已登录，否则 401"""
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def get_current_user_profile(
    user_id: int = Depends(get_current_user_required),
    db: Session = Depends(get_db),
) -> UserProfile:
    """要求已登录并返回当前用户资料对象"""
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return profile
