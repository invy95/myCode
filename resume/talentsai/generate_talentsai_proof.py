#!/usr/bin/env python3
# 功能：把 TalentsAI Agentic Coding×金融 申请材料渲染成可投递 docx。
# 更新 2026-08-23：出题部分改为 4 道可验收样题（场景、I/O、测试、防投机、难度），不再只堆格式名词。

"""Render the TalentsAI application pack from structured markdown-like sections."""

from pathlib import Path

from docx import Document
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
    p.paragraph_format.line_spacing = 1.15


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
    p.paragraph_format.left_indent = Cm(0.5)
    set_run(p.add_run("• " + text), size)


def kv(doc, label, text):
    p = doc.add_paragraph()
    tight(p, 1, 2)
    p.paragraph_format.left_indent = Cm(0.4)
    set_run(p.add_run(label + "："), 11, bold=True)
    set_run(p.add_run(text), 11)


def build(out_path: Path) -> Path:
    doc = Document()
    for s in doc.sections:
        s.top_margin = Cm(1.8)
        s.bottom_margin = Cm(1.8)
        s.left_margin = Cm(2.0)
        s.right_margin = Cm(2.0)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(title, 0, 4)
    set_run(title.add_run("TalentsAI 机会胜任与能力证明"), 18, bold=True, color=ACCENT)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(sub, 0, 8)
    set_run(sub.add_run("大模型训练专家 ｜ Agentic Coding × 金融领域（J83）"), 11, color=MUTED)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tight(meta, 0, 10)
    set_run(meta.add_run("殷维 ｜ 华中科技大学金融硕士 ｜ yw43@foxmail.com ｜ 15671678098"), 10, color=MUTED)

    heading(doc, "一、一句话：我能交出什么样的题")
    body(
        doc,
        "这个岗要的不是再写一套回测曲线，而是把真实投研问题拆成 Agent 在 Docker/终端里能做完、脚本能判对错的任务。"
        "我日常就是在做这件事的前半段：把「自然语言任务 → Python/Bash 实现 → 落盘结果 → 用规则验收」跑通。"
        "下面四道样题都来自我自己做过的活，不是算法竞赛题改写。",
    )

    heading(doc, "二、出题原则（对照平台在看的六件事）")
    bullet(doc, "考察什么：每题只考 1–2 个专业判断，不把清洗、回测、可视化堆进同一题。")
    bullet(doc, "输入是否合理：用脱敏、固定种子的本地文件，不要求 Agent 现场爬网，避免评测不稳定。")
    bullet(doc, "输出是否可验证：规定文件名、字段、排序、小数位；能对 golden 文件或数值容差做断言。")
    bullet(doc, "测试是否严谨：test.sh / pytest 同时查「结果对」和「过程没抄捷径」。")
    bullet(doc, "会不会投机：隐藏用例、打乱股票顺序、禁止硬编码答案表；只改输出文件名过不了。")
    bullet(doc, "是否贴近真实场景：用 A 股真实规则（涨停分板块、预告≠快报、停牌买不进），不用通用排序题换皮。")

    heading(doc, "三、四道样题（可直接扩成 instruction.md + test.sh + solve.sh）")
    body(
        doc,
        "每道题下面按「场景 / 给 Agent 的约束 / 输入输出 / 测试与防投机 / 难度」写。正式交付时再拆成独立文件；这里先证明我知道题该长什么样。",
    )

    subhead(doc, "样题 1｜A 股涨停判定（easy，约 20–30 分钟）")
    kv(doc, "场景来源", "盘中涨停监控里每天都要先判定「今天这只票算不算涨停」。规则按板块不同，写错阈值整条链路废掉。")
    kv(doc, "考察点", "读懂 A 股交易规则，按证券代码/名称/板块字段选对阈值，输出布尔结果。")
    kv(
        doc,
        "instruction 必须写清",
        "主板/中小板 10%；创业板、科创板 20%；北交所 30%；ST/*ST 5%。比较用「当日涨跌幅是否达到该阈值」，复权口径写死为不复权收盘价相对前收。四舍五入到百分号后两位后再比。",
    )
    kv(doc, "输入", "quotes.csv：code, name, board, is_st, pre_close, close。至少含上述四类板块和 ST 样本。")
    kv(doc, "输出", "limit_up.csv：code, limit_up(0/1)，按 code 升序。")
    kv(
        doc,
        "测试与防投机",
        "断言行数、排序、每类板块至少 1 个正例和 1 个负例。另给隐藏文件 quotes_hidden.csv，Agent 看不到答案。卡在阈值上的票（如创业板刚好 19.99%）必须判 0，防止 Agent 用「涨幅>9.5 就算涨停」蒙混。",
    )
    kv(doc, "难度标注", "easy。专业坑在规则，代码量不大。")

    subhead(doc, "样题 2｜业绩预告与快报拆开入库（medium，约 45–70 分钟）")
    kv(doc, "场景来源", "我做过全市场财报/预告采集。预告和快报数字不能混；公告时间戳错了就会把未来信息写进当天股票池。")
    kv(doc, "考察点", "区分公告类型；抽取归母净利润及变动幅度；用公告日而不是报告期做 point-in-time。")
    kv(
        doc,
        "instruction 必须写清",
        "输入是公告列表（已下载的本地 HTML/文本，不爬外网）。类型只允许 forecast / flash / regular 三值。同一公司同一报告期同时有预告和快报时，两条都保留，用 type 区分，禁止合成一条。变动幅度缺省写 NA，禁止用 0 填。announce_date 取披露日。",
    )
    kv(doc, "输入", "announcements/ 下若干文本；schema.md 说明字段中文别名（归属于母公司股东的净利润 / 净利润同比）。")
    kv(doc, "输出", "earnings.csv：code, report_period, type, announce_date, net_profit_parent, yoy_change。")
    kv(
        doc,
        "测试与防投机",
        "golden 表逐字段比对；故意放「预告数字写在快报标题下」的脏样本，混用类型即失败。隐藏 2 篇非常规标题。禁止 Agent 只按文件名猜类型。",
    )
    kv(doc, "难度标注", "medium。坑在中文财务表述和 point-in-time，不在正则炫技。")

    subhead(doc, "样题 3｜强势股位置过滤 + 对照回测（medium，约 60–90 分钟）")
    kv(doc, "场景来源", "现任岗位验证过的规则：收盘价/前 20 日最低价 < 130%，用来去掉已经炒高的票，对照后最大单笔亏损从约 -27% 收到约 -17%。")
    kv(doc, "考察点", "把一条可执行的过滤规则写进回测，并输出对照表，而不是只交一条净值。")
    kv(
        doc,
        "instruction 必须写清",
        "基准组：满足放量条件即买入。实验组：再加 close / min(low, 20) < 1.3。收益用开仓到平仓的区间收益，不是盯市净值。必须输出两组的交易笔数、胜率、最大单笔亏损。20 日窗口不含当日。停牌日不计入窗口。",
    )
    kv(doc, "输入", "daily_bars.parquet：code, date, open, high, low, close, volume, tradable。信号日列表 signals.csv。")
    kv(doc, "输出", "compare.json：baseline 与 filtered 两组指标；trades_filtered.csv 便于抽查。")
    kv(
        doc,
        "测试与防投机",
        "用我算过的脱敏子集做 golden。断言 filtered.max_single_loss > baseline.max_single_loss（亏损是负数，过滤后应更大，即亏得更少）。若 Agent 只改了输出文案、没改成交明细，trades 对不上则失败。禁止读取任何「标准答案收益」文件。",
    )
    kv(doc, "难度标注", "medium。考的是规则定义和对照实验，不考组合优化器。")

    subhead(doc, "样题 4｜分钟板块热度合成日线回测（hard，约 2–3 小时）")
    kv(doc, "场景来源", "掘金短线多头：分钟级板块强度/拥挤度叠日线量价。真实坑是未来函数、涨跌停买不进、停牌缺 bar。")
    kv(doc, "考察点", "多频率对齐、信号时点只用当时已发生的分钟、回测扣交易成本并处理不可成交。")
    kv(
        doc,
        "instruction 必须写清",
        "分钟因子在 14:30 截断，不得使用 14:30 之后的 bar。板块成分用当日开盘可交易名单，不得用收盘后才公布的成分。买入若信号日涨停则成交量为 0。卖出若跌停则次日继续挂。成本：双边佣金+印花税，费率写死在 config.yaml。输出日收益、最大回撤、换手，以及 future_function_check=pass。",
    )
    kv(doc, "输入", "minute_bars/、daily_bars/、board_members.csv、config.yaml。全部本地文件。")
    kv(doc, "输出", "metrics.json；nav.csv；audit.log（记录每笔因涨跌停未成交的次数）。")
    kv(
        doc,
        "测试与防投机",
        "1）把某日 14:45 的分钟值改成极端数，若结果跟着变，判定用了未来函数。2）把信号日收盘改成涨停，成交必须为 0。3）metrics 与 golden 相对误差 < 1e-6。4）禁止联网。",
    )
    kv(doc, "难度标注", "hard。专业深度在约束，不在模型花哨。我不会出 sklearn/xgboost 选股题，那不是我的工作栈。")

    heading(doc, "四、一套题的交付清单（我对齐平台格式）")
    bullet(doc, "instruction.md：目标、数据字典、输出 schema、边界、禁止事项（不联网、不改测试）。")
    bullet(doc, "data/：脱敏输入 + 隐藏测例（不进 Agent 可见目录）。")
    bullet(doc, "Dockerfile：python:3.11-slim + pandas/numpy；能 pip install -r requirements.txt。")
    bullet(doc, "test.sh：调用 pytest，非 0 退出即失败。")
    bullet(doc, "solve.sh：我自己的参考解，用来证明题可解、测试没写反。")
    bullet(doc, "meta.json：easy/medium/hard、预估耗时、考察知识点（涨停规则 / point-in-time / 对照回测 / 未来函数）。")
    body(
        doc,
        "工程能力边界：Linux 上部署过投研脚本、定时任务和日志，能写 Bash 启停；Dockerfile 按任务依赖写，不包装成「长期维护过生产镜像」。测试习惯是断言+落盘对照，正式交付按平台要求改成 pytest。",
    )

    heading(doc, "五、机会胜任原因（可直接粘贴到申请表）")
    body(doc, _paste_reason())

    heading(doc, "六、证明材料建议")
    bullet(doc, "本文件：出题样例 + 胜任原因。")
    bullet(doc, "脱敏回测/对照表 PDF（样题 3 的真实出处）。")
    bullet(doc, "Linux 定时任务或脚本目录截图（证明能在终端闭环）。")
    bullet(doc, "学历与工作履历：华中科技大学金融硕士；量化研究相关工作自 2021 年起。")
    body(doc, "不附带公司内部未脱敏数据、客户信息或未公开业绩。个人账户收益不作为证明。", size=10)

    footer = doc.add_paragraph()
    tight(footer, 14, 0)
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(footer.add_run("仅用于 TalentsAI J83 申请 ｜ 2026年8月"), 9, color=MUTED)

    doc.save(out_path)
    return out_path


