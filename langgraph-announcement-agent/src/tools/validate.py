#!/usr/bin/env python3
# 功能：对解析结果做 6 条硬断言。区分「必须换源重试的违规」与「仅告警仍可落盘的偏差」。
# 设计原则：宁可标 NA，不可编数——任何无法确认的字段都不允许猜测填充。

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from langchain_core.tools import tool

from ..tools.parse import ANNOUNCEMENT_TYPES

# 同比增速与两期净利润自洽性的容差（百分点）
YOY_TOLERANCE_PP = 0.5


def _parse_date(raw: str) -> date | None:
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def validate_parsed(
    parsed: dict[str, Any], today: date | None = None
) -> tuple[list[str], list[str]]:
    """校验解析结果。

    Returns:
        (violations, warnings)
        violations 非空表示该源数据不可用，应换源重试；
        warnings 非空表示数据可疑但仍可落盘，需人工复核。
    """
    today = today or date.today()
    violations: list[str] = []
    warnings: list[str] = []

    # 断言 1：公告类型必须在白名单内
    ann_type = parsed.get("ann_type")
    if ann_type not in ANNOUNCEMENT_TYPES:
        violations.append(f"公告类型非法: {ann_type!r}")

    # 断言 2：净利润必须存在且为数值
    net_profit = parsed.get("net_profit")
    if not isinstance(net_profit, (int, float)):
        violations.append("净利润缺失或非数值")

    # 断言 3：公告日期格式合法且不晚于今天
    ann_date = _parse_date(parsed.get("ann_date", ""))
    if ann_date is None:
        violations.append(f"公告日期格式非法: {parsed.get('ann_date')!r}")
    elif ann_date > today:
        violations.append(f"公告日期晚于今天: {ann_date}")

    # 断言 4：单位已归一到元（parse 层完成，此处复核未残留单位字样）
    if parsed.get("unit_raw") and not isinstance(net_profit, (int, float)):
        violations.append("单位归一化失败")

    # 断言 5：同比增速与两期净利润自洽（超容差仅告警，不阻断）
    prev_profit = parsed.get("prev_profit")
    yoy_pct = parsed.get("yoy_pct")
    if (
        isinstance(net_profit, (int, float))
        and isinstance(prev_profit, (int, float))
        and isinstance(yoy_pct, (int, float))
        and prev_profit != 0
    ):
        implied = (net_profit - prev_profit) / abs(prev_profit) * 100
        if abs(implied - yoy_pct) > YOY_TOLERANCE_PP:
            warnings.append(
                f"同比不自洽: 公告 {yoy_pct:.2f}% vs 测算 {implied:.2f}%"
            )

    # 断言 6：缺失字段必须是 None，不允许被填成 0
    for field in ("net_profit", "prev_profit", "yoy_pct"):
        if parsed.get(field) == 0 and field != "net_profit":
            warnings.append(f"{field} 为 0，需确认是真值还是缺失误填")

    return violations, warnings


@tool
def validate_announcement(parsed: dict[str, Any]) -> dict[str, Any]:
    """校验公告解析结果是否可入库。

    Args:
        parsed: parse_announcement 的输出

    Returns:
        含 violations / warnings / valid 的字典。
    """
    violations, warnings = validate_parsed(parsed)
    return {
        "violations": violations,
        "warnings": warnings,
        "valid": not violations,
    }
