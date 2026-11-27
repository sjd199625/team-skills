# 工作流状态模板

复制到目标仓库的 `docs/<feature>/workflow-state.yaml`，按实际进度更新。

```yaml
feature: <kebab-case-feature>
updated_at: <YYYY-MM-DD HH:mm>
phase: design # design | delivery | test | integration | done
last_completed_phase: ""

repos:
  frontend:
    path: <repo-path>
    branch: <branch>
    commit: <short-sha>
  frontend_pc:              # 可选：同一需求同时有 H5 和 PC
    path: <pc-repo-path-or-empty>
    branch: <pc-branch-or-empty>
    commit: <pc-short-sha-or-empty>
  backend:
    path: <repo-path-or-empty>
    branch: <branch-or-empty>
    commit: <short-sha-or-empty>

feishu:
  folder:
    name: <folder-name-or-empty>
    token: <folder-token-or-empty>
    url: <folder-url-or-empty>
  documents:
    frontend_spec: <doc-url-or-empty>
    test_cases: <doc-url-or-empty>
    backend_business: <doc-url-or-empty>

artifacts:
  frontend_spec: docs/<feature>/01-frontend-tech-design.md
  test_cases: docs/<feature>/02-test-cases-results.md
  backend_business: docs/<feature>/03-backend-business.md

gates:
  design_confirmed: false
  build_passed: false
  test_passed: false
  integration_confirmed: false

open_questions: []
```

## 更新规则

- 进入新阶段前先读 `workflow-state.yaml` 和当前产物，不重新读其他历史文档。
- 分支或提交变化时更新 `repos`，并把旧测试结果标记为可能需要重跑。
- 设计和联调必须由用户确认，不默认已确认。
- 测试失败不把 `test_passed` 设为 true。
- 后端文档是可选的；没有后端输入时不要生成空文件。
- feature 改名时同步文件名和引用，不要留下两套目录。
- 同一需求同时改 H5 和 PC 时，两个仓库分别记录，不要只记一个 frontend。
- 发布到飞书后把 folder token 和文档 URL 写进 `feishu`，不要每轮重新创建重复文档。
- 进入新阶段前先跑 `feature_docs.py gate`；门禁没过就不要把阶段标为完成。
