# 本地 Agent Skills

本仓库的 Cursor skills 放在 `.cursor/skills/`。在对话里输入 `/qimen-dunjia` 或 `/novelist` 即可调用。

| Skill | 用途 |
| --- | --- |
| `qimen-dunjia` | 奇门遁甲排盘 / 解盘。排盘必须跑脚本，不要让模型心算。 |
| `novelist` | 角色小说家。把经历写成低唤醒、有判断的故事，不当人生教练。 |

## 奇门

来源：`tradecatlabs/fatecat` 内嵌的 `Numerologist_skills-main/qimen-dunjia`。

依赖：

```bash
pip install "lunar_python>=1.4.8,<2" "tzdata>=2024.1"
```

正式排盘前先访谈（看什么事、哪一刻、在哪、想判断什么），再调用 `qimen-dunjia/scripts/qimen_cli.py`。

## 小说家

适合把「不知道能做什么」「被职场打折」「被人倾诉」写成故事。公开内容必须脱敏。
