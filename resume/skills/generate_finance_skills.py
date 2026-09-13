# 功能：只保留两条金融投研 Skill 全文，以及 Skill 自己的判定规则和落盘样例。
# 更新：2026-09-13：去掉 TalentsAI 申请说明、Agentic Coding 岗位包装、四道平台样题、
#       Dockerfile/test.sh 交付清单和页脚「仅用于 TalentsAI 申请」。

"""输出 Finance_Research_Skills.docx。不含任何 TalentsAI 申请材料。"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


OUT = Path(__file__).resolve().parent / "Finance_Research_Skills.docx"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GRAY = RGBColor(0x55, 0x55, 0x55)
TEXT = RGBColor(0x22, 0x22, 0x22)


def set_run(run, size=11, bold=False, color=TEXT, name="微软雅黑"):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    run._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    run.font.color.rgb = color


def tight(p, before=2, after=4):
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.08


def heading(doc, text):
    p = doc.add_paragraph()
    tight(p, 12, 6)
    set_run(p.add_run(text), 13, bold=True, color=NAVY)
    ppr = p._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "1F3A5F")
    p_bdr.append(bottom)
    ppr.append(p_bdr)


def subhead(doc, text):
    p = doc.add_paragraph()
    tight(p, 8, 3)
    set_run(p.add_run(text), 12, bold=True, color=NAVY)


def body(doc, text, size=11):
    p = doc.add_paragraph()
    tight(p, 1, 4)
    set_run(p.add_run(text), size)


def bullet(doc, text, size=11):
    p = doc.add_paragraph()
    tight(p, 0, 2)
    p.paragraph_format.left_indent = Cm(0.4)
    set_run(p.add_run("• " + text), size)


def code_block(doc, text):
    p = doc.add_paragraph()
    tight(p, 4, 6)
    p.paragraph_format.left_indent = Cm(0.25)
    run = p.add_run(text)
    set_run(run, 9, name="Consolas")
    # 浅底，方便当 Skill 说明书读
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F4F6F8")
    p._p.get_or_add_pPr().append(shd)


def shade_cell(cell, fill="1F3A5F"):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        tight(p, 1, 1)
        set_run(p.add_run(h), 8, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        shade_cell(cell)
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            p = cell.paragraphs[0]
            tight(p, 1, 1)
            set_run(p.add_run(str(val)), 8)
    doc.add_paragraph()


def main():
    doc = Document()
    for sec in doc.sections:
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
        sec.top_margin = Cm(1.4)
        sec.bottom_margin = Cm(1.4)
        sec.left_margin = Cm(1.6)
        sec.right_margin = Cm(1.6)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(title, 0, 2)
    set_run(title.add_run("金融投研 Skills"), 18, bold=True, color=NAVY)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(sub, 0, 8)
    set_run(
        sub.add_run("殷维 ｜ yw43@foxmail.com ｜ 15671678098"),
        10,
        color=GRAY,
    )

    body(
        doc,
        "下面两份是给 Agent 用的说明书：目标、步骤、验收字段写死，便于稳定复跑。"
        "只保留 Skill 本身，以及跑 Skill 需要的判定规则和落盘样例。",
    )

    heading(doc, "Skill 1　盘中热点板块监控")
    code_block(
        doc,
        "name: 盘中热点板块监控\n"
        "适用：用户提到盘中热点、概念涨停、涨停监控、启停分钟热度表。\n\n"
        "目标：交易时段监控全市场涨停，按概念板块输出热度；落盘分钟 CSV 供复盘。\n\n"
        "行为要点\n"
        "- 约 3 秒检测新增涨停；约 1 分钟输出概念统计并追加当日热度表。\n"
        "- 屏幕显示前 30 个有涨停的概念；落盘表含全部概念（含 0 涨停）。\n"
        "- 交易时段：09:25–11:30、13:00–15:00；周末不跑。\n"
        "- 工作日开盘前启动、收盘后停止。\n"
        "- 涨停阈值按主板 / 创业板科创板 / 北交所 / ST 区分。\n\n"
        "验收\n"
        "- 进程在交易时段存活；当日热度表持续追加。\n"
        "- 表头固定：时间、概念板块、涨停数、较上分钟、今日峰值、新增、开板。\n"
        "- 分析时按时间切片，对涨停数降序取 Top；同时看较上分钟、峰值、新增、开板。",
    )

    subhead(doc, "涨停判定（Skill 内规则）")
    body(
        doc,
        "按代码前缀区分板块；ST 按证券简称判断，不按代码字符串。",
        size=10,
    )
    code_block(
        doc,
        "def get_limit_up_threshold(pre_close, stock_code, stock_name):\n"
        "    # 科创板 688/689、创业板 300 → 20%\n"
        "    if stock_code.startswith(('688', '689', '300')):\n"
        "        return pre_close * 1.20\n"
        "    # 北交所 8/4 开头 → 30%\n"
        "    if stock_code.startswith(('8', '4')):\n"
        "        return pre_close * 1.30\n"
        "    # ST / *ST → 5%\n"
        "    if 'ST' in (stock_name or '').upper():\n"
        "        return pre_close * 1.05\n"
        "    # 主板 → 10%\n"
        "    return pre_close * 1.10",
    )
    body(
        doc,
        "线上脚本可用 19.5%/9.5% 容差做盘中预警。正式验收用整阈值（10/20/30/5），"
        "涨幅卡在 19.99% 的样本必须判「未涨停」。",
        size=10,
    )

    subhead(doc, "落盘样例｜2026-08-21 09:25 开盘附近")
    add_table(
        doc,
        ["时间", "概念板块", "涨停数", "较上分钟", "今日峰值", "新增", "开板"],
        [
            ["2026-08-21 09:25:08", "储能", "1", "1", "1", "*ST威领", "-"],
            ["2026-08-21 09:25:08", "幽门螺杆菌", "2", "2", "2", "双鹭药业, 汉森制药", "-"],
            ["2026-08-21 09:25:08", "锂矿", "1", "1", "1", "*ST威领", "-"],
            ["2026-08-21 09:25:08", "减肥药", "1", "1", "1", "双鹭药业", "-"],
            ["2026-08-21 09:25:08", "智能医疗", "1", "1", "1", "双鹭药业", "-"],
            ["2026-08-21 09:25:08", "特斯拉概念", "0", "0", "0", "-", "-"],
            ["2026-08-21 09:25:08", "虚拟电厂", "0", "0", "0", "-", "-"],
            ["2026-08-21 09:25:08", "算力租赁", "0", "0", "0", "-", "-"],
        ],
    )

    subhead(doc, "落盘样例｜同日「储能」连续分钟")
    add_table(
        doc,
        ["时间", "概念板块", "涨停数", "较上分钟", "今日峰值", "新增", "开板"],
        [
            ["2026-08-21 09:25:08", "储能", "1", "1", "1", "*ST威领", "-"],
            ["2026-08-21 09:26:02", "储能", "1", "0", "1", "-", "-"],
            ["2026-08-21 09:27:02", "储能", "1", "0", "1", "-", "-"],
            ["2026-08-21 09:28:00", "储能", "1", "0", "1", "-", "-"],
            ["2026-08-21 09:29:00", "储能", "1", "0", "1", "-", "-"],
            ["2026-08-21 09:30:03", "储能", "1", "0", "1", "-", "-"],
            ["2026-08-21 09:31:02", "储能", "2", "1", "2", "福华尚纬", "-"],
            ["2026-08-21 09:32:01", "储能", "2", "0", "2", "-", "-"],
        ],
    )

    heading(doc, "Skill 2　巨潮净利润采集")
    code_block(
        doc,
        "name: 巨潮净利润采集\n"
        "适用：用户提到巨潮、业绩预告、归母净利润、变动幅度、业绩快报。\n\n"
        "目标：按指定日期拉取业绩预告，提取归母净利润（万元）与变动幅度（%），"
        "导出表格后再做财务价值筛选。\n\n"
        "执行步骤\n"
        "1. 依赖：requests、pandas；东财兜底可选。\n"
        "2. 写入要跑的日期列表后执行采集脚本。\n"
        "3. 检查当日目录是否同时出现「业绩预告表」和「业绩价值表」。\n\n"
        "解析优先级（勿改乱序）：PDF → 东财接口 → 标题推断。\n\n"
        "业绩预告表字段：公告ID、股票代码、股票简称、公告类型、公告标题、公告时间、"
        "公告pdf、归母净利润（万元）、归母净利润变动幅度（%）、变动幅度展示、"
        "预告类型、业绩变动原因、数据来源。\n\n"
        "价值筛选摘要：负债可控、现金为正、ROE 非负，且 ROE>8% 或较上年改善。",
    )

    subhead(doc, "解析优先级（Skill 内规则，乱序即错）")
    bullet(doc, "1. PDF 表格抽取归母净利润、变动幅度。")
    bullet(doc, "2. PDF 失败：东财业绩预告接口补数字，来源记 eastmoney。")
    bullet(doc, "3. 仍缺增速：标题推断或标记预告类型，禁止用 0 填缺失。")
    bullet(doc, "预告与快报并存时保留两行，用类型字段区分，禁止合成一条。日期用公告披露日。")
    body(
        doc,
        "列表接口没有摘要，标题也常常没有增速，所以必须先下 PDF，不能只扫标题。",
        size=10,
    )

    subhead(doc, "落盘样例｜2026-07-14 业绩预告")
    add_table(
        doc,
        ["代码", "简称", "归母净利(万元)", "变动%", "展示", "来源", "标题"],
        [
            ["300118", "东方日升", "230000", "24.33", "+24.33%", "pdf+em", "2025年度业绩预告"],
            ["302132", "中航成飞", "340000", "2927.37", "+2927.37%", "pdf", "2025年度业绩预告"],
            ["300862", "蓝盾光电", "7000", "1179.36", "+1179.36%", "pdf", "2025年度业绩预告"],
            ["300971", "博亚精工", "8000", "82.68", "+82.68%", "pdf", "2025年度业绩预告"],
            ["300323", "华灿光电", "-45000", "26.37", "+26.37%", "eastmoney", "2025年度业绩预告"],
            ["300107", "建新股份", "-2450", "-226.52", "-226.51%", "eastmoney", "2025年度业绩预告"],
            ["301110", "青木科技", "11770.18", "30.00", "+30.00%", "pdf", "2025年度业绩预告"],
            ["300672", "国科微", "-21500", "-321.30", "-321.30%", "eastmoney", "2025年度业绩预告"],
            ["300061", "旗天科技", "9500", "55.65", "+55.65%", "pdf", "2025年度业绩预告"],
            ["300497", "富祥药业", "-4800", "82.36", "+82.36%", "eastmoney", "2025年度业绩预告"],
        ],
    )

    doc.save(OUT)
    print(f"已生成：{OUT}")


if __name__ == "__main__":
    main()
