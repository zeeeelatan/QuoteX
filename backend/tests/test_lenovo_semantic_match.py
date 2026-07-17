"""联想框架匹配：语义候选串抽取测试"""
from app.routers.lenovo_framework import (
    _build_lenovo_model_candidates,
    _normalize_model_py,
)
from app.semantic import extract_fields


class TestLenovoSemanticCandidates:
    def test_poweredge_core_extracted(self):
        candidates, brand = _build_lenovo_model_candidates(
            db=None,
            model="PowerEdge C4140",
            brand="DELL",
            alias_key="dell-DELL PowerEdge C4140",
        )
        assert "PowerEdge C4140" in candidates
        # 语义核心串应抽出短型号，供联想机型库精确命中
        assert any(_normalize_model_py(c) == "c4140" for c in candidates)

    def test_alias_key_helps_when_model_noisy(self):
        candidates, _ = _build_lenovo_model_candidates(
            db=None,
            model="dell-DELL PowerEdge R740",
            brand="戴尔&易安信/DELL&EMC",
            alias_key="dell-DELL PowerEdge R740",
        )
        norms = {_normalize_model_py(c) for c in candidates}
        assert "r740" in norms or any("r740" in n for n in norms)

    def test_fallback_keeps_raw_model_when_semantic_off(self, monkeypatch):
        monkeypatch.setenv("ENABLE_SEMANTIC_MATCH", "0")
        # is_semantic_enabled 读取环境变量，无 lru 缓存问题
        candidates, _ = _build_lenovo_model_candidates(
            db=None,
            model="PowerEdge C4140",
            brand="DELL",
        )
        assert candidates == ["PowerEdge C4140"]
        monkeypatch.delenv("ENABLE_SEMANTIC_MATCH", raising=False)

    def test_extract_fields_poweredge(self):
        fields = extract_fields("DELL PowerEdge C4140", "DELL", db=None)
        assert fields.core
        assert "C4140" in fields.core.upper().replace(" ", "")
