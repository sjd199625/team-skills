# Playwright 回归脚手架

只有在用户明确需要长期回归测试时使用。先确认现有测试栈，不要覆盖项目已有测试配置。

## 目录

```text
tests/e2e/
├── package.json
├── playwright.config.ts
├── tests/
│   └── <feature>.spec.ts
└── fixtures/
```

测试包独立于业务应用，避免把 Playwright 依赖塞进前端生产依赖。

## 配置要点

- `baseURL` 从环境变量读取，默认值写当前测试地址；
- 登录态优先使用 `storageState`，不要硬编码账号密码；
- 失败保留 `trace` 和 `screenshot`；
- 只跑必要的浏览器；
- 测试数据使用可清理的标识，不污染共享环境。

## 执行

```bash
cd tests/e2e
npx playwright test
```

安装浏览器或新增依赖前先获得用户确认：

```bash
npx playwright install chromium
```

## 选择原则

| 场景 | 工具 |
| --- | --- |
| 复用登录态、看真实页面、截图/网络检查 | `stable-chrome` |
| 长期回归、可重复断言、失败留痕 | Playwright |
| 纯接口验证 | 项目已有 API 测试工具；没有就先问用户 |

不要为了“以后可能回归”提前安装 Playwright。
