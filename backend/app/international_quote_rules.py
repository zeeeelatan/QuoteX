from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Iterable, List


def select_param(key: str, label: str, default: str, options: Iterable[tuple[str, str]]) -> dict:
    return {
        "key": key,
        "label": label,
        "type": "select",
        "default": default,
        "options": [{"label": item_label, "value": value} for value, item_label in options],
    }


def number_param(key: str, label: str, default: float, suffix: str = "%") -> dict:
    return {"key": key, "label": label, "type": "number", "default": default, "suffix": suffix}


COUNTRY_DEFAULTS: List[dict] = [
    {"country_code": "france", "country_name": "法国", "default_city": "巴黎", "currency": "EUR", "currency_symbol": "€", "currency_precision": 2, "exchange_rate_cny": 7.757, "effective_label": "2026.1起·普通非干部员工", "employee_profile": "普通非干部员工", "parameter_config": []},
    {"country_code": "netherlands", "country_name": "荷兰", "default_city": "阿姆斯特丹", "currency": "EUR", "currency_symbol": "€", "currency_precision": 2, "exchange_rate_cny": 7.757, "effective_label": "2026.1起·永久合同雇员", "employee_profile": "永久合同雇员", "parameter_config": [select_param("contract_type", "合同类型", "permanent", (("permanent", "永久合同"), ("temporary", "临时合同"))), select_param("company_size", "企业规模", "small", (("small", "中小企业"), ("large", "大型企业")))]},
    {"country_code": "spain", "country_name": "西班牙", "default_city": "马德里", "currency": "EUR", "currency_symbol": "€", "currency_precision": 2, "exchange_rate_cny": 7.757, "effective_label": "2026.1起·普通永久合同雇员", "employee_profile": "普通永久合同雇员", "parameter_config": [select_param("contract_type", "合同类型", "permanent", (("permanent", "永久合同"), ("temporary", "临时合同")))]},
    {"country_code": "hungary", "country_name": "匈牙利", "default_city": "布达佩斯", "currency": "HUF", "currency_symbol": "Ft", "currency_precision": 0, "exchange_rate_cny": 0.0213, "effective_label": "2026.1起·普通雇员", "employee_profile": "普通雇员", "parameter_config": []},
    {"country_code": "turkey", "country_name": "土耳其", "default_city": "安卡拉", "currency": "TRY", "currency_symbol": "₺", "currency_precision": 0, "exchange_rate_cny": 0.1435, "effective_label": "2026.1起·普通雇员", "employee_profile": "普通雇员", "parameter_config": [select_param("on_time_discount", "按时缴费优惠", "no", (("no", "不使用"), ("yes", "使用5%优惠")))]},
    {"country_code": "uae", "country_name": "阿拉伯联合酋长国", "default_city": "阿布扎比", "currency": "AED", "currency_symbol": "AED", "currency_precision": 2, "exchange_rate_cny": 1.8422, "effective_label": "2026.1起·普通外籍雇员", "employee_profile": "普通外籍雇员", "parameter_config": [select_param("employee_type", "员工身份", "foreign", (("foreign", "外籍员工"), ("local_new", "本地/GCC新员工"), ("local_existing", "本地/GCC老员工")))]},
    {"country_code": "japan", "country_name": "日本", "default_city": "东京", "currency": "JPY", "currency_symbol": "¥", "currency_precision": 0, "exchange_rate_cny": 0.0416, "effective_label": "2026.4-2027.3·协会健保", "employee_profile": "协会健保普通员工", "parameter_config": [number_param("age", "员工年龄", 40, "岁")]},
    {"country_code": "vietnam", "country_name": "越南", "default_city": "河内", "currency": "VND", "currency_symbol": "₫", "currency_precision": 0, "exchange_rate_cny": 0.0003, "effective_label": "2026.7起·一类地区·正式员工", "employee_profile": "一类地区正式员工", "parameter_config": [select_param("employee_type", "员工身份", "local", (("local", "本地员工"), ("foreign", "外籍员工")))]},
    {"country_code": "thailand", "country_name": "泰国", "default_city": "曼谷", "currency": "THB", "currency_symbol": "฿", "currency_precision": 0, "exchange_rate_cny": 0.2008, "effective_label": "2026.1起·办公室低风险行业", "employee_profile": "办公室低风险行业员工", "parameter_config": [number_param("provident_rate", "雇主公积金比例", 0)]},
    {"country_code": "malaysia", "country_name": "马来西亚", "default_city": "吉隆坡", "currency": "MYR", "currency_symbol": "RM", "currency_precision": 2, "exchange_rate_cny": 1.6547, "effective_label": "2026年·60岁以下员工", "employee_profile": "60岁以下本地员工", "parameter_config": [select_param("employee_type", "员工身份", "local", (("local", "本地员工"), ("foreign", "外籍员工")))]},
    {"country_code": "singapore", "country_name": "新加坡", "default_city": "新加坡", "currency": "SGD", "currency_symbol": "S$", "currency_precision": 2, "exchange_rate_cny": 5.2388, "effective_label": "2026.1起·最新CPF费率", "employee_profile": "公民/第三年永久居民", "parameter_config": [number_param("age", "员工年龄", 30, "岁"), select_param("employee_type", "员工身份", "local", (("local", "公民/第三年PR"), ("foreign", "外籍工作准证")))]},
    {"country_code": "norway", "country_name": "挪威", "default_city": "奥斯陆", "currency": "NOK", "currency_symbol": "kr", "currency_precision": 0, "exchange_rate_cny": 0.702, "effective_label": "2026年·Zone I", "employee_profile": "奥斯陆Zone I普通员工", "parameter_config": [select_param("short_term_foreign", "短期外籍（183天内）", "no", (("no", "否"), ("yes", "是"))), number_param("regional_employer_rate", "地区雇主费率", 14.1)]},
    {"country_code": "finland", "country_name": "芬兰", "default_city": "赫尔辛基", "currency": "EUR", "currency_symbol": "€", "currency_precision": 2, "exchange_rate_cny": 7.7418, "effective_label": "2026年·全国统一", "employee_profile": "普通员工", "parameter_config": [select_param("short_term_foreign", "短期外籍/A1证书", "no", (("no", "否"), ("yes", "是")))]},
    {"country_code": "russia", "country_name": "俄罗斯", "default_city": "莫斯科", "currency": "RUB", "currency_symbol": "₽", "currency_precision": 0, "exchange_rate_cny": 0.0863, "effective_label": "2026年·个人零社保", "employee_profile": "办公室低风险普通员工", "parameter_config": [number_param("injury_rate", "行业工伤费率", 0.2)]},
    {"country_code": "germany", "country_name": "德国", "default_city": "柏林", "currency": "EUR", "currency_symbol": "€", "currency_precision": 2, "exchange_rate_cny": 7.7418, "effective_label": "2026年·法定公立保险", "employee_profile": "法定公立保险普通员工", "parameter_config": [select_param("childless_over_23", "23岁以上无子女", "no", (("no", "否"), ("yes", "是")))]},
    {"country_code": "switzerland", "country_name": "瑞士", "default_city": "苏黎世", "currency": "CHF", "currency_symbol": "CHF", "currency_precision": 2, "exchange_rate_cny": 8.329, "effective_label": "2026年·全国联邦统一", "employee_profile": "普通员工", "parameter_config": [select_param("age_band", "员工年龄档", "25-34", (("25-34", "25-34岁"), ("35-44", "35-44岁"), ("45-54", "45-54岁"), ("55-65", "55-65岁")))]},
]


