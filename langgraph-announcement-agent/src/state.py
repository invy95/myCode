#!/usr/bin/env python3
# 功能：定义公告解析 Agent 的图状态（AgentState）与 trace 记录结构。
# 状态在节点间显式传递，不使用全局变量，便于 checkpoint 断点续跑与事后回放。

from __future__ import annotations

from typing import Any, Literal, TypedDict

# 采集源按优先级排列：主源失败后依次降级
SOURCE_ORDER: tuple[str, ...] = ("cninfo", "eastmoney", "cache")

NodeName = Literal["fetch_pdf", "parse_table", "validate", "persist"]


class TraceEntry(TypedDict):
    """单个节点的执行记录，用于可观测与事后复盘。"""

    node: str
    source: str
    ok: bool
    detail: str
    elapsed_ms: float


class AgentState(TypedDict, total=False):
    """公告解析流程的完整状态。

    输入字段由调用方提供；其余字段由各节点逐步填充。
    """

    # --- 输入 ---
    code: str
    period: str

    # --- fetch_pdf 产出 ---
    source_idx: int
    source: str
    raw_text: str
    fetch_ok: bool

    # --- parse_table 产出 ---
    parsed: dict[str, Any]

    # --- validate 产出 ---
    violations: list[str]
    warnings: list[str]
    valid: bool

    # --- 重试控制 ---
    retries: int
    max_retries: int

    # --- persist 产出 ---
    output_path: str

    # --- 全程累积 ---
    trace: list[TraceEntry]


def init_state(code: str, period: str, max_retries: int = 2) -> AgentState:
    """构造初始状态。max_retries 指换源重试次数上限。"""
    return AgentState(
        code=code,
        period=period,
        source_idx=0,
        retries=0,
        max_retries=max_retries,
        parsed={},
        violations=[],
        warnings=[],
        valid=False,
        trace=[],
    )
