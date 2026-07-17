from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class QuoteLiveSnapshot(Base):
    """实时报价快照 - 按外部引用令牌(external_ref)保存"生成报价单"页面的实时状态

    供第三方系统（如 TopSales）在用户尚未点击"完成报价"前，
    实时拉取当前报价金额与导出的报价单文件。
    ref 由调用方生成的高强度随机字符串（UUID）充当查询凭证，安全模型与
    quote_history 的 by-ref 接口一致（"分享链接"模式）。
    """
    __tablename__ = "quote_live_snapshot"

    id = Column(Integer, primary_key=True, index=True)
    external_ref = Column(String(64), unique=True, index=True, nullable=False)

    # 实时值快照：{ subtotal, tax_rate, total, valid_days, service_level, project_name, quote_number, device_count }
    data = Column(JSON, nullable=True)

    # 导出的报价单文件：[{ name, size, type, data(base64) }]，由"导出Excel"时上传
    files = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<QuoteLiveSnapshot(id={self.id}, external_ref={self.external_ref})>"
