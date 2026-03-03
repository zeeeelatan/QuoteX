"""应用启动时确保默认管理员账户存在（可通过环境变量覆盖）"""
import logging
import os
from passlib.context import CryptContext

from app.database import SessionLocal
from app.models.user_profile import UserProfile

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_NAME = os.getenv("DEFAULT_ADMIN_NAME", "Admin")
DEFAULT_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

# bcrypt 最多 72 字节，统一截断避免报错
def _truncate_72(s: str) -> str:
    b = s.encode("utf-8")
    return b[:72].decode("utf-8", errors="replace") if len(b) > 72 else s


def ensure_default_user() -> None:
    """若表中无 username 列会静默跳过，不阻塞启动"""
    db = SessionLocal()
    try:
        profile = (
            db.query(UserProfile).filter(UserProfile.name == DEFAULT_NAME).first()
            or db.query(UserProfile).filter(UserProfile.username == DEFAULT_USERNAME).first()
        )
        if profile:
            profile.username = DEFAULT_USERNAME
            profile.password_hash = pwd_context.hash(_truncate_72(DEFAULT_PASSWORD))
            profile.name = DEFAULT_NAME
            db.commit()
            logger.info("默认账户已更新: username=%s", DEFAULT_USERNAME)
        else:
            profile = UserProfile(
                name=DEFAULT_NAME,
                username=DEFAULT_USERNAME,
                password_hash=pwd_context.hash(_truncate_72(DEFAULT_PASSWORD)),
                employee_id=None,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            if not profile.employee_id:
                profile.employee_id = f"U{profile.id}"
                db.commit()
            logger.info("默认账户已创建: username=%s, id=%s", DEFAULT_USERNAME, profile.id)
    except Exception as e:
        db.rollback()
        logger.warning("默认账户初始化跳过（可能尚未执行迁移）: %s", e)
    finally:
        db.close()
