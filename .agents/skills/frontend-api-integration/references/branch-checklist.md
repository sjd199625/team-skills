# 分支和后端代码检查

## 记录仓库状态

```bash
git -C "<repo>" rev-parse --show-toplevel
git -C "<repo>" branch --show-current
git -C "<repo>" rev-parse --short HEAD
git -C "<repo>" log -1 --format='%h %s'
git -C "<repo>" status --short --branch
```

## 对齐 feature

从文件名、分支名、提交信息或需求号中提取共同标识，例如 `<requirement-id>`、`<feature>`。只有明确匹配才当作同一需求。

同一需求同时涉及移动 H5 和 PC 时，两个前端仓库、分支和提交都要分别记录；不要只写一个 `frontend`。

出现以下情况先问用户：

- 前端在 feature 分支，后端在 `master`；
- 前后端 feature 名不同；
- 后端有多个候选分支；
- 后端工作区有未提交修改；
- 用户只提供了接口文档，没有版本信息。

## 读取顺序

1. README / docs / 技术方案；
2. controller 和路由；
3. request/response DTO；
4. service/logic；
5. DAO/mapper/entity；
6. 配置和外部依赖；
7. 测试和日志。

## 输出要求

联调或后端文档开头写明：

```text
仓库：<path>
分支：<branch>
提交：<sha>
读取时间：<YYYY-MM-DD HH:mm>
```

分支不清时，不写“后端应该”；写“后端分支未确认，暂不能判断”。
