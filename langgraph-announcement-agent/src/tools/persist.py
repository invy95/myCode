#!/usr/bin/env python3
# 功能：把校验后的公告数据落盘为 CSV，并追加运行 trace 到日志。
# 缺失字段统一写 NA；校验失败的记录也会落盘（标记 NA + 违规原因），不静默丢数据。

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "out"
RUN_LOG = OUT_DIR / "run.log"

FIELDNAMES = [
    "code",
    "period",
    "ann_type",
    "ann_date",
    "net_profit",
    "prev_profit",
    "yoy_pct",
    "source",
    "valid",
    "violations",
    "warnings",
]

NA = "NA"


def _cell(value: Any) -> str:
    """空值统一写 NA，避免下游把缺失当作 0 处理。"""
    return NA if value is None else str(value)


def write_row(row: dict[str, Any], out_dir: Path | None = None) -> Path:
    """把单条记录写成 CSV 文件，返回输出路径。"""
    out_dir = out_dir or OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{row['code']}_{row['period']}.csv"

    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow({key: _cell(row.get(key)) for key in FIELDNAMES})

    return path


def append_trace(trace: list[dict[str, Any]], log_path: Path | None = None) -> None:
    """把本次运行的完整 trace 追加到日志，供事后复盘。"""
    log_path = log_path or RUN_LOG
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(trace, ensure_ascii=False) + "\n")


@tool
def persist_announcement(row: dict[str, Any]) -> str:
    """把公告记录落盘为 CSV。

    Args:
        row: 含 code / period / 解析字段 / 校验结果的扁平字典

    Returns:
        输出文件路径字符串。
    """
    return str(write_row(row))
