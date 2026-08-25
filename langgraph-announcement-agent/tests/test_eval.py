#!/usr/bin/env python3
# 功能：回归评测集。5 条用例覆盖正常路径与四类异常路径，全部基于离线 fixture，无需网络。
# 每条用例对应生产环境中真实出现过的情况，不是为了凑覆盖率造的假场景。

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.graph import build_graph  # noqa: E402
from src.state import init_state  # noqa: E402
from src.tools import validate_parsed  # noqa: E402


@pytest.fixture
def graph():
    return build_graph()


def run(graph, code: str, period: str = "2026Q2") -> dict:
    return graph.invoke(init_state(code, period))


def test_normal_forecast(graph):
    """正常业绩预告：6 条断言全过，字段完整落盘。"""
    final = run(graph, "002594")

    assert final["valid"] is True
    assert final["violations"] == []
    assert final["source"] == "cninfo"

    parsed = final["parsed"]
    assert parsed["ann_type"] == "业绩预告"
    assert parsed["ann_date"] == "2026-07-14"
    assert parsed["net_profit"] == pytest.approx(5_224_000_000)
    assert parsed["yoy_pct"] == pytest.approx(12.30)

    assert Path(final["output_path"]).exists()


def test_unit_conversion(graph):
    """金额单位为「万元」：必须归一到元，不能原样落盘。"""
    final = run(graph, "600519")

    assert final["valid"] is True
    parsed = final["parsed"]
    # 418,600 万元 = 4,186,000,000 元
    assert parsed["net_profit"] == pytest.approx(4_186_000_000)
    assert parsed["prev_profit"] == pytest.approx(3_723_000_000)
    assert parsed["unit_raw"] == "万元"


def test_missing_field_writes_na(graph):
    """同比与上年同期缺失：必须是 None（落盘写 NA），绝不能填 0。"""
    final = run(graph, "000001")

    assert final["valid"] is True
    parsed = final["parsed"]
    assert parsed["net_profit"] == pytest.approx(28_900_000_000)
    assert parsed["prev_profit"] is None
    assert parsed["yoy_pct"] is None

    content = Path(final["output_path"]).read_text(encoding="utf-8-sig")
    assert "NA" in content
    # 缺失被误写成 0 是早期真实踩过的坑，这里锁死
    assert ",0," not in content


def test_fallback_source(graph):
    """主源无此公告：自动降级到兜底源并成功。"""
    final = run(graph, "300750")

    assert final["valid"] is True
    assert final["source"] == "eastmoney"

    fetch_traces = [t for t in final["trace"] if t["node"] == "fetch_pdf"]
    # 主源失败一次，兜底源成功一次
    assert fetch_traces[0]["ok"] is False
    assert fetch_traces[0]["source"] == "cninfo"
    assert fetch_traces[-1]["ok"] is True


def test_retry_on_invalid_then_success(graph):
    """主源数据不合规（类型非法 + 日期未来）：换源重试后拿到合规版本。"""
    final = run(graph, "688981")

    assert final["valid"] is True
    assert final["source"] == "eastmoney"
    assert final["retries"] >= 1

    validate_traces = [t for t in final["trace"] if t["node"] == "validate"]
    assert validate_traces[0]["ok"] is False
    assert validate_traces[-1]["ok"] is True


def test_retry_exhausted_writes_na(graph):
    """所有源都没有：重试耗尽后落盘 NA 记录，不抛异常中断批量任务。"""
    final = run(graph, "999999")

    assert final["valid"] is False
    assert final["violations"]
    assert final["parsed"] == {}

    content = Path(final["output_path"]).read_text(encoding="utf-8-sig")
    assert "NA" in content


def test_yoy_inconsistency_warns_not_blocks():
    """同比与两期净利润不自洽：仅告警，不阻断落盘。"""
    parsed = {
        "ann_type": "业绩预告",
        "ann_date": "2026-07-14",
        "net_profit": 1_200_000_000.0,
        "prev_profit": 1_000_000_000.0,
        "yoy_pct": 5.0,  # 实际应约 20%
        "unit_raw": "元",
    }
    violations, warnings = validate_parsed(parsed, today=date(2026, 8, 25))

    assert violations == []
    assert any("同比不自洽" in w for w in warnings)
