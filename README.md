# team-skills

一组可跨 Agent 复用的通用技能。格式遵循 [Agent Skills](https://agentskills.io/specification)：每个技能是一个目录，至少包含一个 `SKILL.md`。

## 已包含

| 技能 | 用途 |
| --- | --- |
| `change-summary` | 根据真实代码差异生成 PR 描述、提交说明或交接摘要 |
| `frontend-workflow` | 移动 H5、PC 后台与 SSR 页面的端到端编排：一份技术设计、一份测试用例与结果、可选后端文档 |
| `frontend-requirement-design` | 读取飞书需求，生成一份前端技术设计 |
| `frontend-page-delivery` | 按技术设计实现移动 H5、PC 后台或 SSR 服务端页面 |
| `frontend-e2e-delivery` | 生成页面测试用例，执行浏览器验收或 Playwright 回归，输出用例与结果 |
| `frontend-api-integration` | 读取接口文档/后端分支，生成可选的接口契约、后端业务与数据来源文档并接入前端 |
| `frontend-conventions` | 移动 H5、PC 后台和 SSR 服务端的页面、组件、接口、路由和样式约定 |

`frontend-conventions` 按角色分文件记录约定。修改哪类前端，就只读对应的 reference；不要把移动 H5、PC 后台和 SSR 的写法混用。

`frontend-workflow` 是端到端入口，其余四个专用技能可以按阶段单独调用。默认只维护 `01-frontend-tech-design.md`、`02-test-cases-results.md` 和可选的 `03-backend-business.md`。

飞书需求固定用 `lark-cli docs +fetch` 读取，并保存到 `docs/<feature>/sources/`；CLI 登录态过期时先重新授权，不用浏览器抓取代替。

日常开发默认走快车道：优先读 `.agents/skills/frontend-workflow/references/project-profile.local.md`，不存在时读模板 `project-profile.md`；再读本次技术文档增量，只维护 `01-frontend-tech-design.md`、`02-test-cases-results.md`，需要时再加 `03-backend-business.md`。详见 `.agents/skills/frontend-workflow/references/fast-lane.md`。

项目画像只提交通用模板；真实仓库路径、测试地址和测试数据放在本地的 `project-profile.local.md`，该文件已被忽略。

不需要记 skill 名称。直接按目标提问即可，例如：

- `读这个飞书需求，只生成前端技术文档`
- `按这份技术文档把这个页面开发出来`
- `页面做完了，生成 case 并真实执行测试`
- `读取这个后端分支，梳理接口和业务数据来源`
- `按项目现有写法修改这个页面`

支持自动发现该目录的宿主会根据任务描述选择对应 skill；不同宿主的加载方式可能不同，只有想强制指定时才需要提 skill 名称。

## 工作流脚本

在目标前端仓库执行初始化和检查；同一需求同时改 H5 和 PC 时，额外传 `--frontend-pc`：

```bash
python3 .agents/skills/frontend-workflow/scripts/feature_docs.py init \
  --repo <h5-repo> --feature <feature> --frontend-pc <pc-repo>

python3 .agents/skills/frontend-workflow/scripts/feature_docs.py check \
  --repo <h5-repo> --feature <feature>

python3 .agents/skills/frontend-workflow/scripts/feature_docs.py gate \
  --repo <h5-repo> --feature <feature> --phase delivery
```

`check` 校验产物和 H5/PC 分支记录，`gate` 校验当前阶段的确认门禁；两者都不能替代真实构建和页面测试。

发布本地 Markdown 到飞书：

```bash
python3 .agents/skills/frontend-workflow/scripts/publish_feishu.py \
  --title '<标题>' --content docs/<feature>/01-frontend-tech-design.md \
  --parent-token '<folder-token>' --dry-run
```

确认后去掉 `--dry-run`，加 `--confirm`。已有文档用 `--doc '<url>' --command append` 追加，不要默认覆盖。

联调时记录 H5、PC、后端三方分支：

```bash
python3 .agents/skills/frontend-api-integration/scripts/record_branches.py \
  --frontend <h5-repo> --frontend-pc <pc-repo> \
  --backend <backend-repo> --require-backend \
  --out docs/<feature>/03-backend-business.md --append
```

这些脚本只做确定性操作，不会自动安装依赖、执行构建或修改业务代码。

## 运行测试

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖 `feature_docs.py` 的状态、门禁和占位符检查，以及 `project_context.py` 的本地画像优先逻辑。它不能替代目标项目的构建和页面测试；GitHub Actions 会在 push 和 pull request 时自动运行。

## 用 npx 安装

需要 Node.js >= 22.20。

```bash
npx skills add sjd199625/team-skills -g --skill change-summary
```

安装前端约定：

```bash
npx skills add sjd199625/team-skills -g --skill frontend-conventions
```

安装端到端入口：

```bash
npx skills add sjd199625/team-skills -g --skill frontend-workflow
```

按阶段使用时再安装对应的 `frontend-requirement-design`、`frontend-page-delivery`、`frontend-e2e-delivery`、`frontend-api-integration`。端到端入口不能替代这些专用 skill 的详细规则。

部分技能带 Python 3 辅助脚本，用于初始化交付文档、读取/创建飞书文档、记录前后端分支、生成 Playwright 脚手架和检查项目命令。脚本不安装依赖、不修改业务代码；写入飞书或执行构建前仍由 Agent 按阶段确认。

`-g` 安装到用户级，所有项目可用；去掉 `-g` 只安装到当前项目。默认安装到通用目录 `~/.agents/skills/`，支持该目录的宿主会自动加载。

Claude Code 使用：

```bash
npx skills add sjd199625/team-skills -g --skill change-summary -a claude-code
```

如果 `npx` 报 `fs/promises` 或 `glob` 相关错误，说明 Node 版本太低。切到 Node 22.20+ 后重试：

```bash
nvm use 24
npx skills add sjd199625/team-skills -g --skill change-summary
```

安装后新开一个会话，直接说“用 change-summary 总结当前改动”或“按 frontend-conventions 修改这个页面”。

## 手动使用（不通过 npx）

用支持 `.agents/skills/` 的宿主打开本目录即可；不支持的工作流需要按宿主方式安装或软链。

## 在 Claude Code 中使用

Claude Code 默认读取 `.claude/skills/`。在项目根目录执行：

```bash
mkdir -p .claude/skills
ln -s ../../.agents/skills/change-summary .claude/skills/change-summary
ln -s ../../.agents/skills/frontend-conventions .claude/skills/frontend-conventions
```

Windows 可使用目录联接，或直接复制目录。

## 在其他项目中使用

复制需要使用的技能目录（如 `change-summary`、`frontend-conventions`）到目标项目的 `.agents/skills/`，或放到用户级目录 `~/.agents/skills/`，即可在所有项目中使用。

## 给其他 Agent 或大模型使用

让 Agent 读取 `.agents/skills/<skill>/SKILL.md`，或把正文加入系统提示/项目规则。自动发现、读取附件和执行脚本的能力取决于具体宿主；实际支持范围以宿主文档为准。

## 新增技能

1. 在 `.agents/skills/` 下新建目录，目录名使用小写字母、数字和连字符。
2. 创建 `SKILL.md`，写入 `name`、`description` 和正文。
3. 需要分项目或分场景说明时，把细节放在 `references/`，并从 `SKILL.md` 链接。
4. 让 `name` 与目录名一致。

GitHub 负责分发；安装或加载仍由各个 Agent 完成。
