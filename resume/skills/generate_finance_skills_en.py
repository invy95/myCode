# 功能：两条金融投研 Skill 的英文说明书，规则与中文版一致。
# 更新：2026-09-13：按中文 Skill 全文英译；不含 TalentsAI 申请包装；落盘数字与代码逻辑不改。

"""输出 Finance_Research_Skills_EN.docx。"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


OUT = Path(__file__).resolve().parent / "Finance_Research_Skills_EN.docx"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GRAY = RGBColor(0x55, 0x55, 0x55)
TEXT = RGBColor(0x22, 0x22, 0x22)


def set_run(run, size=11, bold=False, color=TEXT, name="Calibri"):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    run._element.rPr.rFonts.set(qn("w:ascii"), name)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), name)
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
    set_run(title.add_run("Investment-Research Skills"), 18, bold=True, color=NAVY)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(sub, 0, 8)
    set_run(sub.add_run("Yin Wei  |  yw43@foxmail.com  |  15671678098"), 10, color=GRAY)

    body(
        doc,
        "These two documents are instructions for an agent. The goal, steps, and acceptance fields are fixed so the run can be repeated. "
        "This file keeps only the skills themselves, plus the decision rules and saved-output samples needed to run them.",
    )

    heading(doc, "Skill 1  Intraday Hot-Theme Monitor")
    code_block(
        doc,
        "name: Intraday Hot-Theme Monitor\n"
        "Also triggered by: 盘中热点板块监控; mentions of intraday themes, concept limit-ups, "
        "limit-up monitoring, or starting and stopping the minute heat table.\n\n"
        "Goal: During the trading session, detect limit-up stocks across the A-share market, "
        "score heat by concept theme, and append a minute-level CSV for later review.\n\n"
        "Behavior\n"
        "- Detect newly limit-up names about every 3 seconds; write theme statistics and append "
        "the daily heat table about every 1 minute.\n"
        "- Show the top 30 themes that have at least one limit-up on screen; persist every theme "
        "in the file, including those with zero limit-ups.\n"
        "- Session hours: 09:25–11:30 and 13:00–15:00; do not run on weekends.\n"
        "- Start before the open on trading days; stop after the close.\n"
        "- Limit-up thresholds differ for the Main Board, ChiNext / STAR Market, "
        "the Beijing Stock Exchange, and ST names.\n\n"
        "Acceptance\n"
        "- The process stays up during the session; the daily heat table keeps growing.\n"
        "- Header (fixed Chinese labels): 时间 (time), 概念板块 (theme), 涨停数 (limit-up count), "
        "较上分钟 (change vs. last minute), 今日峰值 (session peak), 新增 (new limit-ups), "
        "开板 (limit-up reversals).\n"
        "- When reviewing, slice by timestamp, rank themes by limit-up count, and also read "
        "the change, the peak, the new names, and the reversals.",
    )

    subhead(doc, "Limit-up rule (inside the skill)")
    body(
        doc,
        "Assign the board from the stock-code prefix. Treat ST from the security short name, not from the code string.",
        size=10,
    )
    code_block(
        doc,
        "def get_limit_up_threshold(pre_close, stock_code, stock_name):\n"
        "    # STAR 688/689, ChiNext 300 → 20%\n"
        "    if stock_code.startswith(('688', '689', '300')):\n"
        "        return pre_close * 1.20\n"
        "    # Beijing Stock Exchange codes starting with 8 or 4 → 30%\n"
        "    if stock_code.startswith(('8', '4')):\n"
        "        return pre_close * 1.30\n"
        "    # ST / *ST → 5%\n"
        "    if 'ST' in (stock_name or '').upper():\n"
        "        return pre_close * 1.05\n"
        "    # Main Board → 10%\n"
        "    return pre_close * 1.10",
    )
    body(
        doc,
        "The live script may use 19.5% / 9.5% bands for an early intraday alert. Formal acceptance uses the full thresholds "
        "(10 / 20 / 30 / 5). A print that stops at 19.99% must be scored as not limit-up.",
        size=10,
    )

    subhead(doc, "Saved sample  |  2026-08-21 09:25, near the open")
    add_table(
        doc,
        ["Time", "Theme", "Limit-ups", "vs last min", "Session peak", "New names", "Reversals"],
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

    subhead(doc, "Saved sample  |  same day, 储能 (energy storage), consecutive minutes")
    add_table(
        doc,
        ["Time", "Theme", "Limit-ups", "vs last min", "Session peak", "New names", "Reversals"],
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

    heading(doc, "Skill 2  CNINFO Net-Profit Collector")
    code_block(
        doc,
        "name: CNINFO Net-Profit Collector\n"
        "Also triggered by: 巨潮净利润采集; mentions of CNINFO (巨潮), earnings pre-announcements, "
        "net profit attributable to the parent, the percentage change, or earnings flashes.\n\n"
        "Goal: For each requested date, pull earnings pre-announcements, extract net profit attributable "
        "to the parent (RMB 10,000) and the percentage change, export a table, then run a financial quality screen.\n\n"
        "Steps\n"
        "1. Dependencies: requests and pandas; the East Money fallback is optional.\n"
        "2. Write the list of dates to run, then execute the collector.\n"
        "3. Confirm that the date folder contains both the earnings-forecast table and the value-screen table.\n\n"
        "Parse order (do not reorder): PDF → East Money API → title inference.\n\n"
        "Forecast-table fields: announcement ID, stock code, short name, announcement type, title, "
        "announcement time, PDF link, net profit attributable to the parent (RMB 10,000), "
        "percentage change, display string for the change, forecast type, reason for the change, and data source.\n\n"
        "Value screen: leverage stays in range, cash is positive, ROE is not negative, and either ROE > 8% "
        "or ROE improved versus the prior year.",
    )

    subhead(doc, "Parse order (inside the skill; the wrong order is an error)")
    bullet(doc, "1. Extract net profit attributable to the parent and the percentage change from the PDF tables.")
    bullet(doc, "2. If the PDF fails, fill the numbers from the East Money earnings-forecast API and mark the source as eastmoney.")
    bullet(doc, "3. If the growth rate is still missing, infer it from the title or tag the forecast type. Do not fill missing values with 0.")
    bullet(
        doc,
        "If a pre-announcement and a flash report both exist, keep two rows and distinguish them with the type field. "
        "Do not merge them into one row. Use the disclosure date, not the reporting period.",
    )
    body(
        doc,
        "The list API has no abstract, and titles often omit the growth rate, so the PDF must be downloaded first. Do not scan titles only.",
        size=10,
    )

    subhead(doc, "Saved sample  |  2026-07-14 earnings pre-announcements")
    add_table(
        doc,
        ["Code", "Name", "Parent NP (RMB 10k)", "Change %", "Display", "Source", "Title"],
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
    print(f"Generated: {OUT}")


if __name__ == "__main__":
    main()
