"""设备匹配算法核心测试"""
import pytest
from app.matching import (
    normalize_manufacturer,
    normalize_model,
    similarity_ratio,
    model_similarity_score,
    calculate_maintenance_price,
    get_maintenance_rate_for_category,
    match_device,
    extract_model_prefix,
    extract_version,
    longest_common_substring,
)


# ──────────────────────────────────────────────
# normalize_manufacturer 品牌标准化
# ──────────────────────────────────────────────
class TestNormalizeManufacturer:
    def test_hp_to_standard(self):
        assert normalize_manufacturer("hp") == "惠普&慧与/HP&HPE"

    def test_hpe_to_standard(self):
        assert normalize_manufacturer("hpe") == "惠普&慧与/HP&HPE"

    def test_dell_to_standard(self):
        assert normalize_manufacturer("dell") == "戴尔/DELL"

    def test_huawei_to_standard(self):
        assert normalize_manufacturer("huawei") == "华为/HUAWEI"

    def test_h3c_to_standard(self):
        assert normalize_manufacturer("h3c") == "新华三/H3C"

    def test_unknown_passthrough(self):
        """未知品牌应原样返回（小写）"""
        result = normalize_manufacturer("SomeUnknownBrand")
        assert result == "someunknownbrand"


# ──────────────────────────────────────────────
# normalize_model 型号标准化
# ──────────────────────────────────────────────
class TestNormalizeModel:
    def test_uppercase(self):
        assert normalize_model("PowerEdge R740") == "POWEREDGE R740"

    def test_strip_whitespace(self):
        assert normalize_model("  DL380  Gen10  ") == "DL380 GEN10"

    def test_remove_special_chars(self):
        """保留 - _ / ，移除其他特殊字符"""
        result = normalize_model("Model@#123-A/B_C")
        assert result == "MODEL123-A/B_C"


# ──────────────────────────────────────────────
# similarity_ratio 相似度计算
# ──────────────────────────────────────────────
class TestSimilarityRatio:
    def test_identical(self):
        assert similarity_ratio("R740", "R740") == 100.0

    def test_empty_string(self):
        assert similarity_ratio("", "R740") == 0.0

    def test_case_insensitive(self):
        assert similarity_ratio("r740", "R740") == 100.0

    def test_partial_similar(self):
        score = similarity_ratio("R740", "R750")
        assert 50 < score < 100


# ──────────────────────────────────────────────
# extract_model_prefix / extract_version
# ──────────────────────────────────────────────
class TestModelParsing:
    def test_prefix_with_dash(self):
        assert extract_model_prefix("AF-2000") == "AF"

    def test_prefix_poweredge(self):
        assert extract_model_prefix("POWEREDGE R740") == "POWEREDGE"

    def test_version_extraction(self):
        assert extract_version("AF-2000 V8.0") == "V8.0"

    def test_version_none(self):
        assert extract_version("PowerEdge R740") == ""


# ──────────────────────────────────────────────
# longest_common_substring
# ──────────────────────────────────────────────
class TestLCS:
    def test_identical(self):
        assert longest_common_substring("R740", "R740") == 4

    def test_partial(self):
        assert longest_common_substring("R740", "R750") == 2  # "R7"

    def test_empty(self):
        assert longest_common_substring("", "R740") == 0


# ──────────────────────────────────────────────
# model_similarity_score 综合相似度
# ──────────────────────────────────────────────
class TestModelSimilarityScore:
    def test_identical_model(self):
        score = model_similarity_score("POWEREDGE R740", "POWEREDGE R740")
        assert score > 90

    def test_similar_model(self):
        score = model_similarity_score("POWEREDGE R740", "POWEREDGE R750")
        assert score > 60

    def test_different_model(self):
        score = model_similarity_score("POWEREDGE R740", "CE6881-48S6CQ")
        assert score < 40

    def test_empty_input(self):
        assert model_similarity_score("", "R740") == 0.0

    def test_manufacturer_bonus(self):
        """相同厂商应获得额外加分"""
        score_with_mfr = model_similarity_score("R740", "R750", "DELL", "DELL")
        score_without_mfr = model_similarity_score("R740", "R750", "", "")
        assert score_with_mfr >= score_without_mfr


