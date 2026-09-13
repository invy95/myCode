# 功能：按本人最新投递 PDF 正文，生成可编辑、目标两页的 Word 简历。
# 更新：2026-09-13：不再用 pdf2docx 直接转换。转换稿会在两页中间留下分节符，
#       Word 回流后变成 3 页。本脚本用单栏紧排、不分节，正文与最新 PDF 一致。

"""输出 resume/殷维_简历.docx。目标：Word / 另存 PDF 均为两页。"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


OUT = Path(__file__).resolve().parent / "殷维_简历.docx"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GRAY = RGBColor(0x55, 0x55, 0x55)
BODY = 10
LINE = 1.02


def set_run_font(run, name="微软雅黑", size=BODY, bold=False, color=None):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run._element.rPr.rFonts.set(qn("w:ascii"), name)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), name)
    if color is not None:
        run.font.color.rgb = color


def _set_bool(p_pr, tag, val="0"):
    el = p_pr.find(qn(tag))
    if el is None:
        el = OxmlElement(tag)
        p_pr.append(el)
    el.set(qn("w:val"), val)


def tight(p, before=0, after=0, line=LINE):
    """压行距，并关掉会把简历顶到第 3 页的 Word 默认项。"""
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p_pr = p._p.get_or_add_pPr()
    _set_bool(p_pr, "w:widowControl", "0")
    _set_bool(p_pr, "w:autoSpaceDE", "0")
    _set_bool(p_pr, "w:autoSpaceDN", "0")
    _set_bool(p_pr, "w:adjustRightInd", "0")
    # 禁止段前对齐网格，避免中文 Word 额外加空。
    _set_bool(p_pr, "w:snapToGrid", "0")


def add_center(doc, text, size, bold=False, after=0, color=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(p, 0, after)
    set_run_font(p.add_run(text), size=size, bold=bold, color=color)
    return p


def add_section(doc, text):
    p = doc.add_paragraph()
    tight(p, 4, 1)
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
    return p


def add_line(doc, text, size=BODY, bold=False, before=0, after=0, color=None):
    p = doc.add_paragraph()
    tight(p, before, after)
    set_run_font(p.add_run(text), size=size, bold=bold, color=color)
    return p


def add_entry_head(doc, title, dates, subtitle=None):
    p = doc.add_paragraph()
    tight(p, 3, 0)
    set_run_font(p.add_run(title), size=BODY, bold=True)
    if subtitle:
        set_run_font(p.add_run("  |  " + subtitle), size=BODY, color=GRAY)
    set_run_font(p.add_run("    " + dates), size=9.5, color=GRAY)
    return p


def add_job(doc, company, dates, title, bullets):
    add_entry_head(doc, company, dates, title)
    for i, b in enumerate(bullets, start=1):
        add_line(doc, f"{i}、{b}")


def add_project(doc, name, dates, desc, duties, result=None):
    add_entry_head(doc, "● " + name, dates)
    add_line(doc, "项目描述：" + desc)
    for i, b in enumerate(duties, start=1):
        add_line(doc, f"{i}、{b}")
    if result:
        add_line(doc, "项目业绩：" + result)


def main():
    doc = Document()
    for sec in doc.sections:
        # A4 比用户 PDF 的 Letter 高约 1.7cm，给 Word 回流留余量。
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
        sec.top_margin = Cm(1.15)
        sec.bottom_margin = Cm(1.15)
        sec.left_margin = Cm(1.45)
        sec.right_margin = Cm(1.45)
        # 页距网格关掉，避免中文版 Word 按网格撑高。
        sect_pr = sec._sectPr
        doc_grid = sect_pr.find(qn("w:docGrid"))
        if doc_grid is None:
            doc_grid = OxmlElement("w:docGrid")
            sect_pr.append(doc_grid)
        doc_grid.set(qn("w:type"), "lines")
        doc_grid.set(qn("w:linePitch"), "240")

    style = doc.styles["Normal"]
    style.font.name = "微软雅黑"
    style.font.size = Pt(BODY)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    style._element.rPr.rFonts.set(qn("w:ascii"), "微软雅黑")
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after = Pt(0)
    s_pr = style.element.get_or_add_pPr()
    _set_bool(s_pr, "w:widowControl", "0")
    _set_bool(s_pr, "w:autoSpaceDE", "0")
    _set_bool(s_pr, "w:autoSpaceDN", "0")

    add_center(doc, "殷  维", 16, bold=True, after=1, color=NAVY)
    add_center(
        doc,
        "女  |  31 岁  |  中共党员  |  湖北武汉  |  金融硕士  |  15671678098  |  yw43@foxmail.com",
        9.5,
        color=GRAY,
    )

    add_section(doc, "工  作  经  历")
    add_job(
        doc,
        "湖北正知资产管理有限公司（私募，中基协 P1007881）",
        "2026.06-至今",
        "AI 投研经理",
        [
            "根据公司投研部门推进 AI 搭建的需求，围绕“工作流”+“知识库”进行投研工作空间搭建。通过对 Coze 等多种 AI 工具功能多端体验，最终确定选型方案。在投研场景搭建 AI 投研工作流 1.0 和量化交易系统 1.0，自动生成个股研报等。",
            "给投研同事做市场数据推送：盘中放量扫描，并按“早盘/午间/午盘”收盘推送股票池要点，辅助盘中交易判断。",
            "针对“科技 vs 成长”风格切换生成“AI 撤退报告”，对接 wind api 接口，每天定时自动化更新日报发送。",
        ],
    )
    add_job(
        doc,
        "量化研究工作室",
        "2024.03-2026.06",
        "二级市场研究员",
        [
            "结合宏观与行业研究框架，研究热点赛道轮动，为策略定调提供逻辑梳理与参考。",
            "搭建标准化财务选股 AI 模型，构建季度更新核心股票池；结合短线指标完善个股买卖点参考逻辑。",
        ],
    )
    add_job(
        doc,
        "江西铜业产融控股有限公司",
        "2023.10-2024.02",
        "投资管理岗",
        [
            "设计调查问卷，对北上广深的量化管理人进行现场尽调，并生成管理人尽调报告。",
        ],
    )
    add_job(
        doc,
        "量盈私募基金管理有限公司",
        "2022.01-2023.09",
        "量化研究员",
        [
            "进行期货、股票因子挖掘、策略开发及回测，并对策略回测结果表现进行分析优化。",
            "根据基金经理要求，使用 python 对券商金工等策略研报进行复现。",
        ],
    )
    add_job(
        doc,
        "深圳引力波量化科技有限公司",
        "2020.08-2021.12",
        "做市产品经理",
        [
            "直接对接交易所需求方，根据对方交易所提出的具体盘口页面需求，落成可执行参数：买一至买五各档的价位排布、每档挂单量、后台逐档铺单的秒级间隔。",
            "自己用 python 在交易所接口上实现铺单程序并上线，搭建物理风控与策略程序风控，盯盘处理极端行情下的撤单与反向平仓。",
            "交易数据获取与清洗（Pandas、Numpy、Talib），做市项目的套利收益跟踪。",
        ],
    )
    add_job(
        doc,
        "中国平安财产保险股份有限公司",
        "2019.07-2020.07",
        "再保险业务管理岗（管培生）",
        [
            "使用 excel 对再保人资信进行月度更新并审核、季度坏账计提、监控风险指标，汇总关联与非关联交易数据。",
        ],
    )

    add_section(doc, "教  育  背  景")
    add_line(doc, "2017.09-2019.06    华中科技大学    金融    硕士（全日制）", before=1)
    add_line(doc, "2013.09-2017.06    武汉科技大学    机械工程    本科（全日制）")

    add_section(doc, "项  目  经  历")
    add_project(
        doc,
        "投研侧 AI：投研需求落地与决策辅助",
        "2026.06-至今",
        "用 AI 把研报生成、公告和市场扫描做成可跑通的小流程，收集投研同事需求并做成可复用的流程和系统。",
        [
            "部门投研平台搭建：日常工作流+AI 投研工作流+知识库搭建，并实现工作空间全连通。帮助部门工作实现 AI 化的留痕、归档、协同、研究。",
            "使用 AI 生成研报、大盘分析报告等部署到投研智能体并每日推送到微信、飞书；做市场数据解析（盘中放量扫描）与股票池分时段推送。",
        ],
    )
    add_project(
        doc,
        "股票投资研究",
        "2024.03-至今",
        "使用 cursor 等 AI Agent 搭建多维度股票分析框架，从基本面、情绪面、技术面解析市场数据、梳理逻辑、整理财报与业绩归因，辅助策略研究决策。",
        [
            "搭建财报数据收集系统：用 tushare 收集全市场个股基本面数据并计算相关因子值。",
            "编写业绩预报、快报爬虫及时爬取个股业绩信息；设计实时热点概念看板。",
        ],
        "加深对财报基本面、短线技术形态与市场情绪周期的理解，能把研究想法落到可核对的选股条件。",
    )
    add_project(
        doc,
        "股票短线多头策略",
        "2022.07-2023.02",
        "使用掘金平台开发股票短线多头策略，通过分钟级别板块因子组合日线级别量价因子进行择时选股获得超额收益，并进行策略实盘，共挖掘 6 个因子，其中 3 个组合成策略有效性最佳。",
        [
            "通过分析量价关系组合择时、选股因子，结合入场出场方式研发策略，并对参数、因子组合进行回测优化。",
            "编写实盘策略版本，接入掘金每日更新数据。",
        ],
        "回测样本内最大回撤 2%，年化收益 17.14%，夏普比率 3.4。",
    )
    add_project(
        doc,
        "金融工程研报复现",
        "2022.11-2023.01",
        "使用 python 结合 wind 数据库对金融工程研报《3M 板块轮动策略》进行复现。",
        [
            "学习研究研报并用 wind 收集涉及的微观部分数据，对策略微观因子设计算法进行计算。",
        ],
        "完成微观因子的数据收集和因子时间截面的输出。",
    )
    add_project(
        doc,
        "期货 CTA 策略研究",
        "2022.01-2022.03",
        "使用 python 结合 tbquant 针对“基于期货的模式识别”进行策略开发及优化工作。",
        [
            "使用 TBQuant 平台与 python 对接实现数据处理并传递；基于拓扑空间结构距离开发模式识别策略算法。",
            "将模式识别策略应用于股指期货市场，进行回测结果分析与策略、参数优化。",
        ],
        "基于股指期货回测 2012-2018 年连续 7 年每年回测收益率为正，年化收益率 80%。",
    )
    add_project(
        doc,
        "做市项目：需求对接 → 铺单方案设计 → 上线",
        "2020.12-2021.12",
        "为交易所提供流动性。包括需求对接、方案设计、程序实现等全流程。",
        [
            "与交易所对接明确流动性目标与盘口形态要求，设计后台铺单序列的相关落地参数，使得五档价位排布、每档挂单数量、逐档铺出节奏合理且贴近真实的市场情况。",
            "用 python 程序实现上线该项目；配套物理风控与程序风控，盯盘控制极端行情风险并及时手动反向平仓。",
        ],
        "提升交易所交投活跃度；完整跑通「需求 → 参数设计 → 实现 → 上线盯盘」闭环。",
    )

    add_section(doc, "荣  誉  技  能")
    for line in [
        "证券、基金、银行从业资格证书；计算机二级；英语四、六级（558）。硕士论文：《医药行业上市公司价值评估研究--以云南白药为例》（采用 Gordon 股利估值模型估值，并用 python 编写量化策略验证）",
        "熟练掌握 python、matlab、wind、Stata、Excel、Access、PPT，能用 wind 结合 excel 做金融数据分析",
        "日常用 Cursor、Claude 做投研任务的拆解、实现和验收，会配 MCP 把工具接到工作流里；用 Coze 搭过投研智能体并对接微信、飞书，能把多步任务编成可跑的 agent 流程（LangGraph），能做 skills 并上传 coze 商店，对不同 AI 工具和不同模型的使用场景有一定了解。用代码能力，也能用 AI 写代码做轻量验证。",
        "近期远程交付：Xpert 金融专家 ai 标注项目、量化工作室以远程协同合作的方式进行。",
    ]:
        add_line(doc, line)

    # 丢掉 python-docx 默认多出来的空段，避免末尾再占半页。
    body = doc.element.body
    for child in list(body):
        if child.tag == qn("w:p") and not "".join(child.itertext()).strip():
            # 保留 sectPr 所在段
            p_pr = child.find(qn("w:pPr"))
            if p_pr is not None and p_pr.find(qn("w:sectPr")) is not None:
                continue
            if child.getnext() is None:
                continue
            body.remove(child)

    doc.save(OUT)
    print(f"已生成：{OUT}")


if __name__ == "__main__":
    main()
