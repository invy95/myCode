#!/usr/bin/env python3
"""
殷维决策器：按十二维和红线，快速判断一个工作/项目/内容该不该接。
更新：2026-09-12：初版交互（剖面、打分、对比、本周投稿任务）。
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

WEIGHTS = {
    "评价对象": 1.4,
    "反馈方差": 1.0,
    "挑战类型": 1.4,
    "人际质量": 1.4,
    "真实性": 1.4,
    "作品性": 1.2,
    "传递性": 1.2,
    "组织复杂度": 1.0,
    "节律": 1.0,
    "能量匹配": 1.2,
    "养活": 1.0,
    "做完还想": 1.2,
}

DIM_HELP = {
    "评价对象": "0=评人  1=混合  2=评交付物",
    "反馈方差": "0=随机（净值/日榜）  1=中  2=做了就有、能归因",
    "挑战类型": "0=结果型  1=混合  2=过程型（努力就有）",
    "人际质量": "0=持续权力评价  1=中  2=一次性/无打压",
    "真实性": "0=必须演  1=偶尔  2=不演",
    "作品性": "0=无署名  1=半作品  2=可留下、能看出是你做的",
    "传递性": "0=不给别人  1=间接  2=把你懂的交出去",
    "组织复杂度": "0=重2B流程  1=中  2=对人、边界清",
    "节律": "0=拉长消耗  1=中  2=紧凑可停",
    "能量匹配": "0=高唤醒表演  1=中  2=低唤醒卸防",
    "养活": "0=透支  1=不稳但有  2=能养1–6个月底层",
    "做完还想": "0=纯逃离  1=模糊  2=做完还想继续",
}

RED_LINES = [
    "持续打压/否定/要你演",
    "主KPI是净值或日榜排名",
    "24小时陪伴或一对一长期疗愈当主业",
    "进门就考现场表演",
    "用别人的对话录音训练模型",
]


@dataclass
class Option:
    name: str
    layer: str
    scores: dict[str, int]
    red: bool
    note: str


PRESETS: list[Option] = [
    Option(
        "当前AI投研-搭建工作流/知识库/推送",
        "底层",
        {
            "评价对象": 1, "反馈方差": 2, "挑战类型": 2, "人际质量": 1,
            "真实性": 1, "作品性": 1, "传递性": 2, "组织复杂度": 1,
            "节律": 1, "能量匹配": 2, "养活": 2, "做完还想": 2,
        },
        False,
        "只接过程型搭建。任务漂到量化结果考核就变红。",
    ),
    Option(
        "金融专家标注/远程小单",
        "底层",
        {
            "评价对象": 2, "反馈方差": 2, "挑战类型": 2, "人际质量": 2,
            "真实性": 2, "作品性": 1, "传递性": 1, "组织复杂度": 2,
            "节律": 2, "能量匹配": 1, "养活": 1, "做完还想": 1,
        },
        False,
        "最干净的过渡底层。不当身份，当缓冲。",
    ),
    Option(
        "客服机器人训练",
        "底层",
        {
            "评价对象": 2, "反馈方差": 2, "挑战类型": 2, "人际质量": 1,
            "真实性": 1, "作品性": 1, "传递性": 1, "组织复杂度": 0,
            "节律": 1, "能量匹配": 1, "养活": 1, "做完还想": 0,
        },
        False,
        "能做、费力、偏2B。可当短项目，不当「我是做这个的」。",
    ),
    Option(
        "投研AI搭建外包（熟人，有边界）",
        "底层",
        {
            "评价对象": 2, "反馈方差": 2, "挑战类型": 2, "人际质量": 2,
            "真实性": 2, "作品性": 2, "传递性": 2, "组织复杂度": 1,
            "节律": 2, "能量匹配": 2, "养活": 1, "做完还想": 2,
        },
        False,
        "赋能者正职。先有一页交付说明再找熟人。",
    ),
    Option(
        "企业AI咨询/对公客户",
        "错层",
        {
            "评价对象": 0, "反馈方差": 1, "挑战类型": 1, "人际质量": 0,
            "真实性": 0, "作品性": 1, "传递性": 1, "组织复杂度": 0,
            "节律": 0, "能量匹配": 0, "养活": 2, "做完还想": 0,
        },
        False,
        "钱可能更好跑，规格书红。默认不接。",
    ),
    Option(
        "2C内容：迷失→自学AI→一种可能",
        "中层",
        {
            "评价对象": 2, "反馈方差": 1, "挑战类型": 2, "人际质量": 2,
            "真实性": 2, "作品性": 2, "传递性": 2, "组织复杂度": 2,
            "节律": 2, "能量匹配": 2, "养活": 0, "做完还想": 2,
        },
        False,
        "主表达。不保证别人就业。前半年不指望它养家。",
    ),
    Option(
        "段子/写成歌",
        "中层出口",
        {
            "评价对象": 2, "反馈方差": 0, "挑战类型": 2, "人际质量": 2,
            "真实性": 2, "作品性": 2, "传递性": 1, "组织复杂度": 2,
            "节律": 2, "能量匹配": 2, "养活": 0, "做完还想": 2,
        },
        False,
        "出口，先发布。变现是以后的事。",
    ),
    Option(
        "陪伴机器人/一对一长期疗愈",
        "错层",
        {
            "评价对象": 0, "反馈方差": 1, "挑战类型": 1, "人际质量": 0,
            "真实性": 1, "作品性": 0, "传递性": 1, "组织复杂度": 1,
            "节律": 0, "能量匹配": 0, "养活": 1, "做完还想": 0,
        },
        True,
        "把卸防做成24小时接待。否决当主业。",
    ),
]


def weighted_score(scores: dict[str, int]) -> float:
    total = 0.0
    wsum = 0.0
    for k, w in WEIGHTS.items():
        total += scores[k] * w
        wsum += 2 * w
    return round(10 * total / wsum, 2)


def verdict(score: float, red: bool) -> str:
    if red:
        return "否决"
    if score >= 8.5:
        return "可接/可进主线"
    if score >= 6.5:
        return "条件接"
    return "不接"


def print_option(opt: Option) -> None:
    s = weighted_score(opt.scores)
    v = verdict(s, opt.red)
    print(f"\n【{opt.name}】")
    print(f"层：{opt.layer}    分：{s}/10    结论：{v}")
    print(f"注：{opt.note}")
    lows = [k for k, val in opt.scores.items() if val == 0]
    if lows:
        print("低分维：" + "、".join(lows))


def cmd_profile() -> None:
    print(
        """