def _paste_reason() -> str:
    return (
        "机会：大模型训练专家 | Agentic Coding × 金融领域\n\n"
        "我做了几年 A 股量化研究和工程落地，日常就是把一个投研问题写成能跑、能对的东西："
        "先写清要算什么，再用 Python/Bash 做出来，最后用文件和规则验收。这和本岗位要的"
        "「在 Docker/终端里按 instruction 完成金融编程任务，并用脚本判定通过/失败」是同一条链路。\n\n"
        "出题上，我不会出成算法题换皮。题从自己做过的场景里抽：A 股涨停要按主板/创业板科创板/北交所/ST 分阈值；"
        "业绩预告和快报不能合成一条，日期必须用公告日；短线回测要写清过滤规则，并输出对照表而不是一条曲线；"
        "分钟因子必须截断时点，涨停买不进、跌停卖不出。每道题我会写明输入文件、输出字段、隐藏测例，以及 Agent 想硬编码或偷看未来数据时怎么让测试失败。"
        "难度按专业坑来标：规则题标 easy，point-in-time 和对照回测标 medium，多频率对齐+不可成交标 hard。\n\n"
        "交付物按平台格式准备：instruction.md、本地数据包、Dockerfile、test.sh/pytest、solve.sh、难度和耗时。"
        "Linux 终端、定时任务和日志我在现岗用过；Docker 按任务写环境即可，不把自己说成运维。\n\n"
        "质量上我认「可复现、可落盘、可回归」：本机有连续多月的涨停概念分钟表和多日业绩预告表，足够拿来做 golden。"
        "愿意按平台质检标准稳定交金融 Agentic Coding 题。"
    )


if __name__ == "__main__":
    out = Path(__file__).with_name("TalentsAI_AgenticCoding金融_机会胜任与能力证明.docx")
    build(out)
    print(f"✓ {out}")
