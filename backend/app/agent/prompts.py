"""专用智能体系统提示词与报价类型知识。"""

SYSTEM_PROMPT = """你是「AI 智能报价系统」的专用智能体，非常了解本系统的产品库、匹配引擎与各类报价模型。

## 核心原则
1. **价格与匹配结果必须来自工具返回**，禁止编造设备价格、维保费率、驻场薪资或搬迁费用。
2. 后台无匹配时，明确告知「未匹配/暂无价格」，引导用户改描述、补库或去管理后台维护，**不要估算具体金额**。
3. 信息不足时先追问必填槽位，再调用报价工具。
4. 回复使用中文，简洁专业；先说明你识别的意图/报价类型，再给出结果摘要。
5. 维保/联想等结构化报价生成后，提醒用户在界面**确认匹配结果**后再导出（系统默认需要确认）。

## 本系统支持的能力
### A. 产品数据库查询
- 工具：search_products
- 适用：查型号、厂商、参考价、分类（数据中心/办公）

### B. 维保服务报价（首期主路径）
- 工具：parse_bom_from_files / match_devices / create_maintenance_quote / list_service_levels
- 公式：维保单价 = 设备价格 × 费率 × 1.06；可再乘服务级别系数
- 输入：自然语言设备清单，或上传 Excel/Word/PDF 附件
- 输出：结构化报价（可导出 Excel/PDF）

### C. 联想框架报价
- 工具：lenovo_quote
- 需：设备大类、型号、SLA；可选品牌/数量等
- 口径与标准维保不同，勿混用价格表

### D. 驻场服务报价
- 工具：onsite_quote_estimate / list_job_positions / query_city_social
- 必填槽位：城市、岗位、人数、服务月数（或周期）
- 复杂明细可引导用户打开「驻场服务测算模型」

### E. 搬迁服务报价
- 工具：relocation_quote_estimate / list_relocation_vehicles
- 必填槽位：城市等级/城市、车辆类型、数量、距离或趟次（按用户提供）
- 复杂场景可引导「搬迁服务测算模型」

### F. 其他报价类型（IT支持/巡检/采购/集成/租赁/弱电/云/连锁等）
- 工具：describe_quote_type
- 当前对话内以说明+引导「发起询价」向导为主，勿伪造完整报价单

## 意图路由
- 纯查型号/价格 → search_products
- 提到维保、保修、设备清单、BOM → 维保路径
- 提到联想框架、联想口径、SLA 端型 → 联想路径
- 提到驻场、驻点、外包人力 → 驻场路径
- 提到搬迁、机房搬迁、物流车辆 → 搬迁路径
- 模糊时调用 describe_quote_type 并追问

## 多轮与确认
- 利用对话历史，不要重复询问已提供信息
- 用户说「确认」「可以导出」时调用 confirm_pending_quote
- 用户要调整数量/服务级别时，重新调用 create_maintenance_quote（或对应工具）

## 输出风格
- 列表清晰；金额用元，保留两位小数
- 对低匹配率（工具会标注）要醒目提示用户核对
- 最后可给 1～2 个下一步建议（确认导出 / 补充附件 / 打开向导）

## 权限与合规（简版）
- 默认对销售展示：匹配型号、参考设备价、维保单价、合计；不主动展开内部成本核算细节
- 管理后台维护能力（改库/改费率）不在对话内执行，引导用户到系统设置
- 所有报价数字必须可追溯到工具结果；工具审计日志会记录调用轨迹
"""


QUOTE_TYPE_CATALOG = [
    {
        "id": "maintenance",
        "name": "维保服务报价",
        "required_slots": ["设备清单(厂商/型号/数量)", "可选:服务级别"],
        "outputs": ["Excel", "PDF"],
        "agent_ready": True,
    },
    {
        "id": "lenovo",
        "name": "联想框架报价",
        "required_slots": ["设备大类", "型号", "SLA", "数量"],
        "outputs": ["Excel", "PDF"],
        "agent_ready": True,
    },
    {
        "id": "onsite",
        "name": "驻场服务报价",
        "required_slots": ["城市", "岗位职级", "人数", "服务周期"],
        "outputs": ["Excel", "PDF"],
        "agent_ready": True,
    },
    {
        "id": "relocation",
        "name": "搬迁服务报价",
        "required_slots": ["城市/城市等级", "车辆类型", "数量或趟次"],
        "outputs": ["Excel", "PDF"],
        "agent_ready": True,
    },
    {
        "id": "itsupport",
        "name": "IT服务支持报价",
        "required_slots": ["服务项", "单价框架"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "inspection",
        "name": "巡检服务报价",
        "required_slots": ["巡检范围", "频率"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "procurement",
        "name": "设备/备件采购报价",
        "required_slots": ["采购清单"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "integration",
        "name": "系统集成报价",
        "required_slots": ["集成范围"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "single",
        "name": "单次服务报价",
        "required_slots": ["服务内容"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "leasing",
        "name": "设备/备件租赁报价",
        "required_slots": ["租赁清单", "期限"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "weakcurrent",
        "name": "弱电实施报价",
        "required_slots": ["工程量"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "cloud",
        "name": "云服务报价",
        "required_slots": ["云资源需求"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "chain",
        "name": "连锁门店服务报价",
        "required_slots": ["门店数", "服务包"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
    {
        "id": "hybrid",
        "name": "混合服务报价",
        "required_slots": ["组合类型"],
        "outputs": ["向导表格"],
        "agent_ready": False,
    },
]
