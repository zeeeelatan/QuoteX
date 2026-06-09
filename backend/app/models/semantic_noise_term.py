"""语义噪声词候选表

存储从 manual_matching_override 已确认记录中自动挖掘出的「设备类型/噪声词」候选。
候选默认 status='pending'，经人工在后台审核为 'approved' 后才会进入 extractor
的运行期词典生效；'rejected' 的词不再挖掘提示。这样既能让词典随用户确认
自我进化，又能避免伪噪声（型号尾码等）污染匹配。
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from app.database import Base


class SemanticNoiseTerm(Base):
    __tablename__ = "semantic_noise_term"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(128), nullable=False, unique=True, comment="噪声词/设备类型词")
    term_type = Column(String(32), default="device_type",
                       comment="词类型: device_type/modifier/series")
    lang = Column(String(8), default="cn", comment="语言: cn/en")
    frequency = Column(Integer, default=0, comment="在已确认记录中的出现频次")
    status = Column(String(16), default="pending", index=True,
                    comment="审核状态: pending/approved/rejected")
    source = Column(String(32), default="miner", comment="来源: miner/manual")
    notes = Column(Text, comment="备注")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<SemanticNoiseTerm(term={self.term!r}, status={self.status}, freq={self.frequency})>"


Index("ix_semantic_noise_term_status_type", SemanticNoiseTerm.status, SemanticNoiseTerm.term_type)
