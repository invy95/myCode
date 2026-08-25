#!/usr/bin/env python3
# 功能：CLI 入口。跑单支股票的公告解析流程并打印每个节点的 trace。
# 用法：python -m src.run --code 002594 --period 2026Q2

from __future__ import annotations

import argparse

from langgraph.checkpoint.memory import MemorySaver

from .graph import build_graph
from .state import init_state

NODE_WIDTH = 11


def format_trace_line(entry: dict) -> str:
    mark = "ok" if entry["ok"] else "fail"
    return (
        f"[{entry['node']:<{NODE_WIDTH}}] "
        f"source={entry['source']:<10} {mark:<4} "
        f"{entry['elapsed_ms']:>7.2f}ms  {entry['detail']}"
    )


def run_once(code: str, period: str, thread_id: str | None = None) -> dict:
    """跑一次完整流程，返回终态。thread_id 相同则复用 checkpoint。"""
    graph = build_graph(checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": thread_id or f"{code}-{period}"}}
    return graph.invoke(init_state(code, period), config=config)


def main() -> None:
    parser = argparse.ArgumentParser(description="投研公告解析 Agent (LangGraph)")
    parser.add_argument("--code", required=True, help="6 位股票代码")
    parser.add_argument("--period", required=True, help="报告期，如 2026Q2")
    args = parser.parse_args()

    final = run_once(args.code, args.period)

    for entry in final.get("trace", []):
        print(format_trace_line(entry))

    parsed = final.get("parsed", {})
    print()
    print(f"公告类型: {parsed.get('ann_type') or 'NA'}")
    print(f"公告日期: {parsed.get('ann_date') or 'NA'}")
    print(f"净利润  : {parsed.get('net_profit') or 'NA'}")
    print(f"同比    : {parsed.get('yoy_pct') or 'NA'}%")
    print(f"校验    : {'通过' if final.get('valid') else '未通过'}")

    if violations := final.get("violations"):
        print(f"违规    : {'; '.join(violations)}")
    if warnings := final.get("warnings"):
        print(f"告警    : {'; '.join(warnings)}")

    print(f"输出    : {final.get('output_path')}")


if __name__ == "__main__":
    main()
