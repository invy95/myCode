#!/usr/bin/env python3
# 功能：生成 TalentsAI Agentic Coding×金融 单文件投递材料（胜任原因 + 落盘证据 + Skill + 出题）。
# 更新 2026-08-23：与「核心能力证明_投递版」合并；删除本机路径/附件索引，证据与摘录全部写进本文。

"""Single-file TalentsAI application pack. No external path index."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

LATIN = "Aptos"
CJK = "Microsoft YaHei"
ACCENT = (26, 83, 92)
TEXT = (34, 34, 34)
MUTED = (90, 90, 90)


def set_run(run, size=11, bold=False, color=TEXT, italic=False):
    run.font.name = LATIN
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), CJK)
    rfonts.set(qn("w:ascii"), LATIN)
    rfonts.set(qn("w:hAnsi"), LATIN)


def tight(p, before=2, after=4):
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.12


def add_bottom_border(p):
    ppr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "12")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "1A535C")
    pBdr.append(bottom)
    ppr.append(pBdr)


def heading(doc, text):
    p = doc.add_paragraph()
    tight(p, 12, 6)
    set_run(p.add_run(text), 13, bold=True, color=ACCENT)
    add_bottom_border(p)


def subhead(doc, text):
    p = doc.add_paragraph()
    tight(p, 8, 3)
    set_run(p.add_run(text), 12, bold=True, color=ACCENT)


def body(doc, text, size=11):
    p = doc.add_paragraph()
    tight(p, 1, 4)
    set_run(p.add_run(text), size)


def bullet(doc, text, size=11):
    p = doc.add_paragraph()
    tight(p, 0, 2)
    p.paragraph_format.left_indent = Cm(0.45)
    set_run(p.add_run("• " + text), size)


def kv(doc, label, text):
    p = doc.add_paragraph()
    tight(p, 1, 2)
    p.paragraph_format.left_indent = Cm(0.3)
    set_run(p.add_run(label + "："), 10.5, bold=True)
    set_run(p.add_run(text), 10.5)


def code_block(doc, text):
    p = doc.add_paragraph()
    tight(p, 2, 6)
    p.paragraph_format.left_indent = Cm(0.2)
    set_run(p.add_run(text), 8.5, color=(40, 40, 40))


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        tight(p, 1, 1)
        set_run(p.add_run(h), 8.5, bold=True, color=ACCENT)
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            p = cell.paragraphs[0]
            tight(p, 1, 1)
            set_run(p.add_run(str(val)), 8)
    doc.add_paragraph()


PASTE = (
    "机会：大模型训练专家 | Agentic Coding × 金融领域\n\n"
    "我做了几年 A 股量化研究和工程落地，日常就是把一个投研问题写成能跑、能对的东西："
    "先写清要算什么，再用 Python/Bash 做出来，最后用落盘表格验收。"
    "这和本岗位要的「在 Docker/终端里按 instruction 完成金融编程任务，并用脚本判定通过/失败」是同一条链路。\n\n"
    "已经跑通的两条闭环：一是盘中涨停按概念板块统计热度，约 3 秒播报新增涨停、约 1 分钟写一张分钟热度表，"
    "涨停阈值按主板/创业板科创板/北交所/ST 区分，自 2026 年 1 月起工作日连续落盘"
    "（2026-08-21 单日约 64435 行）。二是巨潮业绩预告采集：列表不含摘要，必须下 PDF 抽归母净利润和变动幅度，"
    "PDF 失败再用东财接口兜底，最后做负债/现金/ROE 的价值筛选。"
    "回测侧有一套可脱离行情平台的账户与订单模拟，用来验证进出场而不是只画净值。\n\n"
    "出题不会做成算法题换皮。题从上面这些场景抽：涨停分板块阈值、预告和快报不能合成一条、"
    "过滤规则必须交对照表、分钟因子必须截断时点且涨停买不进。"
    "每道题写清输入字段、输出字段、隐藏测例，以及 Agent 硬编码或偷看未来数据时测试怎么失败。"
    "难度按专业坑标：规则题 easy，point-in-time 和对照回测 medium，多频率对齐+不可成交 hard。\n\n"
    "交付物按平台格式：instruction.md、本地数据包、Dockerfile、test.sh、参考解、难度和耗时。"
    "Linux 上写过启停脚本和定时任务；Docker 按题目依赖写环境，不包装成运维。"
    "质量标准是可复现、可落盘、可回归。证据表和 Skill 全文都在本文件里，不再另附带路径的材料。"
)


def build(out_path: Path) -> Path:
    doc = Document()
    for s in doc.sections:
        s.top_margin = Cm(1.6)
        s.bottom_margin = Cm(1.6)
        s.left_margin = Cm(1.8)
        s.right_margin = Cm(1.8)

    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(t, 0, 3)
    set_run(t.add_run("TalentsAI 机会胜任与能力证明"), 18, bold=True, color=ACCENT)

    s = doc.add_paragraph()
    s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(s, 0, 2)
    set_run(s.add_run("大模型训练专家 ｜ Agentic Coding × 金融领域"), 11, color=MUTED)

    m = doc.add_paragraph()
    m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(m, 0, 8)
    set_run(m.add_run("殷维 ｜ 华中科技大学金融硕士 ｜ yw43@foxmail.com ｜ 15671678098 ｜ 2026-08-23"), 10, color=MUTED)

    body(
        doc,
        "单文件自包含。审核只看这一份即可：下面有可粘贴的申请说明、两条已落地闭环的证据表、"
        "Agent Skill 全文、关键逻辑摘录、四道可验收样题。不另附脚本、表格或本机目录。",
        size=10,
    )

    heading(doc, "一、申请说明（可直接粘贴）")
    body(doc, PASTE, size=10.5)

    heading(doc, "二、已落地的两条闭环")
    subhead(doc, "2.1 盘中热点板块监控")
    bullet(doc, "做什么：交易时段识别全市场涨停，按概念板块统计「谁在炒」。约 3 秒播报新增涨停，约 1 分钟追加一张概念热度表。")
    bullet(doc, "专业规则：主板约 10%、创业板/科创板约 20%、北交所约 30%、ST 约 5%；概念来自本地板块映射表。")
    bullet(doc, "运维：工作日定时启动与收盘停止；用启停脚本，不手工挂进程。")
    bullet(doc, "验收：工作日连续落盘（自约 2026-01）；2026-08-21 单日约 64435 行（分钟 × 概念）。")
    bullet(doc, "表字段：时间、概念板块、涨停数、较上分钟、今日峰值、新增、开板。")

    body(doc, "证据表 A｜2026-08-21 09:25 开盘附近（节选）", size=10)
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
    body(doc, "证据表 B｜同日「储能」连续分钟（节选）", size=10)
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

    subhead(doc, "2.2 巨潮业绩预告采集")
    bullet(doc, "做什么：按日拉「业绩预告」公告，抽出归母净利润（万元）和变动幅度（%），再做价值筛选。")
    bullet(doc, "为什么必须下 PDF：列表接口没有摘要，标题也常常没有增速。")
    bullet(doc, "解析顺序（不能乱）：PDF 主路径 → 东财业绩预告接口兜底 → 仍缺则从标题推断或标类型。")
    bullet(doc, "价值筛选摘要：排除部分板块后，看负债、现金、ROE；要求现金为正、ROE 非负，且 ROE>8% 或较上年改善。")
    bullet(doc, "样本日期：2026-01-26、2026-01-28、2026-07-14。")

    body(doc, "证据表 C｜2026-07-14 业绩预告节选", size=10)
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

    subhead(doc, "2.3 回测与监控习惯（不另附工程目录）")
    bullet(doc, "回测引擎：自管账户（现金、持仓、当日可卖、成交均价）和成交记录，用来模拟下单，而不是只算一条收益率。")
    bullet(doc, "数据：日线/分钟从本地文件读，交易日历和复权因子缓存；不把「现场联网拉数」写进评测题。")
    bullet(doc, "盘中监控：按板块股票池跟踪均线类信号，多周期并行拉 K 线，用于复盘而不是当低频因子库。")
    bullet(doc, "验证方式：对照实验和出场逻辑检查，输出表格字段，而不是只交曲线图。")

    heading(doc, "三、关键逻辑摘录（去路径，只留判定）")
    body(doc, "涨停阈值（按代码前缀区分板块；ST 按证券简称判断，不按代码字符串）：", size=10)
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
        "说明：线上脚本里用过「接近涨停」的 19.5%/9.5% 容差，方便盘中先报警。"
        "出题和验收用整阈值（10/20/30/5），卡在 19.99% 的样本必须判「未涨停」，避免 Agent 用宽松容差蒙混。",
        size=10,
    )
    body(doc, "业绩预告解析优先级（乱序即错）：", size=10)
    bullet(doc, "1. PDF 表格抽取归母净利润、变动幅度。")
    bullet(doc, "2. PDF 失败：东财业绩预告接口补数字，来源记 eastmoney。")
    bullet(doc, "3. 仍缺增速：标题推断或标记预告类型，禁止用 0 填缺失。")
    bullet(doc, "预告与快报并存时保留两行，用类型字段区分，禁止合成一条。日期用公告披露日。")

    heading(doc, "四、Agent Skill 全文（已去掉本机路径）")
    body(
        doc,
        "这两份是我给 Agent 用的说明书：目标、步骤、验收字段写死，所以能稳定复跑。"
        "投递不需要再打开任何 Skill 文件，全文如下。",
        size=10,
    )

    subhead(doc, "4.1 Skill：盘中热点板块监控")
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

    subhead(doc, "4.2 Skill：巨潮净利润采集")
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

    heading(doc, "五、四道样题（可扩成平台任务，材料都在题面里）")
    body(
        doc,
        "对照平台在看的六件事：考察点、输入是否合理、输出能否自动判、测试严不严、Agent 会不会投机、是否真场景。"
        "输入一律用题包内的脱敏文件，不要求联网，不指向任何本机目录。",
        size=10,
    )

    subhead(doc, "样题 1｜A 股涨停判定（easy，20–30 分钟）")
    kv(doc, "场景", "盘中监控的第一步：今天这只票算不算涨停。阈值写错，后面热度表全废。")
    kv(doc, "考察", "按板块选对阈值，输出 0/1。")
    kv(
        doc,
        "instruction 写死",
        "主板 10%；创业板/科创板 20%；北交所 30%；ST/*ST 5%。用当日不复权收盘相对前收，先四舍五入到百分号后两位再比。",
    )
    kv(doc, "输入（写在题包内）", "quotes.csv：code,name,board,is_st,pre_close,close。必须覆盖四类板块和 ST。")
    kv(doc, "输出", "limit_up.csv：code,limit_up，按 code 升序。")
    kv(
        doc,
        "测试",
        "查行数、排序、每类板块至少一个正例和一个负例。隐藏测例 Agent 不可见。创业板 19.99% 必须为 0。",
    )

    subhead(doc, "样题 2｜预告与快报拆开入库（medium，45–70 分钟）")
    kv(doc, "场景", "巨潮采集的真实坑：预告和快报数字不能合成一条；必须用公告日，不能用报告期。")
    kv(doc, "考察", "类型、归母净利、变动幅度、point-in-time。")
    kv(
        doc,
        "instruction 写死",
        "类型只允许 forecast / flash / regular。同一公司同一报告期两条都留。缺失变动幅度写 NA，禁止填 0。announce_date 取披露日。不联网。",
    )
    kv(doc, "输入", "announcements/ 下若干本地文本 + 字段中文别名说明。")
    kv(doc, "输出", "earnings.csv：code,report_period,type,announce_date,net_profit_parent,yoy_change。")
    kv(doc, "测试", "与 golden 逐字段比。故意放「预告数字写在快报标题下」的脏样本。禁止按文件名猜类型。")

    subhead(doc, "样题 3｜位置过滤对照回测（medium，60–90 分钟）")
    kv(doc, "场景", "现任验证过的规则：收盘价/前 20 日最低价 < 1.3，用来去掉已经炒高的票。对照后最大单笔亏损从约 -27% 收到约 -17%。")
    kv(doc, "考察", "规则进回测，必须交对照表。")
    kv(
        doc,
        "instruction 写死",
        "基准组只看放量；实验组再加 close/min(low,20)<1.3。收益用开仓到平仓，不是盯市净值。20 日窗口不含当日，停牌不计入。",
    )
    kv(doc, "输入", "daily_bars 表（code,date,open,high,low,close,volume,tradable）+ signals 表。")
    kv(doc, "输出", "compare.json（两组笔数、胜率、最大单笔亏损）+ trades_filtered.csv。")
    kv(doc, "测试", "过滤后最大单笔亏损应好于基准（亏损为负则数值更大）。只改文案、成交明细不变则失败。")

    subhead(doc, "样题 4｜分钟热度合成日线回测（hard，2–3 小时）")
    kv(doc, "场景", "短线多头：分钟板块强度叠日线量价。坑是未来函数和涨跌停成交不了。")
    kv(doc, "考察", "多频率对齐、时点截断、不可成交、成本。")
    kv(
        doc,
        "instruction 写死",
        "分钟因子 14:30 截断。板块成分用当日可交易名单。信号日涨停则买量为 0；跌停则卖不出、次日再挂。费率写在 config 里。",
    )
    kv(doc, "输入", "分钟行情、日线、板块成分、config。全部在题包内。")
    kv(doc, "输出", "metrics.json、nav.csv、未成交次数审计。")
    kv(doc, "测试", "把 14:45 改成极端值，结果变了就是未来函数。信号日改成涨停，成交必须为 0。禁止联网。")
    body(doc, "不出机器学习选股题，那不是我的工作栈。", size=10)

    heading(doc, "六、平台交付物（仍写在本题包内，不指向外部文件）")
    add_table(
        doc,
        ["文件", "写什么"],
        [
            ["instruction.md", "目标、字段字典、输出 schema、边界、禁止联网和改测试"],
            ["data/", "脱敏输入 + 隐藏测例（Agent 不可见）"],
            ["Dockerfile", "Python + pandas/numpy，按 requirements 安装"],
            ["test.sh", "调用断言；非 0 退出即失败"],
            ["solve.sh", "参考解，证明题可解、测试没写反"],
            ["meta.json", "easy/medium/hard、预估耗时、知识点"],
        ],
    )
    body(
        doc,
        "工程边界：Linux 终端、Bash 启停、定时任务和日志用过；Dockerfile 按题写，不声称长期维护生产镜像。"
        "本机测试习惯是对落盘表做列、行数、关键股票、数值范围断言，正式交付改成平台要求的 pytest。",
        size=10,
    )

    heading(doc, "七、本文用到的全部材料（不再外挂）")
    add_table(
        doc,
        ["材料", "在本文哪里", "说明"],
        [
            ["申请说明", "第一节", "可整段粘贴到申请表"],
            ["涨停热度证据", "表 A、表 B", "2026-08-21 真实落盘节选"],
            ["业绩预告证据", "表 C", "2026-07-14 字段节选"],
            ["涨停判定逻辑", "第三节摘录", "按板块阈值；出题用整阈值"],
            ["预告解析顺序", "第三节条目", "PDF → 东财 → 标题"],
            ["两条 Skill 全文", "第四节", "已去掉目录和启停命令地址"],
            ["四道样题", "第五节", "输入输出和测试都写在题面"],
            ["交付清单", "第六节", "平台文件角色，不是本机路径"],
        ],
    )
    body(
        doc,
        "不附带：本机目录、Skill 原文件、原始 CSV/Excel、未脱敏公告 PDF、个人账户收益、公司内部未公开数据。",
        size=10,
    )

    foot = doc.add_paragraph()
    tight(foot, 12, 0)
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(foot.add_run("仅用于 TalentsAI 申请 ｜ 单文件投递 ｜ 2026年8月"), 9, color=MUTED)

    doc.save(out_path)
    return out_path


if __name__ == "__main__":
    out = Path(__file__).with_name("TalentsAI_AgenticCoding金融_机会胜任与能力证明.docx")
    build(out)
    print(f"✓ {out}")
