#!/usr/bin/env python3
# 功能：公告文本结构化提取。用正则定位净利润、同比增速、上年同期、公告类型与公告日期。
# 规则解析在该场景准确率高于 LLM 抽取且零成本；LLM 接口位预留在 parse_with_llm。

from __future__ import annotations

import re
from typing import Any

from langchain_core.tools import tool

# 金额单位换算到「元」
UNIT_SCALE: dict[str, float] = {
    "元": 1.0,
    "万元": 1e4,
    "百万元": 1e6,
    "亿元": 1e8,
}

ANNOUNCEMENT_TYPES: tuple[str, ...] = ("业绩预告", "业绩快报", "定期报告")

_NUM = r"(-?[\d,]+(?:\.\d+)?)"
_UNIT = r"(元|万元|百万元|亿元)"

RE_NET_PROFIT = re.compile(rf"归属于上市公司股东的净利润[：:\s]*{_NUM}\s*{_UNIT}")
RE_PREV_PROFIT = re.compile(rf"上年同期[：:\s]*{_NUM}\s*{_UNIT}")
RE_YOY = re.compile(r"同比(?:增长|变动|下降)?[：:\s]*(-?[\d.]+)\s*%")
RE_DATE = re.compile(r"公告日期[：:\s]*(\d{4}-\d{2}-\d{2})")
RE_TYPE = re.compile(r"公告类型[：:\s]*(\S+)")


def _to_yuan(raw: str, unit: str) -> float:
    """把带单位的金额字符串归一到元。"""
    return float(raw.replace(",", "")) * UNIT_SCALE[unit]


def parse_announcement_text(text: str) -> dict[str, Any]:
    """从公告原文抽取结构化字段。

    缺失字段一律返回 None（下游统一写 NA），绝不填 0。
    早期版本把缺失写成 0，导致下游把「未披露」和「亏损」混为一类。
    """
    result: dict[str, Any] = {
        "ann_type": None,
        "ann_date": None,
        "net_profit": None,
        "prev_profit": None,
        "yoy_pct": None,
        "unit_raw": None,
    }

    if m := RE_TYPE.search(text):
        result["ann_type"] = m.group(1)

    if m := RE_DATE.search(text):
        result["ann_date"] = m.group(1)

    if m := RE_NET_PROFIT.search(text):
        result["net_profit"] = _to_yuan(m.group(1), m.group(2))
        result["unit_raw"] = m.group(2)

    if m := RE_PREV_PROFIT.search(text):
        result["prev_profit"] = _to_yuan(m.group(1), m.group(2))

    if m := RE_YOY.search(text):
        result["yoy_pct"] = float(m.group(1))

    return result


def parse_with_llm(text: str) -> dict[str, Any]:  # pragma: no cover - 接口位
    """LLM 抽取接口位，便于与规则解析做准确率对比。当前未启用。"""
    raise NotImplementedError("LLM 抽取尚未启用，当前使用规则解析")


@tool
def parse_announcement(text: str) -> dict[str, Any]:
    """把公告原文解析成结构化字段。

    Args:
        text: 公告纯文本

    Returns:
        含 ann_type / ann_date / net_profit / prev_profit / yoy_pct 的字典，
        缺失字段为 None。
    """
    return parse_announcement_text(text)
