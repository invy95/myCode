# 功能：按原简历模块顺序生成「两页投递稿」，只收字、不重排结构。
# 更新：2026-08-30：正知/工作室/短线留细；江铜量盈引力波平安各留一行；去掉做市、CTA、研报复现。

"""输出 殷维_简历_两页投递.docx。职位名、公司名、日期、保留项目的数字与原 PDF 一致。"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


OUT = Path(__file__).resolve().parent / "殷维_简历_两页投递.docx"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GRAY = RGBColor(0x55, 0x55, 0x55)


def set_run_font(run, name="微软雅黑", size=10, bold=False, color=None):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    if color is not None:
        run.font.color.rgb = color


def tight(p, before=0, after=1, line=1.02):
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = line


def add_center(doc, text, size, bold=False, after=1, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(p, 0, after, 1.0)
    set_run_font(p.add_run(text), size=size, bold=bold, color=color)


def add_section(doc, text):
    p = doc.add_paragraph()
    tight(p, 6, 2, 1.0)
    set_run_font(p.add_run(text), size=11, bold=True, color=NAVY)
    p_pr = p._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "1F3A5F")
    p_bdr.append(bottom)
    p_pr.append(p_bdr)


def add_line(doc, text, size=10, bold=False, before=0, after=1, color=None):
    p = doc.add_paragraph()
    tight(p, before, after)
    set_run_font(p.add_run(text), size=size, bold=bold, color=color)


def add_job_full(doc, company, dates, title, bullets):
    p = doc.add_paragraph()
    tight(p, 4, 0)
    set_run_font(p.add_run(company), size=10, bold=True)
    set_run_font(p.add_run("  |  " + title), size=10, color=GRAY)
    set_run_font(p.add_run("    " + dates), size=9.5, color=GRAY)
    for i, b in enumerate(bullets, start=1):
        add_line(doc, f"{i}、{b}", size=10, after=1)


def add_job_one_line(doc, company, dates, title, summary):
    p = doc.add_paragraph()
    tight(p, 3, 0)
    set_run_font(p.add_run(company), size=10, bold=True)
    set_run_font(p.add_run("  |  " + title), size=10, color=GRAY)
    set_run_font(p.add_run("    " + dates), size=9.5, color=GRAY)
    add_line(doc, summary, size=10, after=1)


def add_project(doc, name, dates, desc, duties, result):
    p = doc.add_paragraph()
    tight(p, 4, 1)
    set_run_font(p.add_run("● " + name), size=10, bold=True)
    set_run_font(p.add_run("    " + dates), size=9.5, color=GRAY)
    add_line(doc, "项目描述：" + desc, size=10, after=1)
    for i, b in enumerate(duties, start=1):
        add_line(doc, f"{i}、{b}", size=10, after=1)
    add_line(doc, "项目业绩：" + result, size=10, after=1)


def main():
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(1.2)
        sec.bottom_margin = Cm(1.2)
        sec.left_margin = Cm(1.6)
        sec.right_margin = Cm(1.6)

    style = doc.styles["Normal"]
    style.font.name = "微软雅黑"
    style.font.size = Pt(10)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    add_center(doc, "殷  维", 16, bold=True, after=2, color=NAVY)
    add_center(
        doc,
        "女  |  31岁  |  中共党员  |  湖北武汉  |  165cm  |  金融硕士",
        9.5,
        after=0,
        color=GRAY,
    )
    add_center(
        doc,
        "15671678098  |  yw43@foxmail.com  |  武汉市洪山区",
        9.5,
        after=0,
        color=GRAY,
    )
    add_center(doc, "求职意向：AI产品经理（交易创新方向）", 10, bold=True, after=2)

    add_section(doc, "工  作  经  历")
    add_job_full(
        doc,
        "湖北正知资产管理有限公司（私募，中基协 P1007881）",
        "2026.06-至今",
        "AI投研 / 量化研究",
        [
            "对比 WorkBuddy、Coze，部署投研智能体并对接微信、飞书，先打通可用再迭代；Linux 定时任务保证工作日可跑。",
            "为看盘同事做盘中放量扫描，按上午 / 午盘 / 下午 / 收盘推送股票池要点。",
            "把「强势股放量」收成带过滤的可回测规则（收盘价 / 前20日最低价 < 130%），对照回测看最大单笔亏损变化，并记录低波动、下跌市失效。",
        ],
    )
    add_job_full(
        doc,
        "量化研究工作室",
        "2024.03-2026.04",
        "二级市场研究员",
        [
            "结合宏观与行业框架研究热点赛道轮动，搭建季度更新的财务选股池。",
            "结合短线指标完善个股买卖点，自己看盘执行并复盘。",
        ],
    )
    add_job_one_line(
        doc,
        "江西铜业产融控股有限公司",
        "2023.10-2024.02",
        "投资管理岗",
        "使用 tbquant、聚宽、掘金等平台做期货 / 股票因子与回测，按要求用 python 复现金工研报。",
    )
    add_job_one_line(
        doc,
        "量盈私募基金管理有限公司",
        "2022.01-2023.09",
        "量化研究员",
        "期货、股票因子挖掘、策略开发及回测；按基金经理要求用 python 复现券商金工研报。",
    )
    add_job_one_line(
        doc,
        "深圳引力波量化科技有限公司",
        "2020.08-2021.12",
        "量化研究员",
        "用 Pandas、Numpy、Talib 清洗交易数据；参与套利、做市策略的日常优化与维护。",
    )
    add_job_one_line(
        doc,
        "中国平安财产保险股份有限公司",
        "2019.07-2020.07",
        "再保险业务管理岗（管培生）",
        "再保人资信月度更新、季度坏账计提与风险指标监控；汇总关联 / 非关联交易。",
    )

    add_section(doc, "教  育  背  景")
    add_line(doc, "2017.09-2019.06    华中科技大学    金融    硕士（全日制）", size=10, before=2, after=1)
    add_line(doc, "2013.09-2017.06    武汉科技大学    机械工程    本科（全日制）", size=10, after=1)

    add_section(doc, "项  目  经  历")
    add_project(
        doc,
        "交易侧 AI 投研辅助",
        "2026.06-至今",
        "用 AI 工具把盘中看盘和公告采集做成可跑通的小流程，先给内部同事用，再用对照回测验证，不先上重系统。",
        [
            "做盘中放量扫描和分时段推送；把「找强势股」写成带 130% 过滤的规则并对照回测。",
            "把「盯公告 / 净利润」拆成采集、校验、失败换源。demo：github.com/invy95/myCode（langgraph-announcement-agent）。",
        ],
        "对照回测中最大单笔亏损约从 -27% 降至 -17%，并写明下跌市信号变差；不把模型输出当成成交指令。",
    )
    add_project(
        doc,
        "股票投资研究",
        "2024.03-至今",
        "用 cursor 等 AI 工具搭多维度分析框架，追踪热点板块、整理财报与业绩预告，辅助投资决策。",
        [
            "用 tushare 收集财报并计算基本面因子；编写业绩预报 / 快报爬虫。",
            "做实时热点概念看板，追踪热点板块。",
        ],
        "完成数据收集与有效性观察，日常用 AI 工具拆任务并自己验数。",
    )
    doc.add_page_break()
    add_project(
        doc,
        "股票短线多头策略",
        "2022.07-2023.02",
        "掘金平台开发短线多头：分钟级板块因子组合日线量价因子择时选股，并接日更数据做实盘版。共挖掘 6 个因子，其中 3 个组合效果最好。",
        [
            "组合择时 / 选股因子，选择入场出场方式，做回测与参数优化。",
            "编写实盘策略版本，接入掘金每日更新数据。",
        ],
        "回测样本内最大回撤 2%，年化收益 17.14%，夏普比率 3.4。",
    )

    add_section(doc, "荣  誉  技  能")
    add_line(
        doc,
        "证书：证券 / 基金 / 银行从业、计算机二级；英语六级 558。论文：《医药行业上市公司价值评估研究--以云南白药为例》。",
        size=10,
        after=1,
    )
    add_line(
        doc,
        "工具：Python（Pandas / Numpy / Talib）、matlab、wind、掘金、聚宽、Excel；claude、cursor、Coze、MCP。能把投研任务拆成采集、校验、换源，不把模型输出当成下单指令。",
        size=10,
        after=1,
    )
    add_line(
        doc,
        "近期：Xpert 金融 Skill 评测、TalentsAI Agentic Coding × 金融已过审（远程交付，非全职经历）。",
        size=10,
        after=1,
    )

    doc.save(OUT)
    print(f"已生成：{OUT}")


if __name__ == "__main__":
    main()
