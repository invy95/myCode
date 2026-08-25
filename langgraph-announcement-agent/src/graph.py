#!/usr/bin/env python3
# 功能：LangGraph 主图。4 个节点 + 1 条条件边，实现「采集→解析→校验→(重试)→落盘」闭环。
# 校验失败时通过条件边退回 fetch_pdf 换源重试；重试耗尽则标记 NA 落盘，不抛异常中断批量任务。

from __future__ import annotations

import time
from typing import Any, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .state import SOURCE_ORDER, AgentState, TraceEntry
from .tools import (
    SourceUnavailable,
    append_trace,
    fetch_from_source,
    parse_announcement_text,
    validate_parsed,
    write_row,
)


def _trace(node: str, source: str, ok: bool, detail: str, started: float) -> TraceEntry:
    return TraceEntry(
        node=node,
        source=source,
        ok=ok,
        detail=detail,
        elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
    )


def fetch_pdf(state: AgentState) -> dict[str, Any]:
    """按当前优先级取公告原文；该源不可用时自动前进到下一个源。"""
    started = time.perf_counter()
    idx = state.get("source_idx", 0)
    trace = list(state.get("trace", []))

    while idx < len(SOURCE_ORDER):
        source = SOURCE_ORDER[idx]
        try:
            text = fetch_from_source(source, state["code"], state["period"])
        except SourceUnavailable as exc:
            trace.append(_trace("fetch_pdf", source, False, str(exc), started))
            idx += 1
            continue

        trace.append(
            _trace("fetch_pdf", source, True, f"{len(text)} chars", started)
        )
        return {
            "raw_text": text,
            "source": source,
            "source_idx": idx,
            "fetch_ok": True,
            "trace": trace,
        }

    return {
        "raw_text": "",
        "source": "none",
        "source_idx": idx,
        "fetch_ok": False,
        "trace": trace,
    }


def parse_table(state: AgentState) -> dict[str, Any]:
    """把公告原文抽成结构化字段。采集失败时直接透传空结果。"""
    started = time.perf_counter()
    trace = list(state.get("trace", []))
    source = state.get("source", "none")

    if not state.get("fetch_ok"):
        trace.append(_trace("parse_table", source, False, "无原文可解析", started))
        return {"parsed": {}, "trace": trace}

    parsed = parse_announcement_text(state["raw_text"])
    filled = sum(1 for value in parsed.values() if value is not None)
    trace.append(
        _trace("parse_table", source, True, f"{filled}/{len(parsed)} 字段命中", started)
    )
    return {"parsed": parsed, "trace": trace}


def validate(state: AgentState) -> dict[str, Any]:
    """跑 6 条断言。violations 非空表示该源数据不可用。"""
    started = time.perf_counter()
    trace = list(state.get("trace", []))
    source = state.get("source", "none")

    violations, warnings = validate_parsed(state.get("parsed", {}))
    valid = not violations
    detail = "全部通过" if valid else "; ".join(violations)
    trace.append(_trace("validate", source, valid, detail, started))

    return {
        "violations": violations,
        "warnings": warnings,
        "valid": valid,
        "trace": trace,
    }


def route_after_validate(state: AgentState) -> Literal["retry", "persist"]:
    """校验失败且仍有重试额度与备用源时换源重试，否则进入落盘。"""
    if state.get("valid"):
        return "persist"

    has_retry_budget = state.get("retries", 0) < state.get("max_retries", 2)
    has_next_source = state.get("source_idx", 0) + 1 < len(SOURCE_ORDER)
    return "retry" if has_retry_budget and has_next_source else "persist"


def bump_retry(state: AgentState) -> dict[str, Any]:
    """推进到下一个数据源并累加重试计数。"""
    return {
        "retries": state.get("retries", 0) + 1,
        "source_idx": state.get("source_idx", 0) + 1,
    }


def persist(state: AgentState) -> dict[str, Any]:
    """落盘 CSV 并写运行日志。校验未通过的记录同样落盘，字段标 NA。"""
    started = time.perf_counter()
    trace = list(state.get("trace", []))
    parsed = state.get("parsed", {})

    row = {
        "code": state["code"],
        "period": state["period"],
        "ann_type": parsed.get("ann_type"),
        "ann_date": parsed.get("ann_date"),
        "net_profit": parsed.get("net_profit"),
        "prev_profit": parsed.get("prev_profit"),
        "yoy_pct": parsed.get("yoy_pct"),
        "source": state.get("source", "none"),
        "valid": state.get("valid", False),
        "violations": "; ".join(state.get("violations", [])) or None,
        "warnings": "; ".join(state.get("warnings", [])) or None,
    }

    path = write_row(row)
    trace.append(_trace("persist", row["source"], True, str(path.name), started))
    append_trace(trace)

    return {"output_path": str(path), "trace": trace}


def build_graph(checkpointer: MemorySaver | None = None):
    """组装并编译主图。传入 checkpointer 可启用断点续跑。"""
    builder = StateGraph(AgentState)

    builder.add_node("fetch_pdf", fetch_pdf)
    builder.add_node("parse_table", parse_table)
    builder.add_node("validate", validate)
    builder.add_node("bump_retry", bump_retry)
    builder.add_node("persist", persist)

    builder.add_edge(START, "fetch_pdf")
    builder.add_edge("fetch_pdf", "parse_table")
    builder.add_edge("parse_table", "validate")
    builder.add_conditional_edges(
        "validate",
        route_after_validate,
        {"retry": "bump_retry", "persist": "persist"},
    )
    builder.add_edge("bump_retry", "fetch_pdf")
    builder.add_edge("persist", END)

    return builder.compile(checkpointer=checkpointer)
