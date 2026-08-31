# -*- coding: utf-8 -*-
"""
岗位投递跟踪表生成与维护脚本。
用于将用户提供的招聘信息录入 Excel，并支持后续定期更新投递状态。
创建时间：2026-08-31
"""

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

# 表头定义
COLUMNS = [
    "录入日期",
    "岗位名称",
    "公司/平台",
    "工作地点",
    "办公方式",
    "岗位要求摘要",
    "薪资范围",
    "投递状态",
    "投递日期",
    "简历版本",
    "匹配度评估",
    "备注",
    "信息来源",
]

STATUS_OPTIONS = ["待评估", "待投递", "已投递", "简历筛选", "面试中", "已拒绝", "已录用", "已放弃"]

# 初始岗位数据（用户提供的招聘信息）
INITIAL_JOBS = [
    {
        "录入日期": "2026-08-31",
        "岗位名称": "AI Chatbot 客服产品经理/专家",
        "公司/平台": "top平台（待确认具体公司）",
        "工作地点": "远程/吉隆坡",
        "办公方式": "线上办公",
        "岗位要求摘要": "统招本科以上；3年以上AI产品经验；负责智能对话打磨，优化机器人应答逻辑",
        "薪资范围": "待确认",
        "投递状态": "待评估",
        "投递日期": "",
        "简历版本": "",
        "匹配度评估": "学历符合；AI产品经验需简历侧重包装（见备注）",
        "备注": "流程超快；可尝试用AI工具/agent搭建经历+产品化思维补强投递",
        "信息来源": "用户转发招聘信息",
    },
]


def _style_header(ws):
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    for col_idx, title in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _auto_width(ws):
    for col_idx, title in enumerate(COLUMNS, start=1):
        max_len = len(title)
        for row in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
            val = row[0].value
            if val:
                max_len = max(max_len, min(len(str(val)), 50))
        ws.column_dimensions[get_column_letter(col_idx)].width = max_len + 2


def create_tracker(excel_path: Path, jobs: list[dict] | None = None) -> Path:
    jobs = jobs or INITIAL_JOBS
    wb = Workbook()
    ws = wb.active
    ws.title = "岗位投递跟踪"
    _style_header(ws)

    for row_idx, job in enumerate(jobs, start=2):
        for col_idx, key in enumerate(COLUMNS, start=1):
            ws.cell(row=row_idx, column=col_idx, value=job.get(key, ""))
            ws.cell(row=row_idx, column=col_idx).alignment = Alignment(
                vertical="top", wrap_text=True
            )

    _auto_width(ws)
    ws.freeze_panes = "A2"

    # 状态说明页
    guide = wb.create_sheet("使用说明")
    guide["A1"] = "投递状态可选值"
    guide["A1"].font = Font(bold=True)
    for i, status in enumerate(STATUS_OPTIONS, start=2):
        guide[f"A{i}"] = status
    guide["A10"] = "更新方式"
    guide["A10"].font = Font(bold=True)
    guide["A11"] = "1. 直接在 Excel 中编辑「岗位投递跟踪」表"
    guide["A12"] = "2. 或将新岗位信息发给 AI，由脚本追加后重新生成"
    guide["A14"] = f"最近生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"

    wb.save(excel_path)
    return excel_path


if __name__ == "__main__":
    out = Path(__file__).parent / "岗位投递跟踪.xlsx"
    path = create_tracker(out)
    print(f"已生成：{path}")
