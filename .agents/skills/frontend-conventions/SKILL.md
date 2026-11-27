---
name: frontend-conventions
description: 当用户说“按项目现有写法/代码风格改”“新增或修改移动 H5、PC 后台、服务端渲染页面”时使用；先识别角色，再沿用该角色的现有实现。其他项目不要直接套用。
---

# 前端开发约定

这三类前端共享业务语言，但框架、返回值和目录结构不同。先确认目标角色，再只读对应 reference；最终以目标目录里的同类页面为准。

## 角色分流

| 角色 | 形态 | 主要入口 | 详细约定 |
| --- | --- | --- | --- |
| `mobile-h5` | Vue 3 + Vant 移动 H5，无分号 | `src/pages`、`src/router/routes` | [mobile-h5.md](references/mobile-h5.md) |
| `desktop-admin` | React PC 后台 + antd，有分号 | `src/pages`、`src/router/index.tsx` | [desktop-admin.md](references/desktop-admin.md) |
| `servicer-ssr` | 服务端渲染移动页，React | `src/actions`、`src/views-react` | [servicer-ssr.md](references/servicer-ssr.md) |

用 `package.json` 和目录确认角色。目标仓库不在当前 workspace 时先定位路径，不要改到另一个同名目录。

## 开始修改

1. 读目标页面本身，再读同目录最接近的列表页、详情页或弹窗。
2. 按实际链路补齐：页面、页面内组件、配置、接口、路由、样式。
3. 先复用现有 `request`、公共表格/表单、权限、Bridge、导航和空值工具，再考虑新增函数。
4. 页面内复用的组件放在页面 `components/`；跨页面复用的组件才放进 `src/components/`。
5. 接口路径放进对应项目的 API 文件，不要散落在 JSX 或模板里。
6. 新代码的类型尽量落在入参/出参和核心状态上；周边已有 `any` 可以沿用，但不要把边界补成更多 `any`。
7. 中文注释只解释业务约束、接口口径、降级原因和兼容性，不逐行解释代码。

## 硬约束

- 不要跨角色复用格式：`mobile-h5` 无分号，`desktop-admin` 和 `servicer-ssr` 有分号；三者都是 2 空格、单引号、120 列。
- 不要混组件库：`mobile-h5` 用 Vant；`desktop-admin` 以 antd 为主；`servicer-ssr` 的组件库按邻近文件选择。
- 不要重复解包：`mobile-h5` 和 `desktop-admin` 的 `request` 通常返回业务数据；`servicer-ssr` 可能返回完整 Axios 响应。以目标项目实际为准。
- 不要顺手升级框架或做全仓迁移。旧页面保持原写法，新页面跟随同目录风格。
- 不要为了“统一”更换 Tailwind、Less、CSS Modules 或状态库。
- 不要把 `servicer-ssr` 的浏览器 API 移到模块顶层；SSR 阶段没有 `window`。
- 不要改公共组件的默认行为而不检查全部调用方。

## 组件抽取

| 角色 | 页面内复用 | 跨页面复用 |
| --- | --- | --- |
| `mobile-h5` | `pages/<Feature>/components/` | `src/components/<Name>/index.vue` |
| `desktop-admin` | `pages/<Domain>/<Page>/components/` | `src/components/<Name>/index.tsx` + `index.less` + `README.md` |
| `servicer-ssr` | `views-react/pages/<Module>/<Page>/components/` | `views-react/components/<Name>/index.jsx` + `index.less` |

公共表单、表格和弹窗如果通过 ref 暴露查询或回填方法，修改前先看 README 和调用方。其他页面优先复用现有组件，不为一个页面提前抽象。

## 请求与数据

- `mobile-h5`：接口模块主要导出 URL 常量，页面直接调用 `request.get/post`；只有跨页面共享的数据契约才放进 API 模块。
- `desktop-admin`：接口模块导出 URL 常量；列表页通过现有表格组件的 `requestMap` 查询，页面不重复管理分页和 loading。
- `servicer-ssr`：后端地址定义在 `src/apis/`，服务端代理在 `src/actions/api/`，浏览器只请求 `/api/...` 的 Node 路由。

项目已有的 Pinia、Redux Toolkit、Vue Query、ahooks 或局部 state 继续沿用；不要把另一个角色的状态方案搬过来。

## 样式

- `mobile-h5` 默认用 Tailwind 原子类组织布局和间距；复杂交互页用相邻页面已有的 scoped CSS 或 Less。
- `desktop-admin` 用 Less，公共变量放在现有样式文件；表格按项目 README 保持左对齐。
- `servicer-ssr` 用 Less，设计稿按 375 宽写 `px`，构建会转成 `vw`；不要手写 rem 或新设计系统。

## 验证

- `mobile-h5`：`npm run build`；改复杂纯逻辑时运行项目已有测试。`npm run test` 可能只是 testing 模式构建，不是单元测试。
- `desktop-admin`：`npm run lint` 和 `npm run build`；lint 覆盖率按项目配置。
- `servicer-ssr`：按该仓库 README 切换 Node，运行项目已有服务端构建和构建命令；新增 action 后需要重启服务。

没有实际执行的验证要明确写“未运行”，不要用构建命令推断页面行为正确。

## 相关工作流

- `frontend-workflow`：从需求到联调的阶段编排。
- `frontend-requirement-design`：需求和技术设计。
- `frontend-page-delivery`：按设计实现页面。
- `frontend-e2e-delivery`：页面用例和测试报告。
- `frontend-api-integration`：接口联调和后端业务/数据来源分析。
