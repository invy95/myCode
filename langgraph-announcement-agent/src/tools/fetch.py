#!/usr/bin/env python3
# 功能：公告文本多源采集工具。按 巨潮(cninfo) → 东财(eastmoney) → 本地缓存(cache) 三级降级。
# 离线模式下从 data/fixtures 读取脱敏样本，无需网络与凭据即可跑通全流程。

from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures"


class SourceUnavailable(Exception):
    """该数据源无此公告，调用方应降级到下一个源。"""


def _fixture_path(source: str, code: str, period: str) -> Path:
    return FIXTURE_DIR / source / f"{code}_{period}.txt"


def fetch_from_source(source: str, code: str, period: str) -> str:
    """从指定源取公告原文。

    离线实现：读取 fixture 文件。接入真实数据源时，替换本函数内部即可，
    上层图结构与降级逻辑无需改动。
    """
    path = _fixture_path(source, code, period)
    if not path.exists():
        raise SourceUnavailable(f"{source} 无 {code} {period} 公告")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SourceUnavailable(f"{source} 返回空内容")
    return text


@tool
def fetch_announcement(source: str, code: str, period: str) -> str:
    """按指定数据源抓取上市公司公告原文。

    Args:
        source: 数据源标识，取值 cninfo / eastmoney / cache
        code: 6 位股票代码
        period: 报告期，如 2026Q2

    Returns:
        公告纯文本；该源无数据时抛出 SourceUnavailable。
    """
    return fetch_from_source(source, code, period)