殷维 · 底层不是工具清单
  传递/翻译 · 卸防 · 异步深度 · 结构化提问
  理念关联 · 过程型赋能 · 金融母语 · 自我观察

选工作看：评价落在东西上、过程型、不演、低打压、紧凑、能留下作品。
2B企业默认过重。2C作品是中层。底层只负责钱和节律。

红线：打压/要演、净值或日榜当主KPI、一对一长期陪伴当主业、
      现场表演考场、偷录别人训练模型、没落点就走（除非踩红线）。
""".strip()
    )


def cmd_demo() -> None:
    print("预置选项（可当对照表，也可改分后再判）：")
    rows = []
    for opt in PRESETS:
        s = weighted_score(opt.scores)
        rows.append((s, opt))
    rows.sort(key=lambda x: (-1 if x[1].red else x[0]), reverse=True)
    # show vetoes last
    ok = [(s, o) for s, o in rows if not o.red]
    bad = [(s, o) for s, o in rows if o.red]
    ok.sort(key=lambda x: x[0], reverse=True)
    for s, o in ok + bad:
        flag = "否" if o.red else verdict(s, False)[:2]
        print(f"  {s:4.1f}  {flag:8}  [{o.layer}] {o.name}")
    print("\n细看用：python3 decide.py demo --name 关键词")


def cmd_demo_one(name: str) -> None:
    hits = [o for o in PRESETS if name in o.name]
    if not hits:
        print("没有匹配的预置，先看：python3 decide.py demo")
        return
    for o in hits:
        print_option(o)


def ask_int(label: str, hint: str) -> int:
    while True:
        raw = input(f"{label}（{hint}）> ").strip()
        if raw in {"0", "1", "2"}:
            return int(raw)
        print("请输入 0 / 1 / 2")


def ask_yes(label: str) -> bool:
    raw = input(f"{label}（y/n）> ").strip().lower()
    return raw in {"y", "yes", "是"}


def collect_scores() -> tuple[str, dict[str, int], bool]:
    name = input("这个选项叫什么？> ").strip() or "未命名"
    print("红线（有一条就否决）：")
    red = False
    for line in RED_LINES:
        if ask_yes("是否存在：" + line):
            red = True
    print("十二维，只打 0/1/2：")
    scores = {}
    for k in WEIGHTS:
        scores[k] = ask_int(k, DIM_HELP[k])
    return name, scores, red


def cmd_score() -> None:
    name, scores, red = collect_scores()
    opt = Option(name, "待定", scores, red, "现场打分")
    print_option(opt)
    v = verdict(weighted_score(scores), red)
    if v == "条件接":
        print("写下再接的条件（建议）：任务不漂、不评人、有退出日、交付物有你的名字。")
    if v == "不接":
        print("给一个落点：回到标注/搭建短项目，或只做中层投稿，不要空着走。")
    if v == "否决":
        print("这是红线，不解释、不忍耐。先离开评价源。")


def cmd_compare() -> None:
    print("选项 A")
    a_name, a_s, a_r = collect_scores()
    print("选项 B")
    b_name, b_s, b_r = collect_scores()
    a = Option(a_name, "对比", a_s, a_r, "")
    b = Option(b_name, "对比", b_s, b_r, "")
    print_option(a)
    print_option(b)
    ascore, bscore = weighted_score(a_s), weighted_score(b_s)
    if a_r and not b_r:
        print(f"\n选 {b_name}。A 触红线。")
    elif b_r and not a_r:
        print(f"\n选 {a_name}。B 触红线。")
    elif a_r and b_r:
        print("\n两个都触红线，都不要。回到预置里的底层干净项。")
    elif ascore >= bscore:
        print(f"\n选 {a_name}（{ascore} > {bscore}）。")
    else:
        print(f"\n选 {b_name}（{bscore} > {ascore}）。")


def cmd_path() -> None:
    print(
        """
