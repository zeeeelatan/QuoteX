from sqlalchemy import Column, Integer, String, DateTime, func, Text
from app.database import Base


class UserProfile(Base):
    """用户个人资料（支持登录：username/password_hash）"""
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=True, index=True)  # 登录用户名（自主注册用户必填）
    password_hash = Column(String(255), nullable=True)  # 密码哈希
    name = Column(String(64), nullable=False)  # 姓名
    employee_id = Column(String(32), unique=True, nullable=True)  # 工号（自主注册可为空或自动生成）
    department = Column(String(64), nullable=True)  # 所属部门
    position = Column(String(64), nullable=True)  # 当前职位
    avatar = Column(Text, nullable=True)  # 头像URL
    phone = Column(String(32), nullable=True)  # 手机号
    email = Column(String(128), nullable=True)  # 邮箱
    email_verified = Column(Integer, default=0)  # 邮箱是否验证 0-未验证 1-已验证
    sales_region = Column(String(32), default='east')  # 销售区域
    currency = Column(String(8), default='CNY')  # 默认币种
    permission_level = Column(String(32), default='普通报价师')  # 权限等级
    tags = Column(Text, nullable=True)  # 常用客户标签，JSON格式
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CompanyInfo(Base):
    """公司信息"""
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # 关联用户ID
    company_name = Column(String(255), nullable=False)  # 公司名称
    company_address = Column(String(512), nullable=True)  # 公司地址
    company_website = Column(String(255), nullable=True)  # 官网地址
    company_logo = Column(Text, nullable=True)  # 公司Logo（base64格式）
    is_default = Column(Integer, default=0)  # 是否默认公司 0-否 1-是
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Customer(Base):
    """客户信息"""
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # 创建人用户ID
    customer_name = Column(String(255), nullable=False)  # 客户名称
    contact_person = Column(String(64), nullable=True)  # 联系人
    contact_phone = Column(String(64), nullable=True)  # 联系方式
    customer_address = Column(String(512), nullable=True)  # 客户地址
    tags = Column(Text, nullable=True)  # 客户标签
    notes = Column(Text, nullable=True)  # 备注
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
