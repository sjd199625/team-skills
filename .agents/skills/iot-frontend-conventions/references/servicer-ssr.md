# servicer-ssr

## 适用场景

修改服务端渲染 H5：页面、服务端 action、浏览器交互和 SSR 初始数据。新增页面必须同时考虑服务端入口和 React 视图；不要当成普通 Vite 单页应用。

## 项目事实

- 先以目标项目的 `package.json` 和 `README.md` 为准。
- 服务端渲染框架、React/TypeScript 版本和组件库按目标项目。
- `@`、`~` 等别名按 tsconfig 和现有文件，不要混用。
- Node 和构建版本按项目 README；版本过高可能导致依赖问题。
- 设计稿尺寸、px/vw 转换和样式方案按项目配置。

## 目录和数据边界

```text
src/actions/                 # 页面路由处理器，文件路径对应访问路由
src/actions/api/             # 浏览器请求的服务端 API 代理
src/apis/                    # 后端接口定义
src/views-react/pages/       # React 页面和页面内组件
src/views-react/components/  # 跨页面 React 组件
src/views-react/hooks/       # 前端 hooks
src/utils/request.js         # 浏览器请求封装
src/responses/ajax.ts        # 服务端统一 JSON 返回
```

`src/apis` 是服务端接口定义；浏览器组件不直接访问后端地址，而是请求 `src/actions/api` 提供的 `/api/...` 路由。

## 新增页面

### 1. 建服务端 action

在 `src/actions/<module>/<route>.ts` 建页面处理器，渲染路径要对应 `src/views-react/pages` 下的文件：

```ts
export default {
  async handler(ctx) {
    try {
      const userInfo = await ctx.checkLogin();
      const rendered = await kssr.render('<module>/<route>/index', { userInfo });
      ctx.body = rendered.body;
    } catch (e) {
      ctx.response.render('500', { error: e });
    }
  }
};
```

- 文件路径就是访问路由，新增后需要重启服务。
- 需要登录时调用项目已有登录方法；不需要登录的页面不要为了形式调用。
- 服务端异常走项目已有 500 渲染，不直接返回异常对象。

### 2. 建 React 页面

在 `src/views-react/pages/<module>/<route>/index.jsx`（或 `.tsx`）建页面，样式放同目录。页面壳、Head 和埋点使用项目已有 layout。

类组件仍然存在时跟随当前文件；新页面按仓库规范优先函数组件。不要在单页混用 class 生命周期和 hooks。

需要 SSR 初始数据时，使用类或函数组件已有的 `getInitialProps` 模式；它接收 action 传入的 props。

### 3. 浏览器逻辑放到挂载后

- `window`、`document`、`location`、`localStorage`、Bridge 初始化只能放在 `componentDidMount` 或 `useEffect`。
- 不要在模块顶层读浏览器对象。
- 页面使用 `this.state` 或 hooks 时跟随当前文件；不要为了新功能重写整页。
- 使用目标项目支持的 React/TypeScript 语法。

## 新增接口

这个项目通常有三层，缺一层浏览器就调不通：

1. `src/apis/<domain>.ts` 定义后端接口；
2. `src/actions/api/<domain>/<name>.ts` 建服务端代理；
3. React 页面通过 `~/utils/request` 请求 Node 路由。

具体 import、返回结构和成功码以目标项目为准。浏览器响应可能是完整 Axios 响应；不要套用其他项目的解包方式。

新 API 必须同时检查 `needLogin` 和 `catchError`。

## SSR 与 Bridge

- 登录信息、URL 查询和标题等稳定数据可以由 action 传入；
- 需要服务端数据时，在 action 里完成登录和查询，再传给服务端渲染；
- 服务端渲染阶段不要访问 Bridge；
- 浏览器端和 App 端的标题、关闭页面、登录行为要分别验证。

## 组件和样式

- 页面内组件放页面 `components/`；跨页面组件放 `views-react/components/<Name>/`。
- 样式使用项目已有 Less/CSS 方案，类名沿用现有写法。
- 设计稿尺寸按项目构建方案处理，不要手动引入 rem 或新设计系统。
- 长列表滚动、图片上传等通用能力优先复用项目已有组件。

## 验证

```bash
npm run build
```

项目有独立服务端构建脚本时一并运行；命令以 `package.json` 为准。新增 action 后重启服务；只跑类型检查不能证明 SSR 页面能渲染。

## 常见错误

- 只建 React 页面，忘记 `src/actions` 路由。
- 服务端渲染路径和页面文件路径不一致。
- 在模块顶层访问 `window`，导致 SSR 500。
- 浏览器直接请求 `src/apis` 里的后端地址。
- 套用移动 H5 或 PC 后台的请求返回值习惯。
- 把 `@/` 当成 `src/`，或混用两个别名。
- 在普通页面使用当前 React 版本不支持的 API。
