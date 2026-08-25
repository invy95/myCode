# 投研公告解析 Agent · LangGraph

> 用 LangGraph 重写的 A 股上市公司业绩预告 / 快报解析管道：**多源采集 → 结构化提取 → 断言校验 → 失败重试 → 落盘**。
>
> 本项目是把已在生产环境跑了数月的巨潮公告采集 Skill，用主流 Agent 编排框架重新实现的版本。业务逻辑与校验口径未变，换的是编排层。

---

## 为什么做这个

原管道以 Cursor Skill（`SKILL.md` + Python 脚本 + cron）的形式运行，工程上是完整的，但用的是「Skill / 落盘断言 / 启停脚本」这套词。招聘市场检索的是「Agent 编排 / 评测集 / 可观测性」。

这个仓库把同一件事翻译成主流框架的表达：`StateGraph` 编排、`@tool` 能力封装、`checkpoint` 断点续跑、`pytest` 回归评测。**做过的事没变，换了个说法。**

---

## 架构

```
                    ┌──────────────┐
       START ─────► │  fetch_pdf   │  巨潮主源 → 东财兜底 → 本地缓存
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │ parse_table  │  正则 + 表格定位，抽净利润/同比/公告日
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │  validate    │  6 条断言：类型/数值/日期/单位/同比一致性
                    └──┬───────┬───┘
                 pass  │       │  fail & retries_left
                       ▼       └──────► fetch_pdf（换源重试，最多 2 次）
                    ┌──────────────┐
                    │   persist    │  CSV 落盘 + 运行日志
                    └──────┬───────┘
                           ▼
                          END
```

条件边由 `route_after_validate` 决定：校验通过走 `persist`；失败且还有重试额度则退回 `fetch_pdf` 换下一个数据源；重试耗尽则标记 `NA` 落盘，不静默丢数据。

---

## 快速开始

```bash
pip install -r requirements.txt

# 跑一支股票（离线 fixture，无需网络与 API Key）
python -m src.run --code 002594 --period 2026Q2

# 跑评测集
pytest -v
```

正常路径输出：

```
[fetch_pdf  ] source=cninfo     ok      0.09ms  334 chars
[parse_table] source=cninfo     ok      0.02ms  6/6 字段命中
[validate   ] source=cninfo     ok      3.47ms  全部通过
[persist    ] source=cninfo     ok      1.07ms  002594_2026Q2.csv

公告类型: 业绩预告
公告日期: 2026-07-14
净利润  : 5224000000.0
同比    : 12.3%
校验    : 通过
```

主源数据不合规时自动换源（`--code 688981`）：

```
[fetch_pdf  ] source=cninfo     ok      0.09ms  227 chars
[parse_table] source=cninfo     ok      0.02ms  6/6 字段命中
[validate   ] source=cninfo     fail    3.40ms  公告类型非法: '投资者关系活动记录'; 公告日期晚于今天: 2029-08-01
[fetch_pdf  ] source=eastmoney  ok      0.09ms  220 chars
[parse_table] source=eastmoney  ok      0.02ms  6/6 字段命中
[validate   ] source=eastmoney  ok      0.03ms  全部通过
[persist    ] source=eastmoney  ok      1.24ms  688981_2026Q2.csv
```

全部数据源都没有时，落盘 `NA` 记录而不是抛异常中断批量任务（`--code 999999`）。

---

## 目录结构

| 路径 | 说明 |
|------|------|
| `src/graph.py` | LangGraph 主图：节点注册、条件边、checkpoint |
| `src/state.py` | `AgentState` 定义（TypedDict） |
| `src/tools/fetch.py` | 多源采集工具（主源 + 兜底 + 缓存） |
| `src/tools/parse.py` | 公告文本结构化提取 |
| `src/tools/validate.py` | 6 条断言校验 |
| `src/tools/persist.py` | CSV 落盘与运行日志 |
| `src/run.py` | CLI 入口 |
| `tests/test_eval.py` | 回归评测集（5 条用例） |
| `data/fixtures/` | 脱敏公告样本，供离线跑通 |

---

## 校验规则（`validate` 节点）

