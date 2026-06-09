"""语义匹配模块

在自动匹配之前对原始型号做「语义字段抽取」：把一段混杂的原始写法
（如 "监控接入交换机HUAWEI S5720"）拆解成结构化字段：
    品牌 brand / 设备类型 device_type / 型号核心串 core / 配置 config

后续匹配只用 core 串参与相似度计算，品牌单独作校验维度，从而避免
设备类型词、品牌词、配置参数等噪声稀释型号相似度。
"""
from app.semantic.extractor import extract_fields, SemanticFields, is_semantic_enabled

__all__ = ["extract_fields", "SemanticFields", "is_semantic_enabled"]
