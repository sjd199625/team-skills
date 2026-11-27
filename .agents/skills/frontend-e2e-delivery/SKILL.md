---
name: frontend-e2e-delivery
description: 当用户说“测试这个页面”“生成并执行 case”“跑页面验收”“做回归”“验证这些入口”时使用；为 `mobile-h5`、`desktop-admin` 和 `servicer-ssr` 角色生成可追溯的页面测试用例并执行浏览器验收/自动化测试，用例和真实结果统一输出到 `02-test-cases-results.md`；不修改业务代码，不虚构测试结果。
---

# 页面测试交付

测试 skill 只做三件事：生成可追溯的 case、真实执行、写真实报告。不要在这里修业务代码；失败项回到 `frontend-page-delivery`。

## 第 0 步：确认真实入口

先确认：

- 页面路由和访问地址；
- 登录态或测试账号；
- 测试环境/本地启动命令；
- 前端是否依赖后端分支或联调数据；
- 本轮是冒烟验收还是一轮回归。

页面打不开、没有测试数据或没有登录态时，先停下来补条件；不要写“预期通过”。已知测试入口、登录方式和 mock 开关先读 `frontend-workflow/references/project-profile.local.md`，不存在时读模板 `project-profile.md`，不要每轮重新猜。

### 登录态获取顺序

1. 优先使用 `stable-chrome` 接管用户已经登录的真实 Chrome。
2. 用户没有登录时，明确请用户登录一次；不要用匿名窗口硬登。
3. 登录后先验证一个真实接口返回，再开始写用例。
4. 仍然拿不到登录态时，把相关项目/入口标为“阻塞”，写清原因和下一步；不能因为登录失败跳过整个 PC 或核心入口。

### 覆盖范围先定死

生成用例前先写“覆盖矩阵”，至少覆盖本轮需求涉及的项目和入口：

| 角色 | 必查入口 |
| --- | --- |
| `desktop-admin` | PC 主页面；需求涉及的二级入口或深链 |
| `mobile-h5` | H5 主页面；需求涉及的二级入口、深链或扫码入口 |
| `servicer-ssr` | 服务端渲染 H5 主页面；刷新/直达；Bridge 相关入口 |

规则：

- 需求明确涉及的入口不能省略；确实不涉及时写“不适用 + 原因”，不要写“未执行”。
- 核心项目或核心入口没有执行时，结论只能是“部分通过”，不能写“通过”。
- 不能用 PC 通过代替 H5 通过，也不能用 H5 通过代替 SSR H5 通过。

## 第 1 步：检测测试能力

先检查现有测试栈：

```bash
rg -n 'playwright|cypress|puppeteer|vitest|jest' package.json pnpm-lock.yaml package-lock.json tests 2>/dev/null
```

再选择执行方式：

### 冒烟/一次性验收

使用 `stable-chrome`：

- 复用用户真实 Chrome 和登录态；
- 不要求业务仓库先安装 Playwright；
- 适合页面验收、截图、网络请求检查、联调冒烟；
- 产物是测试报告和截图，不是长期回归套件。

执行前读 `stable-chrome` skill，按它的安装/附着流程操作。典型检查：

```bash
sbc doctor
sbc start-task --title "<feature>-验收"
sbc new-tab --url "<page-url>"
sbc snapshot
sbc net-start
sbc screenshot --out /tmp/<feature>.png
sbc end-task
```

如果当前 Chrome 扩展不支持 `start-task`、`claim` 或 `content`，不要跳过测试：先尝试 `sbc goto` / `sbc snapshot` / `sbc screenshot` 的可用组合；仍然不可用时改用 Playwright 或如实写阻塞。

### 可重复回归

只有用户明确需要长期回归时，才使用 Playwright：

- 在新目录 `tests/e2e/` 建独立测试包，不把测试依赖塞进业务应用；
- 使用 `@playwright/test` + TypeScript；
- 记录 baseURL、登录态、测试数据和浏览器；
- `trace`/`screenshot` 只在测试包内；
- 安装依赖或初始化测试包前先获得用户确认。

Scaffold 见 [playwright-scaffold.md](references/playwright-scaffold.md)。

需要独立测试包时，可以先生成不安装依赖的脚手架（在 skill 目录执行）：

```bash
python3 <skill-dir>/scripts/scaffold_playwright.py \
  --dir tests/e2e \
  --base-url '<test-url>'
```

脚本只创建 `package.json`、`playwright.config.ts`、smoke case 和 fixtures；安装依赖或浏览器前仍需用户确认。

## 第 2 步：生成 case

从 `01-frontend-tech-design.md` 和真实页面生成用例。至少覆盖：

- 正向主流程；
- 空数据/初始态；
- 边界值和异常；
- 权限/未登录；
- 加载/失败/重试；
- 重复提交/返回；
- PC/H5 差异；
- 联调后的接口数据。

每条用例要有：

- 需求来源；
- 前置条件；
- 测试数据；
- 操作步骤；
- 可观测的预期结果；
- 实际结果和状态；
- 执行环境、页面 URL、截图/请求证据；
- 阻塞时的原因、责任人和下一步。

用例模板见 [test-case-template.md](references/test-case-template.md)。

## 第 3 步：执行

### stable-chrome

- 页面操作后截图；
- 关键请求用 `sbc net-get` 核对状态码和响应；
- 控制台错误不能只看页面是否打开；
- 记录失败页面 URL、操作和截图路径。
- 记录登录态是否可用；登录态失效导致没测的入口，单独列入“阻塞”。

### Playwright

- 在 `tests/e2e` 运行；
- 失败保留 trace/screenshot；
- 不吞异常；
- 不把跳过的用例算通过；
- 不对列表做绝对数量断言，优先断言当前用例创建的标识存在。

## 第 4 步：写用例和结果

输出 `docs/<feature>/02-test-cases-results.md`，同一份文件同时包含用例、实际结果和报告结论：

- 环境、页面地址、分支/提交；
- 用例总数、通过、失败、阻塞、不适用；
- 每条失败的实际结果和截图/日志；
- 未覆盖或无法执行的场景，必须写原因、责任人和下一步；
- 结论：通过 / 部分通过 / 不通过。

用例与结果模板见 [test-case-template.md](references/test-case-template.md)。

### 结论门禁

- 核心角色（PC/H5/SSR）或核心入口没有执行：结论写“部分通过”。
- 只有“需求不涉及”的入口可以写“不适用”；“没时间/没登录/没数据”只能写“阻塞”。
- 报告里出现“阻塞”时，必须同时写清楚谁跟进、下一步做什么；不能只留一个空状态。

## 硬约束

- 没有真实执行不写通过。
- 页面打不开、环境未启动、没有测试数据时写阻塞，不写通过。
- 不修改业务代码来“让测试通过”；失败回到开发 skill。
- 不在业务仓库静默安装测试依赖。
- 不把构建通过、接口 200 或截图一张当成完整页面测试。
- 不用随机假数据断言具体业务结果。

完成后把报告交给 `frontend-workflow` 继续联调或总结。
