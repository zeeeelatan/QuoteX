#!/usr/bin/env python3
"""设置默认账户：杨昆 / yangkun / 123456（若已存在则更新用户名与密码）"""
import os
import sys

# 保证从 backend 目录运行时能导入 app
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.database import SessionLocal
from app.models.user_profile import UserProfile
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_NAME = "杨昆"
DEFAULT_USERNAME = "yangkun"
DEFAULT_PASSWORD = "123456"


def seed_default_user():
    db = SessionLocal()
    try:
        # 优先按姓名「杨昆」查找，其次按用户名 yangkun
        profile = (
            db.query(UserProfile).filter(UserProfile.name == DEFAULT_NAME).first()
            or db.query(UserProfile).filter(UserProfile.username == DEFAULT_USERNAME).first()
        )
        if profile:
            profile.username = DEFAULT_USERNAME
            profile.password_hash = pwd_context.hash(DEFAULT_PASSWORD)
            profile.name = DEFAULT_NAME
            db.commit()
            db.refresh(profile)
            print(f"已更新默认账户：id={profile.id}, name={profile.name}, username={profile.username}")
        else:
            profile = UserProfile(
                name=DEFAULT_NAME,
                username=DEFAULT_USERNAME,
                password_hash=pwd_context.hash(DEFAULT_PASSWORD),
                employee_id=None,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            if not profile.employee_id:
                profile.employee_id = f"U{profile.id}"
                db.commit()
            print(f"已创建默认账户：id={profile.id}, name={profile.name}, username={profile.username}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"设置默认账户失败: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(seed_default_user())
