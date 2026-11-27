---
name: frontend-workflow
description: 当用户要把一个移动 H5、PC 后台或服务端渲染前端需求从飞书文档/需求说明一路做到技术文档、页面开发、测试和联调时使用；也用于用户说“按需求开发这个页面”“把需求跑完”“从文档到页面和测试”“端到端交付”。默认只输出前端技术设计、测试用例与结果，以及可选的后端业务文档。
---

# 前端需求交付编排

这是入口，不重复各阶段的执行细节。先判断当前处于哪一步，再调用对应的专用 skill；只有用户要求端到端推进时才从需求开始连续执行。

## 默认快车道

当用户已经给出目标仓库、分支或明确需求，并希望尽快开始开发时，默认走 [fast-lane.md](references/fast-lane.md)，不要机械拆成八份文档：

1. 先读 `references/project-profile.local.md`；不存在时读 [project-profile.md](references/project-profile.md) 模板，再读 `01-frontend-tech-design.md`、`workflow-state.yaml` 和目标目录的同类页面。
2. 需求来源没有变化时复用 `sources/` 快照，不重复抓飞书；只有用户说需求变了或快照缺失时才重新拉取。
3. 开发前只写一份技术设计；测试完成后写一份测试用例与结果；只有需要后端分析时再写第三份。
4. 每完成一块只跑相关逻辑或一条主流程；结构稳定后再跑 build，交付前再补完整测试。
5. 真实接口、设备或后端分析没有输入时不要为了填文档而猜，也不要把已知信息重复写在多份文件里。

只有需求仍有影响实现的未决问题、需要真实联调/设备/权限，或需要正式交付时，才追加对应的后端或测试产物。

## 项目识别

| 角色 | 形态 | 目录特征 |
| --- | --- | --- |
| `mobile-h5` | Vue + Vant 移动 H5 | `src/pages`、`src/router/routes` |
| `desktop-admin` | React + antd PC 后台 | `src/pages`、`src/components/CommonFormTable` |
| `servicer-ssr` | SSR 服务端渲染 H5 | `src/actions`、`src/views-react` |

先读 `references/project-profile.local.md`；不存在时读 [project-profile.md](references/project-profile.md) 模板，再用目录和 `package.json` 确认角色。读不到目标仓库时先要求用户提供路径，不要改到同名目录。

## 阶段与专用 Skill

| 阶段 | 使用 | 进入条件 | 产物 |
| --- | --- | --- | --- |
| 需求与技术设计 | `frontend-requirement-design` | 有飞书需求或需求说明 | `01-frontend-tech-design.md` |
| 前端开发 | `frontend-page-delivery` | 技术设计已确认 | 页面代码、`01-frontend-tech-design.md` 的实现记录 |
| 页面测试 | `frontend-e2e-delivery` | 页面已实现且可访问 | `02-test-cases-results.md` |
| 联调/后端分析 | `frontend-api-integration` | 有接口文档或后端分支 | 可选 `03-backend-business.md` |

若对应 skill 未安装，先提示用户安装；本 skill 只负责编排，不替代阶段规则。不要凭记忆编造项目结构。

## 状态文件

每个需求在目标仓库创建：

```text
docs/<feature>/workflow-state.yaml
```

字段和示例见 [state-template.md](references/state-template.md)。每次进入新阶段前先读状态文件，不依赖上一轮聊天上下文。

状态文件至少记录：

- 当前阶段和最后完成阶段；
- 前端/后端仓库路径、分支、提交；
- 已存在产物和缺失产物；
- 设计、联调、测试的确认状态；
- 未解决问题。

## 脚本

脚本只做确定性的初始化和结构检查，不替代阶段判断。在 skill 目录执行：

```bash
# 输出一次紧凑上下文：分支、提交、工作区、脚本、feature 相关文件
python3 scripts/project_context.py --repo <repo> --feature <feature>

# 初始化 docs/<feature>/、sources/ 和 workflow-state.yaml
python3 scripts/feature_docs.py init --repo <repo> --feature <feature>

# 同一需求同时改 H5 和 PC
python3 scripts/feature_docs.py init --repo <repo> --feature <feature> --frontend-pc <pc-repo>

# 检查当前阶段产物、占位符和分支记录
python3 scripts/feature_docs.py check --repo <repo> --feature <feature>

# 检查当前阶段的确认门禁
python3 scripts/feature_docs.py gate --repo <repo> --feature <feature>

# 查看阶段和产物
python3 scripts/feature_docs.py status --repo <repo> --feature <feature>
```

