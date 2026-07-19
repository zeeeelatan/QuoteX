"""智能体策略配置（对应计划推荐默认）。"""
import os

# 匹配结果需用户确认后才允许导出
REQUIRE_MATCH_CONFIRMATION = os.getenv("AGENT_REQUIRE_CONFIRM", "true").lower() in (
    "1",
    "true",
    "yes",
)

# 匹配率低于该阈值时标记为低置信，仍返回但不自动确认
LOW_MATCH_RATE_THRESHOLD = float(os.getenv("AGENT_LOW_MATCH_RATE", "70"))

# 无匹配时禁止模型编造价格（工具层强制）
FORBID_INVENTED_PRICES = True

# Tool calling 最大轮次
MAX_TOOL_ROUNDS = int(os.getenv("AGENT_MAX_TOOL_ROUNDS", "8"))

# 会话内存 TTL（秒）
SESSION_TTL_SECONDS = int(os.getenv("AGENT_SESSION_TTL", "7200"))

# 首期支持的报价类型（工具与提示词对齐）
SUPPORTED_QUOTE_TYPES = (
    "product_query",
    "maintenance",
    "lenovo",
    "onsite",
    "relocation",
    "other",
)
