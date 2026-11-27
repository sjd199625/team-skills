---
name: iot-frontend-delivery
description: 当用户说“按这份技术文档开发页面”“把页面实现出来”“补组件和路由”“改这个前端功能”时使用；根据已确认的前端技术文档，在 `mobile-h5`、`desktop-admin` 或 `servicer-ssr` 中实现页面、组件、路由、请求和样式；不负责需求澄清或后端实现。
---

# 前端页面交付

输入是已确认的前端技术文档，不是一句“帮我写个页面”。如果设计文档缺失，先用 `iot-requirement-design`；如果只是接口字段没定，先用 `iot-api-integration` 补契约。

## 开始前

1. 读 `iot-feature-workflow/references/project-profile.md` 和 `docs/<feature>/01-frontend-tech-design.md`；只有当前阶段需要时，才读 `02` 或可选的 `03`。
2. 读取当前角色的 `iot-frontend-conventions/references/<role>.md`，确认格式、组件和验证方式。
3. 读最近的同类页面、页面内组件、接口模块和样式文件。
4. 记录当前分支和工作区状态；不要清理或覆盖无关修改。
5. 把文档中的页面/路由/组件映射到真实文件；不存在的标“拟新建”。

设计文档和代码冲突时，代码是当前事实，但要把差异写进 `01-frontend-tech-design.md`，不要静默改需求。

已有技术文档时只补“本次实现增量”，不要重写整份。测试和后端文档不是开发前阻塞项。

## 实施顺序

1. 路由和入口；
2. 页面骨架和已有组件复用；
3. 页面内组件；
4. API 常量和类型；
5. 交互、权限、Bridge；
6. 空/加载/错误/重试；
7. 样式和响应式；
8. 文档和验证。

不要为了“结构统一”先重写公共组件；先确认它是否真的影响多个页面。

## 三个角色的落点

### desktop-admin

- 页面在 `src/pages/<Domain>/<Page>/`；
- 列表用 `CommonFormTable`，列和筛选项放 `config.tsx`；
- 弹窗用 `CommonFormModal`，表格弹窗用 `CommonTableModal`；
- `request` 已解包业务数据，不重复 `.data`；
- 导出使用 `needResponse` + `downloadBlob`；
- 公共组件改动前检查全部调用方。

### mobile-h5

- 页面在 `src/pages/<Feature>/`，路由加到 `src/router/routes/`；
- 列表沿用 `van-list` 的 loading/finished/error；
- 筛选条件按现有页面保留到 URL；
- 按钮权限用 `v-permission:button`；
- Bridge 用 `src/utils/bridge.ts` 的封装；
- 无分号，Vant 组件按现有自动引入方式使用。

### servicer-ssr

- 新增页面必须同时创建 `src/actions` 路由和 `src/views-react/pages` 页面；
- 浏览器 API 只放在挂载后；不要在模块顶层访问 `window`；
- `@` 指向 `src/views-react`，`~` 指向 `src`；
- 浏览器请求返回完整 Axios 响应，成功码 `100000`；
- 注意 React 16、TypeScript 3.9、antd-mobile 2/5 的版本边界；
- 样式使用 Less，设计稿 px 由构建转 vw。

## 验证脚本

实现完成后先 dry-run 检查项目命令和 Node 版本（在 skill 目录执行）：

```bash
python3 <skill-dir>/scripts/run_project_checks.py --repo <repo> --role <mobile-h5|desktop-admin|servicer-ssr>
```

确认后加 `--run` 执行 lint/build。脚本不会切换 Node 版本；版本不符时先手动切换。

## 完成后

把实现记录补进 `01-frontend-tech-design.md`，至少包含：

- 需求 ID 和实际完成范围；
- 改动文件；
- 复用的现有组件；
- 新增组件及原因；
- 接口/字段映射；
- 未完成项和已知风险；
- 实际执行的 lint/build；
- 手工验证过的页面和未验证页面。

再按项目运行验证：

```bash
# desktop-admin
npm run lint
npm run build

# mobile-h5
npm run build

# servicer-ssr
npm run hobber-build
npm run build
```

命令以仓库真实脚本为准；如果项目 README 要求特定 Node 版本，先切换再跑。构建通过不等于页面测试通过，页面验收交给 `iot-e2e-delivery`。

## 交接

- 需要生成/执行页面测试：交给 `iot-e2e-delivery`。
- 接口字段没定或需要读后端：交给 `iot-api-integration`。
- 需要从需求重新开始：回到 `iot-requirement-design`。
- 需要最终摘要：交给 `iot-feature-workflow` 的总结阶段。

更细的实现检查见 [delivery-checklist.md](references/delivery-checklist.md)。
