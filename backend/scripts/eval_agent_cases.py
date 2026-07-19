#!/usr/bin/env python3
"""离线评测专用智能体用例清单（不调用大模型，仅校验工具可执行性）。

用法（在 backend 目录）:
  python -m scripts.eval_agent_cases
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.agent.prompts import QUOTE_TYPE_CATALOG, SYSTEM_PROMPT
from app.agent.tools import tool_schemas, try_extract_bom_from_requirement


def main() -> int:
    cases_path = ROOT / "app" / "agent" / "eval_cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    tools = {t["function"]["name"] for t in tool_schemas()}
    print(f"工具数: {len(tools)}")
    print(f"报价类型目录: {len(QUOTE_TYPE_CATALOG)}")
    print(f"系统提示词长度: {len(SYSTEM_PROMPT)}")
    print(f"评测用例: {len(cases)}")

    missing = []
    for c in cases:
        for name in c.get("expect_tools") or []:
            if name not in tools:
                missing.append((c["id"], name))

    # 抽样自然语言提取
    sample = try_extract_bom_from_requirement("10台华为 2288H V5")
    print(f"NL BOM 抽样提取: {sample}")

    if missing:
        print("缺失工具映射:")
        for cid, name in missing:
            print(f"  - {cid}: {name}")
        return 1

    print("评测清单校验通过（工具名齐全）。完整效果需结合线上对话人工抽检。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
