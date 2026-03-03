from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, JSON
from sqlalchemy.sql import func
from app.database import Base


class QuoteHistory(Base):
    """报价单历史记录表 - 保存报价完整快照"""
    __tablename__ = "quote_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)      # 关联用户ID（未登录为 None，用于数据隔离）

    # 基本信息
    file_name = Column(String(255), nullable=False)           # 导入文件名称
    user_name = Column(String(100), nullable=False)           # 用户名称
    status = Column(String(20), nullable=False, default='completed')  # 状态: completed, processing, failed

    # 价格信息
    total_amount = Column(Numeric(14, 2))                     # 报价总额

    # 数据快照 - 保存各节点的完整数据
    # 导入数据节点 - 原始上传的Excel数据
    import_data = Column(JSON, nullable=True)                 # { headers: [], data: [], converted: { headers, data } }

    # 数据匹配节点 - 匹配完成后的设备数据
    match_data = Column(JSON, nullable=True)                  # 匹配后的设备列表 [{ manufacturer, model, ... }]

    # 价格调整节点 - 服务级别调整后的数据
    price_adjust_data = Column(JSON, nullable=True)           # 价格调整后的数据

    # 生成报价节点 - 最终报价单数据
    quote_data = Column(JSON, nullable=True)                  # 最终报价单数据 { original: [], converted: [] }

    # 报价单元数据 - 用于历史记录详情展示
    quote_metadata = Column(JSON, nullable=True)             # { quote_number, quote_date, table_data, ... }

    # 页面UI状态 - 用于恢复各页面的UI状态
    page_states = Column(JSON, nullable=True)                # { doc_recognition: {...}, smart_matching: {...}, ... }

    # 元数据
    data_source = Column(String(50), default='datacenter')    # 数据来源: datacenter/office/hybrid
    device_count = Column(Integer, default=0)                 # 设备数量
    draft_stage = Column(String(50), nullable=True)           # 草稿阶段: doc_recognition, smart_matching, price_adjustment, quotation_generation

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<QuoteHistory(id={self.id}, file_name={self.file_name}, status={self.status})>"
