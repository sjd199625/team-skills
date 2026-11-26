# team-skills

一组可跨 Agent 复用的通用技能。格式遵循 [Agent Skills](https://agentskills.io/specification)：每个技能是一个目录，至少包含一个 `SKILL.md`。

## 已包含

| 技能 | 用途 |
| --- | --- |
| `change-summary` | 根据真实代码差异生成 PR 描述、提交说明或交接摘要 |

## 在 Codex / VS Code Copilot 中使用

用 Codex 或 VS Code Copilot 打开本目录即可。它们会扫描项目内的 `.agents/skills/`。

## 在 Claude Code 中使用

Claude Code 默认读取 `.claude/skills/`。在项目根目录执行：

```bash
mkdir -p .claude/skills
ln -s ../../.agents/skills/change-summary .claude/skills/change-summary
```

Windows 可使用目录联接，或直接复制目录。

## 在其他项目中使用

复制 `change-summary` 目录到目标项目的 `.agents/skills/`，或放到用户级目录 `~/.agents/skills/`，即可在所有项目中使用。

## 给其他 Agent 或大模型使用

让 Agent 读取 `change-summary/SKILL.md`，或把正文加入系统提示/项目规则。自动发现、读取附件和执行脚本的能力取决于具体宿主。

## 新增技能

1. 在 `.agents/skills/` 下新建目录，目录名使用小写字母、数字和连字符。
2. 创建 `SKILL.md`，写入 `name`、`description` 和正文。
3. 让 `name` 与目录名一致。

GitHub 负责分发；安装或加载仍由各个 Agent 完成。