`init` 默认只创建 `01-frontend-tech-design.md`、`02-test-cases-results.md` 和状态文件；`--frontend-pc <path>` 记录 PC 仓库，`--backend <path>` 才额外创建 `03-backend-business.md`。状态文件同时保留 `feishu` 目录和文档 URL 的位置。`check` 检查产物结构、占位符和已记录的分支，不验证业务结论或测试真实性。

## 发布到飞书

本地文档确认后，可以创建成飞书文档。先 dry-run 看请求，再确认写入：

```bash
python3 scripts/publish_feishu.py \
  --title '<文档标题>' \
  --content docs/<feature>/01-frontend-tech-design.md \
  --dry-run

python3 scripts/publish_feishu.py \
  --title '<文档标题>' \
  --content docs/<feature>/01-frontend-tech-design.md \
  --parent-token '<folder-or-wiki-token>' \
  --confirm

# 已有文档追加内容
python3 scripts/publish_feishu.py \
  --doc '<doc-url-or-token>' \
  --command append \
  --content docs/<feature>/01-frontend-tech-design.md \
  --confirm
```

不传 `--parent-token` 时使用 `lark-cli` 的默认位置。创建是写操作，必须先确认标题和目录；更新已有文档使用 `--doc` + `--command append`，不要静默覆盖。发布成功后把 folder token 和文档 URL 写进 `workflow-state.yaml` 的 `feishu`。

飞书授权、scope 和 keychain 排障见 `frontend-requirement-design/references/feishu-intake.md`；不要在沙箱里重试 `lark-cli`。

## 阶段门禁

进入新阶段前先跑 `feature_docs.py gate`；门禁失败就停在当前阶段，不要靠聊天记忆跳过。

### 需求与技术设计

- 飞书文档已拉取并保存快照，或用户明确提供了完整需求。
- 页面、路由、组件、状态、权限、接口假设和测试范围都有落点。
- 未解决问题没有被静默假设；阻塞问题先问用户。
- 用户确认技术设计后才进入开发。

### 前端开发

- 先读 `01-frontend-tech-design.md` 和已有实现，再写代码。
- 使用 `frontend-conventions`；不同角色的格式和组件库不能混。
- 页面完成后至少跑项目已有的 lint/build，不通过不得进入测试。
- 把实际改动、未完成项和验证结果补进 `01-frontend-tech-design.md` 的“实现记录”。

### 页面测试

- 先生成可追溯的用例，再执行；不能只跑一次手工操作就写“测试通过”。
- 测试结果必须有真实页面、真实请求或真实截图支撑。
- 用例、预期、实际结果、阻塞和构建结论统一写入 `02-test-cases-results.md`。
- 失败项回到 `frontend-page-delivery` 修，不在测试 skill 里顺手改业务代码。

### 联调

- 后端分支或提交必须明确记录；没有匹配分支时停下来问用户，不默认使用 `master`。
- 接口契约要覆盖前端实际使用的字段、分页、枚举、错误码、权限和空值。
- 后端代码只读；除非用户明确要求，否则不修改后端。

## 常用流程

### 快速开发（默认）

```text
project_context + project_profile
  → 读 01 的本次增量
  → 复制同模块页面结构
  → 实现主流程
  → 跑相关逻辑和页面
  → 补 01 的实现记录和 02 的用例结果
```

### 完整交付

```text
读飞书需求并保存快照
  → 01 前端技术设计（含需求摘要和实现记录）
  → 02 测试用例与结果
  → 有后端输入时再写 03
```

### 只做联调

```text
读接口文档或后端分支
  → 03 契约、字段映射和后端业务/数据来源
  → 修改前端 API 和页面
  → 把回归结果补进 02
```

### 只做后端业务分析

使用 `frontend-api-integration` 的 `business-doc` 模式；先记录仓库、分支和提交，再沿调用链产出文档。

## 硬约束

- 飞书需求/技术文档统一用 `lark-cli docs +fetch` 读取，不用浏览器抓取；先保存来源快照，再分析内容。
- 不根据文件名猜业务；先读需求、代码和接口。
- 不把“构建通过”写成“页面测试通过”。
- 不把“测试未跑”写成“测试通过”。
- 不在一个阶段里悄悄切换项目或分支。
- 不把设计文档中的待确认接口当成已确认契约。
- 不在用户未确认时批量安装测试依赖、修改后端或提交代码。
- 不默认生成和重读完整八份文档；默认只维护三份精简产物。
- 不重复扫描已经记录在 `project-profile.local.md` 或模板中且未变化的项目事实。

产物命名、来源快照和交付检查见 [artifact-contract.md](references/artifact-contract.md)。