| # | 断言 | 失败处理 |
|---|------|----------|
| 1 | 公告类型 ∈ {预告, 快报, 正式报告} | 换源重试 |
| 2 | 净利润为数值且非空 | 换源重试 |
| 3 | 公告日期格式 `YYYY-MM-DD` 且不晚于今天 | 换源重试 |
| 4 | 单位已归一到元（识别「万元/亿元」） | 就地修正 |
| 5 | 同比增速与上年同期数值自洽（容差 0.5pp） | 标记 `warn`，仍落盘 |
| 6 | 缺失字段一律写 `NA`，不写 0 | 就地修正 |

第 5、6 条是从实盘踩坑来的：早期把缺失值写成 0，导致下游筛选把「没披露」和「亏损」混成一类。

---

## 可观测性

- 每个节点向 `state["trace"]` 追加一条记录（节点名、耗时、数据源、结果）
- `MemorySaver` checkpoint 支持断点续跑：同一 `thread_id` 重跑时跳过已完成节点
- `data/out/run.log` 落盘完整 trace，便于事后复盘

---

## 评测集

`tests/test_eval.py` 覆盖 7 类场景，对应生产环境中真实出现过的情况：

| 用例 | 场景 | 期望 |
|------|------|------|
| `test_normal_forecast` | 正常业绩预告 | 6/6 断言通过，落盘成功 |
| `test_unit_conversion` | 金额单位为「万元」 | 归一到元，数值正确 |
| `test_missing_field_writes_na` | 同比字段缺失 | 写 `NA` 而非 0 |
| `test_fallback_source` | 主源无此公告 | 自动切兜底源并成功 |
| `test_retry_on_invalid_then_success` | 主源数据不合规 | 换源重试后拿到合规版本 |
| `test_retry_exhausted_writes_na` | 全部源失败 | 重试耗尽后标记 `NA`，不抛异常 |
| `test_yoy_inconsistency_warns_not_blocks` | 同比与两期净利不自洽 | 仅告警，不阻断落盘 |

```
$ pytest -v
tests/test_eval.py::test_normal_forecast                   PASSED [ 14%]
tests/test_eval.py::test_unit_conversion                   PASSED [ 28%]
tests/test_eval.py::test_missing_field_writes_na           PASSED [ 42%]
tests/test_eval.py::test_fallback_source                   PASSED [ 57%]
tests/test_eval.py::test_retry_on_invalid_then_success     PASSED [ 71%]
tests/test_eval.py::test_retry_exhausted_writes_na         PASSED [ 85%]
tests/test_eval.py::test_yoy_inconsistency_warns_not_blocks PASSED [100%]
============================== 7 passed in 0.24s ===============================
```

---

## 与岗位要求的能力映射

| JD 要求（天弘 / 华创 / 国信 / TOP 交易所） | 本项目对应实现 |
|---|---|
| Agent 框架（LangGraph / LangChain） | `StateGraph` 编排 + 条件边路由 |
| Skills / 工具调用（Tool Use） | `@tool` 封装 4 个能力模块，可独立复用 |
| 任务编排与上下文管理 | `AgentState` 显式状态传递，节点间无隐式耦合 |
| 多源召回与降级策略 | 主源 → 兜底源 → 缓存三级 fallback |
| 非结构化数据解析 | PDF / HTML 公告文本抽取 |
| 评测集 / Benchmark / 回归测试 | `pytest` 5 条用例，覆盖正常与异常路径 |
| 可观测与回放 | `trace` 记录 + checkpoint 断点续跑 + 运行日志 |
| 幻觉控制 / 准确性保障 | 6 条硬断言，宁可标 `NA` 不可编数 |
| 生产级稳定性 | 重试上限、异常兜底、失败不中断批量任务 |

---

## 诚实边界

- 本仓库是**编排层的重写**，业务逻辑与校验口径来自已运行数月的原管道
- 离线 fixture 为脱敏样本，真实数据源接入需配置网络与凭据
- 未使用 LLM 做抽取（规则解析在这个场景准确率更高、成本更低）；`parse` 节点预留了 LLM 接口位，便于后续对比

---

## 依赖

见 `requirements.txt`。核心依赖只有 `langgraph`，解析层用标准库，无重型依赖。
