"""专用智能体：Tool Calling 编排层。

产品决策（计划默认值）：
- 智能体只做编排，价格一律由工具/后端计算
- 首期：产品查询 + 维保报价（含 BOM）+ Excel；PDF / 联想 / 驻场 / 搬迁随后
- 匹配结果默认需用户确认后才能导出
- 无匹配不编造价格
"""

from app.agent.runtime import run_agent_stream

__all__ = ["run_agent_stream"]
