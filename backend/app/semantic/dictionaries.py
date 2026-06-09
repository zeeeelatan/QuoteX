"""语义抽取种子词典（人工校准，高置信度）

词表来源：对 manual_matching_override 表 634 条已确认记录做规律挖掘后，
人工筛除伪噪声（如型号尾码 AB/JQ）得到。运行期还会叠加从数据库
semantic_noise_term 表加载的、已审核通过的动态候选词（见 extractor）。

注意：
- DEVICE_TYPE_TERMS / 中文品牌按「长词优先」剥离，模块加载时已排序。
- 系列名默认从核心串剥离，但通过 SERIES_BRAND_MAP 反推品牌作为弱信号。
"""

# ───────────── 设备类型词（中文为主，含场景前缀复合词）─────────────
# 长词必须排在短词前面由 _sorted() 保证，避免 "接入交换机" 被 "交换机" 先吃掉。
DEVICE_TYPE_TERMS = [
    # 复合 / 带场景前缀
    "智慧服务区系统接入交换机",
    "上网行为管理",
    "监控接入交换机",
    "办公接入交换机",
    "收费接入交换机",
    "核心交换机",
    "汇聚交换机",
    "接入交换机",
    "存储服务器",
    "笔记本电脑",
    "戴尔存储",
    "光交换机",
    "磁盘阵列",
    "磁带库",
    "服务器",
    "交换机",
    "防火墙",
    "路由器",
    "工作站",
    "一体机",
    "刀片",
    "机箱",
    "存储",
    "带库",
    "网关",
    "硬盘",
    "设备",
]

# ───────────── 配置 / 修饰噪声词（剥离，无品牌含义）─────────────
MODIFIER_TERMS = [
    "新一代",
    "总装",
    "英寸",
    "量子",
    "国产",
]

# ───────────── 中文品牌词（剥离并用于品牌识别）─────────────
# 仅作种子兜底；运行期优先查 manufacturer 字典表。
BRAND_TERMS_CN = [
    "新华三",
    "华三",
    "华为",
    "联想",
    "深信服",
    "浪潮",
    "锐捷",
    "思科",
    "博科",
    "戴尔",
    "日立",
    "研华",
    "曙光",
    "中兴",
    "山石",
]

# ───────────── 英文品牌词（剥离并用于品牌识别）─────────────
BRAND_TERMS_EN = [
    "HEWLETT-PACKARD", "HEWLETT", "PACKARD",
    "HPE", "HP",
    "DELL", "EMC",
    "IBM",
    "H3C", "EWP",
    "HUAWEI",
    "LENOVO",
    "INSPUR",
    "CISCO",
    "NETAPP",
    "BROCADE",
    "HDS", "HITACHI",
    "FUJITSU",
    "F5",
    "MELLANOX",
    "EMERSON",
    "ORACLE",
    "NUTANIX",
    "VMWARE",
    "SANGFOR",
    "RUIJIE",
    "ADVANTECH",
    "SUGON",
    "ZTE",
]

# ───────────── 产品系列名（默认剥离，保留为弱信号）─────────────
SERIES_TERMS = [
    "POWEREDGE", "POWERVAULT", "POWERSTORE", "POWERMAX",
    "PROLIANT", "PROLIANTDL", "STORESERV", "PRIMERA",
    "THINKSYSTEM", "THINKSERVER", "THINKAGILE", "THINKSTATION", "THINKPAD",
    "ELITEBOOK", "ELITEDESK", "PRODESK", "OPTIPLEX", "LATITUDE", "PRECISION",
    "UNISERVER",
    "OCEANSTOR", "DORADO", "QUIDWAY", "FUSIONSERVER",
    "SECPATH", "UNISERVER",
    "VSP",
    "VPLEX",
    "POWERCONNECT",
]

# 系列名 → 品牌标准名（用于无显式品牌词时反推品牌作为弱信号）
SERIES_BRAND_MAP = {
    "POWEREDGE": "戴尔&易安信/DELL&EMC",
    "POWERVAULT": "戴尔&易安信/DELL&EMC",
    "POWERSTORE": "戴尔&易安信/DELL&EMC",
    "POWERMAX": "戴尔&易安信/DELL&EMC",
    "POWERCONNECT": "戴尔&易安信/DELL&EMC",
    "OPTIPLEX": "戴尔&易安信/DELL&EMC",
    "LATITUDE": "戴尔&易安信/DELL&EMC",
    "PRECISION": "戴尔&易安信/DELL&EMC",
    "VPLEX": "戴尔&易安信/DELL&EMC",
    "PROLIANT": "惠普&慧与/HP&HPE",
    "PROLIANTDL": "惠普&慧与/HP&HPE",
    "STORESERV": "惠普&慧与/HP&HPE",
    "PRIMERA": "惠普&慧与/HP&HPE",
    "ELITEBOOK": "惠普&慧与/HP&HPE",
    "ELITEDESK": "惠普&慧与/HP&HPE",
    "PRODESK": "惠普&慧与/HP&HPE",
    "THINKSYSTEM": "联想/Lenovo",
    "THINKSERVER": "联想/Lenovo",
    "THINKAGILE": "联想/Lenovo",
    "THINKSTATION": "联想/Lenovo",
    "THINKPAD": "联想/Lenovo",
    "OCEANSTOR": "华为/HUAWEI",
    "DORADO": "华为/HUAWEI",
    "QUIDWAY": "华为/HUAWEI",
    "FUSIONSERVER": "华为/HUAWEI",
    "SECPATH": "新华三/H3C",
    "UNISERVER": "新华三/H3C",
}

# ───────────── 配置参数 token（剥离，型号尾部的硬件配置描述）─────────────
# 这些词作为独立 token 出现时剥离，不会误伤型号核心。
CONFIG_TOKENS = {
    "INTEL", "XEON", "GOLD", "SILVER", "BRONZE", "PLATINUM", "CPU", "CORE",
    "GHZ", "GB", "TB", "MB", "HDD", "SSD", "SAS", "SATA", "NVME", "DDR3", "DDR4", "DDR5",
    "RAM", "MEM", "PORTS", "PORT",
    "DESKTOP", "MINI", "SFF", "MT", "TWR", "CTO", "WW", "TYPE",
    "AC", "DC", "PSU",
}

# ───────────── 编译期：长词优先排序 ─────────────
def _sorted(terms):
    return sorted(set(terms), key=len, reverse=True)

DEVICE_TYPE_TERMS = _sorted(DEVICE_TYPE_TERMS)
MODIFIER_TERMS = _sorted(MODIFIER_TERMS)
BRAND_TERMS_CN = _sorted(BRAND_TERMS_CN)
BRAND_TERMS_EN = _sorted(BRAND_TERMS_EN)
SERIES_TERMS = _sorted(SERIES_TERMS)
