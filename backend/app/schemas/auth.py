from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=2, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    name: str = Field(..., min_length=1, max_length=64, description="姓名")
    email: str | None = Field(None, max_length=128)


class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """登录/注册返回的令牌与用户信息"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    name: str
