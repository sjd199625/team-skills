# mobile-h5

## 适用场景

修改移动端 H5 页面：列表、详情、表单、权限和复杂交互。先看同目录页面和项目 `README.md`，不要写成 PC 后台风格。

## 项目事实

- 先以目标项目的 `package.json` 和 `README.md` 为准；本模板不绑定具体仓库。
- Vue 3 + Vite + Vant + Pinia + Tailwind + Less 是常见组合，但其他组合按目标项目处理。
- TypeScript 和样式规则沿用目标页面，不要为一个页面引入新框架。
- `@/*` 通常映射到 `src/*`；版本以 tsconfig 为准。
- 本地开发地址由本地 profile 填写，不写进仓库。

## 目录

```text
src/pages/<Feature>/
  list/index.vue
  detail/index.vue
  components/
  config.ts
  type.ts
  model.ts
src/components/<Name>/index.vue
src/api/<domain>/index.ts
src/router/routes/<domain>.ts
src/stores/
src/utils/
src/types/
```

`list` 页面是否拆成独立搜索/筛选路由，按当前模块决定，不要机械复制。

## 页面与路由

- 页面优先使用 `<script setup lang="ts">`、`ref`、`computed`、`onMounted`。
- 路由按领域放在 `src/router/routes/*.ts`，由现有路由入口展开。
- 保留 `name`、`meta.title`、`meta.menu`、`meta.skipPermission` 的现有语义。
- 只有公开页面等确实不需要权限接口的页面才加 `skipPermission`。
- 新页面要检查应用启动顺序；依赖用户初始化的请求不得提前触发。

## 请求

先读目标项目的 `src/utils/request.ts` 或等价封装：

- 确认请求是否已经解包业务数据；
- 是否统一写入用户、频道和登录态；
- 是否统一处理登录跳转和错误 toast。

页面不要把已解包的数据再次按 Axios 响应解包，也不要在页面重复 toast 网络异常。接口地址集中放在项目 API 文件。

如果项目已经使用 `useQuery`，沿用同类页面的 `queryKey` 写法；不要为一次页面新增查询层。

## 权限与 Bridge

- 按钮权限用目标项目已有的指令或权限组件。
- 用户身份和权限初始化在现有 auth/启动流程中；页面不要在挂载前抢发依赖用户态的请求。
- App 能力统一走目标项目的 Bridge 封装；不要在新页面直接调用老版全局对象。
- 浏览器环境的降级由 Bridge 封装内部处理。

## 列表与详情

- 列表沿用目标项目的 `van-list` 或等价组件的 loading/finished/error 三态。
- 失败时保留错误态，避免自动重试形成死循环。
- 筛选条件放 URL 还是页面 state，跟随同模块页面。
- 空值展示优先使用项目已有工具，不重复写 `|| '-'`。
- 状态、绑定状态等展示值优先使用现有枚举和 Tag 映射。

## 复杂流程

复杂流程可参考目标项目的纯函数模块结构：

- `model.ts`：接口原始结构、前端结构和归一化纯函数；
- `normalize.ts`：unknown、数组和嵌套字段读取；
- `pageConfig.ts`：文案和流程配置；
- `mock.ts`：开发 mock；
- `env.ts`：用开发环境开关作为 mock 硬门槛；
- 页面组件按步骤拆到 `components/`，轮询、超时和异常在页面层收敛；
- 定时器和事件监听在卸载时清理。

只有“字段不稳定、流程多阶段、需要 mock 和纯函数验证”时才采用这套结构。

## 样式

- 默认使用目标页面已有的 Tailwind 原子类。
- 复杂嵌套、伪元素、组件库内部类覆盖放页面 scoped style 或已有共享 Less。
- 不要为一个新页面新建另一套样式方案。
- 1px 分隔线、状态颜色等跟随现有页面。

## 验证

```bash
npm run build
```

项目没有独立 lint 脚本时不要编造 `npm run lint`。改复杂流程时，运行项目已有的纯逻辑测试；命令以本地 profile 和 `package.json` 为准。

## 常见错误

- 把已经解包的请求返回值再次当 Axios response。
- 在用户初始化前发依赖用户态的请求。
- 使用 PC 后台的组件、分页参数或 Redux 写法。
- 为单个接口造通用请求层。
- 忘记把新路由加入领域路由文件。
- 在页面里重复维护筛选条件和 URL 状态。
