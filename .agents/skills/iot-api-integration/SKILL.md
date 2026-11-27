---
name: iot-api-integration
description: 当用户说“和后端联调”“读这个后端分支”“看接口文档”“梳理后端逻辑和数据来源”“接口对齐”时使用；与后端联调时，读取接口文档或后端分支，生成接口契约、字段映射和后端业务/数据来源文档，并完成前端 API 接入；默认只读后端。
---

# 前后端联调与后端业务分析

先确定模式，不要一边猜接口一边写页面。

| 模式 | 输入 | 产物 |
| --- | --- | --- |
| `contract` | 接口文档 / OpenAPI / 飞书文档 | 接口契约、字段映射、前端接入点 |
| `backend` | 后端仓库和分支 | 调用链、DTO、数据源、权限、错误 |
| `business-doc` | 后端分支 + 前端页面 | `03-backend-business.md` |
| `full` | 以上全部 | 契约 + 后端分析 + 前端接入 + 测试 |

## 先对齐分支

必须记录：

- 前端仓库、分支、提交；
- 后端仓库、分支、提交；
- 需求/功能标识；
- 读取的文件和行号。

没有匹配的后端分支时停下来问用户，不要默认 `master`。检查命令见 [branch-checklist.md](references/branch-checklist.md)。

记录仓库状态并写入联调文档（在 skill 目录执行）：

```bash
# 同一需求同时改 H5 和 PC 时，额外加 --frontend-pc
python3 <skill-dir>/scripts/record_branches.py \
  --frontend <frontend-repo> \
  --frontend-pc <pc-repo> \
  --backend <backend-repo> \
  --require-backend \
  --out docs/<feature>/03-backend-business.md \
  --append
```

没有后端仓库或后端分支为空时，`--require-backend` 会直接失败。脚本只记录 git 事实，不判断业务结论。

## contract 模式

从接口文档或后端 controller 提取：

- method、path、base path、网关前缀；
- 鉴权 header、ucid/token、租户/城市过滤；
- 请求字段、类型、必填、默认值、枚举；
- 响应 envelope、分页字段、空值；
- 错误码和错误文案；
- 日期/金额/状态格式；
- 幂等、重复提交、副作用。

然后对照前端：

- API 常量放在哪；
- 请求函数/页面在哪里调用；
- 请求和响应是否已经被拦截器解包；
- 现有类型是否需要补；
- 页面显示是否缺少字段。

把接口契约和字段映射写入 `03-backend-business.md`，模板见 [contract-template.md](references/contract-template.md)。

## backend / business-doc 模式

沿真实调用链读：

```text
Controller
  → Request DTO
  → Service / Logic
  → DAO / Mapper
  → Entity / Table
  → Redis / MQ / RPC / Feign / 外部 API
  → Apollo / 配置
```

至少回答：

- 数据从哪里来；
- 哪个字段由哪段逻辑计算；
- 有哪些状态流转；
- 哪些条件会提前返回或抛错；
- 权限/租户/城市如何过滤；
- 是否有异步、定时任务、MQ、缓存副作用；
- 哪些结论是代码事实，哪些是推断。

把后端调用链、数据来源和业务规则追加到 `03-backend-business.md`，模板见 [backend-business-template.md](references/backend-business-template.md)。

## 前端接入

- 不同前端角色的请求解包方式不同，按 `iot-frontend-conventions` 处理；
- 接口路径放在项目 API 文件，不写死在页面；
- 新增字段先补类型和兜底，再改展示；
- 后端只读；除非用户明确要求，否则不改后端代码；
- 接口不一致时先记录，不静默改字段名。

完成后交给 `iot-e2e-delivery` 重跑页面测试，并把结果写进 `02-test-cases-results.md`。

## 硬约束

- 不猜后端分支。
- 不把字段名相似当成同一字段。
- 不把 `master` 的后端行为当成 feature 分支行为。
- 不修改后端代码来迁就前端猜测。
- 不重复实现项目已有的请求封装。
- 不把未验证的推断写成后端事实。

详细模板：

- [contract-template.md](references/contract-template.md)
- [backend-business-template.md](references/backend-business-template.md)
- [branch-checklist.md](references/branch-checklist.md)
