---
name: frontend-requirement-design
description: 当用户说“只生成前端技术文档”“先出技术方案”“读这个飞书需求”“把需求拆成页面和测试范围”时使用；读取飞书需求或需求说明，为 `mobile-h5`、`desktop-admin`、`servicer-ssr` 角色生成包含页面/路由/组件、接口假设和测试范围的技术文档。不直接写业务代码。
---

# 需求到前端技术设计

目标不是写一份摘要，而是产出一份前端可以直接照着实现的文档：页面在哪、路由是什么、复用哪些组件、状态怎么变、接口还缺什么、哪些场景要测。

## 输入

优先从飞书读取：

```bash
lark-cli docs +fetch --doc '<feishu-url>' --doc-format markdown --detail simple --as user
```

飞书链接固定用 CLI 读取，不用浏览器抓取。遇到 `need_user_authorization` 时先按 [feishu-intake.md](references/feishu-intake.md) 重新登录，再保存快照；不要把登录失败当成文档无权限。

把原始 Markdown 保存到 `docs/<feature>/sources/`，并记录来源、获取时间和读取范围。命令和冲突处理见 [feishu-intake.md](references/feishu-intake.md)。

输入还可以是：

- 用户直接粘贴的需求；
- 产品文档或接口草稿；
- 现有页面、设计稿或后端分支。

缺少关键信息时先问，不要用“通常是这样”补全。

## 脚本

读取飞书并保存快照可以交给脚本（在 skill 目录执行）：

```bash
python3 <skill-dir>/scripts/fetch_feishu.py \
  --doc '<feishu-url>' \
  --out docs/<feature>/sources/feishu-<name>.md
```

脚本只负责调用 `lark-cli`、检查返回和写入来源头；事实提取、冲突处理和未决问题仍按本节规则完成。

## 执行步骤

### 1. 拉取并标注事实

把需求拆成事实、决策和未决问题：

- 事实：文档明确写的；
- 决策：用户或文档明确选择的；
- 未决：影响页面、接口或验收的；
- 不做：文档明确排除的。

飞书文档中的旧版本、评论和变更记录不能自动当成当前结论；以最新正文加用户确认为准。

### 2. 识别项目和改动面

先读目标项目的 `frontend-conventions`，再读最近的同类页面：

- PC 后台：`desktop-admin`
- 移动 H5：`mobile-h5`
- 服务端渲染 H5：`servicer-ssr`

至少定位：

- 入口路由和页面目录；
- 可复用的列表/详情/弹窗/表单；
- 状态和请求的现有写法；
- 权限、Bridge、空值和错误处理；
- 目标分支和当前工作区状态。

### 3. 生成一份文档

#### `01-frontend-tech-design.md`

按 [frontend-tech-design-template.md](references/frontend-tech-design-template.md) 写，把需求摘要和设计放在同一份文件里，至少包含：

- 来源、背景、范围、角色、业务规则和验收标准；
- 不做项和未决问题；
- 页面和路由；
- 页面/组件拆解；
- 复用组件和新建组件；
- 状态、请求和数据流；
- 接口假设和待联调项；
- 权限、Bridge、空/错/加载；
- PC/H5 差异；
- 文件改动计划；
- 测试范围和测试数据。

接口字段没有确认时标 `待联调`，不要把假设写成契约。

测试用例在页面完成后由 `frontend-e2e-delivery` 写入 `02-test-cases-results.md`，不再单独生成测试计划。

### 4. 设计评审

进入开发前必须让用户确认：

- 页面范围和路由；
- 组件复用/新建；
- 接口假设和待确认项；
- 测试范围；
- 明确不做。

用户未确认时继续补文档；不要先写页面再补设计。

## 项目差异

| 项目 | 设计文档要特别写清 |
| --- | --- |
| `desktop-admin` | 列表/详情路由、`CommonFormTable`/`CommonFormModal`、`config.tsx`、权限、Less、接口解包 |
| `mobile-h5` | 页面路由、`van-list`、筛选 URL、Vant/Tailwind、`v-permission`、Bridge、接口解包 |
| `servicer-ssr` | `src/actions` + `views-react` 双入口、SSR props、SSR 边界、React 版本、组件库版本、`@`/`~`、接口完整响应 |

## 硬约束

- 不编造飞书文档没有写的业务规则。
- 不把未确认接口写成已确认契约。
- 不把另一个项目的组件或状态写法当成本项目方案。
- 不跳过测试范围，页面方案和验证方案一起交付。
- 用户确认前不进入 `frontend-page-delivery`。
- 文档中的代码路径必须真实存在，或明确标为“拟新建”。

模板见 [frontend-tech-design-template.md](references/frontend-tech-design-template.md)。