本周最小执行（作家投稿式，不是职业规划）

底层（养活，选 1 件）
  - 把正在看的活丢进：python3 decide.py score
  - 或接一单标注 / 写一页「AI工作台+知识库」交付说明

中层（作品，必须 1 件，7 天内发出）
  - 一条：我有几个月不知道能做什么；自学 AI 后找到一种可能
  - 或一段脱敏故事（/novelist）
  - 或把一条段子哼成 30 秒，先发，不问卖不卖得掉

禁止本周做
  - 企业咨询方案、陪伴机器人、保证别人就业的教程
  - 为「别人会不会看我不上班」再开一场内心法庭

验收
  - 发出去 1 个作品
  - 对 1 个外来机会打过分
  - 没有在红线环境里加时
""".strip()
    )


def cmd_json() -> None:
    payload = []
    for o in PRESETS:
        payload.append(
            {
                "name": o.name,
                "layer": o.layer,
                "score": weighted_score(o.scores),
                "verdict": verdict(weighted_score(o.scores), o.red),
                "red": o.red,
                "note": o.note,
                "scores": o.scores,
            }
        )
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    print()


def main() -> None:
    p = argparse.ArgumentParser(description="殷维决策器")
    p.add_argument(
        "cmd",
        nargs="?",
        default="demo",
        choices=["demo", "score", "compare", "path", "profile", "json"],
    )
    p.add_argument("--name", default="", help="demo 时按名称过滤")
    args = p.parse_args()
    if args.cmd == "demo" and args.name:
        cmd_demo_one(args.name)
    elif args.cmd == "demo":
        cmd_demo()
    elif args.cmd == "score":
        cmd_score()
    elif args.cmd == "compare":
        cmd_compare()
    elif args.cmd == "path":
        cmd_path()
    elif args.cmd == "profile":
        cmd_profile()
    elif args.cmd == "json":
        cmd_json()


if __name__ == "__main__":
    main()