COUNTRY_DEFAULT_MAP = {item["country_code"]: item for item in COUNTRY_DEFAULTS}


def _round(value: float, precision: int) -> float:
    quantizer = Decimal("1") if precision == 0 else Decimal("1").scaleb(-precision)
    return float(Decimal(str(value)).quantize(quantizer, rounding=ROUND_HALF_UP))


def _clamp(value: float, minimum: float = 0, maximum: float = 0) -> float:
    if value <= 0:
        return 0
    result = max(value, minimum)
    return min(result, maximum) if maximum > 0 else result


def _rule(name: str, base: float, rate: float, precision: int, basis: str, minimum: float = 0, maximum: float = 0) -> dict:
    return {
        "type": name,
        "min_base": minimum,
        "max_base": maximum,
        "corp_rate": rate,
        "indiv_rate": 0,
        "calc_base": base,
        "amount": _round(base * rate / 100, precision),
        "basis": basis,
    }


def _salary_rules(country_code: str, salary: float, params: Dict[str, Any], precision: int) -> List[dict]:
    s = max(float(salary or 0), 0)
    rules: List[dict] = []
    add = lambda name, base, rate, basis, minimum=0, maximum=0: rules.append(
        _rule(name, base, rate, precision, basis, minimum, maximum)
    )

    if country_code == "france":
        capped = _clamp(s, 0, 4005)
        for name, base, rate, basis, maximum in [
            ("医疗保险（疾病/生育/伤残）", s, 13, "全额工资", 0), ("基础养老保险（封顶）", capped, 8.55, "PMSS上限4005 EUR", 4005),
            ("基础养老保险（不封顶）", s, 2.11, "全额工资", 0), ("家庭补助金", s, 5.25, "全额工资", 0),
            ("失业保险", capped, 4, "PMSS上限4005 EUR", 4005), ("补充养老保险T1", capped, 4.72, "PMSS上限4005 EUR", 4005),
            ("CEG一般平衡缴费", capped, 1.29, "PMSS上限4005 EUR", 4005), ("工伤事故保险", s, 2, "办公室行业参考值", 0),
            ("AGS工资保障保险", capped, 0.2, "PMSS上限4005 EUR", 4005),
        ]: add(name, base, rate, basis, 0, maximum)
    elif country_code == "netherlands":
        contract_rate = 2.64 if params.get("contract_type", "permanent") == "permanent" else 7.74
        aof_rate = 6.27 if params.get("company_size", "small") == "small" else 7.63
        for name, base, rate, basis in [
            ("Zvw医疗保险（雇主）", _clamp(s, 0, 5968.67), 6.51, "月上限5968.67 EUR"),
            ("WW失业保险", _clamp(s, 0, 6617.42), contract_rate, "永久/临时合同分档"),
            ("Aof/WIA伤残保险", s, aof_rate, "企业规模分档"), ("Whk工伤/重返工作保险", s, 1, "行业平均"),
            ("儿童福利及其他缴费", s, 0.5, "全额工资"), ("职业补充养老金（雇主）", s, 12, "行业参考值"),
        ]: add(name, base, rate, basis)
    elif country_code == "spain":
        base = _clamp(s, 1424.4, 5101.2)
        unemployment = 5.5 if params.get("contract_type", "permanent") == "permanent" else 6.7
        for name, rate in [("一般社保", 23.6), ("失业保险", unemployment), ("职业培训缴费", 0.6), ("MEI代际公平养老缴费", 0.75), ("工伤保险/职业病", 1.5), ("FOGASA工资保障基金", 0.2)]:
            add(name, base, rate, "社保基数1424.4-5101.2 EUR", 1424.4, 5101.2)
    elif country_code == "hungary":
        base = _clamp(s, 322800, 1125000)
        add("社会贡献税SZOCHO", base, 13, "基数322800-1125000 HUF", 322800, 1125000)
    elif country_code == "turkey":
        base = _clamp(s, 33030, 297270)
        pension = 7 if params.get("on_time_discount", "no") == "yes" else 12
        for name, rate in [("养老/伤残/遗属保险", pension), ("一般医疗保险", 7.75), ("工伤/生育保险", 2), ("失业保险", 2)]:
            add(name, base, rate, "社保基数33030-297270 TRY", 33030, 297270)
    elif country_code == "uae":
        employee_type = params.get("employee_type", "foreign")
        pension_rate = 0 if employee_type == "foreign" else 15
        add("医疗保险（阿布扎比法定）", s, 4, "全额工资")
        add("离职酬金EOSG月度计提", s, 5.83, "每服务一年21天工资")
        add("养老金（本地/GCC员工）", _clamp(s, 0, 50000), pension_rate, "外籍0%，本地员工5万AED封顶", 0, 50000)
        add("行政及WPS费用", s, 0.5, "全额工资")
    elif country_code == "japan":
        age = float(params.get("age", 40) or 0)
        care_rate = 0.81 if 40 <= age <= 64 else 0
        for name, base, rate, basis in [
            ("厚生年金", _clamp(s, 0, 650000), 9.15, "月上限650000 JPY"), ("健康保险", s, 4.925, "全额工资"),
            ("介护保险", s, care_rate, "仅40-64岁"), ("雇佣保险", s, 0.85, "一般事业"),
            ("劳灾保险", s, 0.25, "办公室低风险"), ("儿童育儿支援金", s, 0.115, "全额工资"),
        ]: add(name, base, rate, basis)
    elif country_code == "vietnam":
        base = _clamp(s, 4960000, 50600000)
        local = params.get("employee_type", "local") == "local"
        for name, rate in [("社会保险", 17.5), ("健康保险", 3), ("失业保险", 1 if local else 0), ("工会经费", 2)]:
            add(name, base, rate, "一类地区基数4960000-50600000 VND", 4960000, 50600000)
    elif country_code == "thailand":
        base = _clamp(s, 1650, 17500)
        add("社会保障基金", base, 5, "基数1650-17500 THB", 1650, 17500)
        add("工伤保险WCS", base, 0.2, "办公室低风险", 1650, 17500)
        add("雇主公积金", s, float(params.get("provident_rate", 0) or 0), "自愿计划")
    elif country_code == "malaysia":
        local = params.get("employee_type", "local") == "local"
        epf_base = _clamp(s, 1500, 20000)
        socso_base = _clamp(s, 1500, 6000) if local else 0
        epf_rate = (13 if s <= 5000 else 12) if local else 2
        add("EPF公积金（雇主）", epf_base, epf_rate, "本地员工按工资分档，外籍2%", 1500, 20000)
        add("SOCSO社会保险（雇主）", socso_base, 1.75 if local else 0, "本地员工适用", 1500, 6000)
        add("EIS就业保险（雇主）", epf_base if local else 0, 0.2 if local else 0, "本地员工适用", 1500, 20000)
        add("HRD人力资源发展基金", epf_base, 1, "EPF/EIS基数", 1500, 20000)
    elif country_code == "singapore":
        age = float(params.get("age", 30) or 0)
        foreign = params.get("employee_type", "local") == "foreign"
        cpf_rate = 0 if foreign else (17 if age <= 55 else 16.5 if age <= 60 else 13.5 if age <= 65 else 9 if age <= 70 else 7.5)
        add("CPF中央公积金（雇主）", 0 if foreign else _clamp(s, 0, 8000), cpf_rate, "外籍工作准证免缴；本地按年龄分档", 0, 8000)
        add("SDL技能发展基金", _clamp(s, 0, 4500), 0.25, "月基数上限4500 SGD", 0, 4500)
        add("工伤保险WICA", s, 0.5, "办公室低风险")
    elif country_code == "norway":
        exempt = params.get("short_term_foreign", "no") == "yes" or s <= 69650 / 12
        base = 0 if exempt else s
        add("国民保险（雇主）", base, float(params.get("regional_employer_rate", 14.1) or 0), "地区费率；短期外籍免缴")
        add("强制职业养老金OTP", base, 2, "法定最低比例")
        add("工伤保险", s, 0.5, "办公室行业参考值")
    elif country_code == "finland":
        exempt = params.get("short_term_foreign", "no") == "yes" or s <= 71.72
        base = 0 if exempt else s
        for name, item_base, rate, basis in [
            ("TyEL职业养老金（雇主）", base, 17.1, "A1短期外籍免缴"), ("健康保险（雇主）", base, 1.91, "全国统一"),
            ("失业保险（雇主）", base, 0.31, "工资总额低档"), ("工伤保险", s, 0.5, "行业平均"), ("团体人寿保险", s, 0.07, "法定集体保险"),
        ]: add(name, item_base, rate, basis)
    elif country_code == "russia":
        capped = _clamp(s, 0, 248250)
        excess = max(s - 248250, 0)
        add("养老保险（基数内）", capped, 22, "月上限248250 RUB", 0, 248250)
        add("养老保险（超上限）", excess, 10, "超过上限部分")
        add("医疗保险", s, 5.1, "全额工资")
        add("失业/生育保险", capped, 2.9, "月上限248250 RUB", 0, 248250)
        add("工伤保险", s, float(params.get("injury_rate", 0.2) or 0), "行业风险费率")
    elif country_code == "germany":
        pension_base = _clamp(s, 0, 8450)
        medical_base = _clamp(s, 0, 5812.5)
        for name, base, rate, basis in [
            ("养老保险", pension_base, 9.3, "月上限8450 EUR"), ("医疗保险", medical_base, 8.75, "月上限5812.5 EUR"),
            ("失业保险", pension_base, 1.3, "月上限8450 EUR"), ("护理保险", medical_base, 1.8, "月上限5812.5 EUR"),
            ("工伤保险", s, 1.3, "行业参考值"), ("U1/U2破产/生育统筹", s, 1.5, "全额工资"),
        ]: add(name, base, rate, basis)
    elif country_code == "switzerland":
        capped = _clamp(s, 0, 12350)
        excess = max(s - 12350, 0)
        coordinated = max(min(s, 7560) - 2205, 0)
        bvg_rates = {"25-34": 7, "35-44": 10, "45-54": 15, "55-65": 18}
        add("AHV/IV/EO", s, 5.3, "全额工资")
        add("ALV失业保险（基数内）", capped, 1.1, "月上限12350 CHF", 0, 12350)
        add("ALV团结附加（超上限）", excess, 0.5, "超过上限部分")
        add("BVG职业养老金（雇主）", coordinated, bvg_rates.get(params.get("age_band", "25-34"), 7), "协调工资按年龄分档")
        add("职业工伤保险BU", s, 0.3, "办公室行业参考值")
        add("家庭补贴基金FAK", s, 0.5, "州级参考值")
    else:
        raise ValueError("不支持的国家报价规则")
    return rules


def calculate_employer_rules(country_code: str, salary: float, params: Dict[str, Any]) -> dict:
    config = COUNTRY_DEFAULT_MAP.get(country_code)
    if config is None:
        raise ValueError("不支持的国家报价规则")
    precision = config["currency_precision"]
    rules = _salary_rules(country_code, salary, params, precision)
    return {
        "country_code": country_code,
        "currency": config["currency"],
        "currency_precision": precision,
        "employer_rules": rules,
        "employer_total": _round(sum(item["amount"] for item in rules), precision),
    }


def country_seed_rows() -> List[dict]:
    common = {
        "exchange_rate_date": date(2026, 7, 1),
        "eor_rate": 12,
        "management_rate": 12,
        "profit_rate": 8,
        "vat_rate": 6,
        "local_vat_rate": 0,
        "local_vat_enabled": False,
        "is_active": True,
    }
    return [{**common, **item} for item in COUNTRY_DEFAULTS]