# ──────────────────────────────────────────────
# calculate_maintenance_price 维保价格计算
# ──────────────────────────────────────────────
class TestCalculateMaintenancePrice:
    def test_normal_calculation(self):
        """45000 * 0.08 * 1.06 = 3816.0"""
        price = calculate_maintenance_price(45000, 0.08)
        assert abs(price - 3816.0) < 0.01

    def test_zero_price(self):
        assert calculate_maintenance_price(0, 0.08) == 0.0

    def test_none_price(self):
        assert calculate_maintenance_price(None, 0.08) == 0.0

    def test_default_rate(self):
        """使用默认费率 0.02：45000 * 0.02 * 1.06 = 954.0"""
        price = calculate_maintenance_price(45000, 0.02)
        assert abs(price - 954.0) < 0.01


# ──────────────────────────────────────────────
# get_maintenance_rate_for_category 费率查找（需要数据库）
# ──────────────────────────────────────────────
class TestGetMaintenanceRate:
    def test_exact_three_level_match(self, db, seed_devices):
        rate = get_maintenance_rate_for_category(
            db, "服务器", "机架式服务器", "标准机架式"
        )
        assert rate == 0.08

    def test_fallback_to_default(self, db, seed_devices):
        """找不到匹配分类时返回默认费率 0.02"""
        rate = get_maintenance_rate_for_category(
            db, "不存在的分类", "不存在", "不存在"
        )
        assert rate == 0.02

    def test_none_categories(self, db, seed_devices):
        rate = get_maintenance_rate_for_category(db, None, None, None)
        assert rate == 0.02


# ──────────────────────────────────────────────
# match_device 完整匹配流程（需要数据库）
# ──────────────────────────────────────────────
class TestMatchDevice:
    def test_exact_match(self, db, seed_devices):
        """精确匹配 Dell PowerEdge R740"""
        result = match_device(db, "dell", "PowerEdge R740", source="datacenter")
        assert result["matched_model"] == "PowerEdge R740"
        assert result["match_rate"] == 100.0
        assert result["device_price"] == 45000
        assert result["rate"] == 0.08
        assert result["price"] > 0

    def test_prefix_match(self, db, seed_devices):
        """前缀匹配"""
        result = match_device(db, "dell", "PowerEdge R74", source="datacenter")
        assert result["matched_model"] is not None
        assert result["match_rate"] >= 90.0

    def test_fuzzy_match(self, db, seed_devices):
        """模糊匹配"""
        result = match_device(db, "dell", "PowerEdge R741", source="datacenter")
        assert result["matched_model"] is not None
        assert result["match_rate"] > 50

    def test_no_match_empty_model(self, db, seed_devices):
        """空型号应返回空结果"""
        result = match_device(db, "dell", "", source="datacenter")
        assert result["matched_model"] is None
        assert result["match_rate"] == 0.0

    def test_no_match_unrelated(self, db, seed_devices):
        """完全不相关的型号"""
        result = match_device(db, "unknown", "ZZZZXXX-9999", source="datacenter")
        # 可能匹配分数过低返回 None，也可能找到一个低分匹配
        if result["matched_model"] is not None:
            assert result["match_rate"] < 70

    def test_huawei_switch_match(self, db, seed_devices):
        """华为交换机精确匹配"""
        result = match_device(db, "huawei", "CE6881-48S6CQ", source="datacenter")
        assert result["matched_model"] == "CE6881-48S6CQ"
        assert result["match_rate"] == 100.0
        assert result["rate"] == 0.05

    def test_hp_manufacturer_normalization(self, db, seed_devices):
        """HP 品牌标准化后匹配"""
        result = match_device(db, "hp", "ProLiant DL380 Gen10", source="datacenter")
        assert result["matched_model"] == "ProLiant DL380 Gen10"
        assert result["match_rate"] == 100.0
