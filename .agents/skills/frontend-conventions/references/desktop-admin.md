# desktop-admin

## 适用场景

修改 PC 后台页面：列表、详情、表单、弹窗、权限和导出。先看同模块的 `index.tsx`、`config.tsx` 和 `components/`，不要用移动 H5 的组件和分页习惯。

## 项目事实

- 先以目标项目的 `package.json` 和 `README.md` 为准。
- React、路由、状态库和 UI 库按目标项目；不要因为模板而升级或替换。
- `@/*` 通常映射到 `src/*`；以 tsconfig 为准。
- ESLint、Prettier 和 Node 版本以项目配置为准。
- 内部接口、域名和测试数据只放本地 profile。

## 目录

```text
src/pages/<Domain>/<Page>/
  index.tsx
  index.less
  config.tsx
  components/
src/components/<Name>/
  index.tsx
  index.less
  README.md
src/api/<domain>.ts
src/router/index.tsx
src/store/
src/utils/
src/common/
```

页面内的列定义、筛选项、格式化和状态映射通常放在 `config.tsx`，页面 `index.tsx` 只负责组合和事件。

## 路由

- 在项目现有路由入口增加懒加载页面。
- 菜单和按钮权限来自项目权限数据，不要另造一套菜单常量。
- 导航优先使用项目已有的全局导航封装。

## 列表页

优先使用项目已有的表格/查询组件：

- 列、筛选字段、格式化和事件放页面配置；
- 分页、loading、空态和错误态由公共组件处理；
- 请求 URL 放在项目 API 文件；
- 不要在页面重复实现 `list/records` 和 `total/totalCount` 兼容。

公共表格通常支持搜索字段、范围日期、参数清理和重置回调；新增能力前先读组件 README 和调用方。

## 弹窗和表单

- 编辑弹窗优先使用项目已有表单弹窗；
- 表格弹窗优先使用项目已有表格弹窗；
- 字段联动通过现有字段配置或表单 API 完成；
- 修改公共组件前检查全部调用方和 README。

## 请求与数据

- 先确认 `src/utils/request` 是否已经解包业务数据；
- 页面不要再次读取 `.data`；
- 导出文件按项目已有 `blob`/`needResponse`/下载方法处理；
- 全局 store 和页面 state 的边界沿用现有页面；
- 不要为单个页面新增 Redux slice 或新的请求库。

## 权限

- 先找目标模块已有权限常量、hook 或判断函数；
- 不要直接写全局权限对象；
- 按钮权限缺失时按现有页面的条件渲染处理。

## 样式

- 页面样式放同目录 `index.less` 或项目已有样式文件；
- 公共组件同时提供组件、样式和 README 时，新增也补齐；
- 不要引入第二套 UI 组件库或替换现有 Less。
- 专项可视化可以沿用项目已有依赖；普通增删改查页不要新增一套。

## 组件抽取

- 页面内展示/交互组件放页面 `components/`；
- 跨页面复用才放 `src/components/`；
- 需要父页面触发查询、回填或提交时，使用项目已有 ref 模式；
- 不要为单个页面造通用表格、筛选器或弹窗。

## 验证

```bash
npm run lint
npm run build
```

命令以 `package.json` 为准；lint 通过不代表所有文件都检查过，构建通过不代表页面测试通过。

## 常见错误

- 把 `request` 返回值再按 Axios response 解包。
- 在页面重复实现分页和 `list/records` 兼容。
- 把列定义和筛选项都塞进 `index.tsx`。
- 为单个页面修改公共表格或弹窗的默认行为。
- 忘记把新页面加入路由。
- 用移动端布局写 PC 页面。
- 引入第二套 UI 组件库。
