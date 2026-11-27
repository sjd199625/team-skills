#!/usr/bin/env python3
"""初始化并检查精简交付产物。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ARTIFACTS = [
    ("frontend_spec", "01-frontend-tech-design.md"),
    ("test_cases", "02-test-cases-results.md"),
    ("backend_business", "03-backend-business.md"),
]
ARTIFACT_FILES = dict(ARTIFACTS)

PHASE_REQUIRED = {
    "design": ["frontend_spec"],
    "delivery": ["frontend_spec"],
    "test": ["frontend_spec", "test_cases"],
    "integration": ["frontend_spec", "test_cases"],
    "done": ["frontend_spec", "test_cases"],
}

GATE_REQUIRED = {
    "design": [],
    "delivery": ["design_confirmed"],
    "test": ["design_confirmed", "build_passed"],
    "integration": ["design_confirmed", "build_passed", "test_passed"],
    "done": ["design_confirmed", "build_passed", "test_passed", "integration_confirmed"],
}

PLACEHOLDERS = ("TBD", "FIXME", "待补充", "待填写", "待执行")


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def git_value(repo: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def repo_info(repo: Path) -> dict:
    return {
        "path": str(repo),
        "branch": git_value(repo, "branch", "--show-current"),
        "commit": git_value(repo, "rev-parse", "--short", "HEAD"),
    }


def yaml_value(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def template_01(title: str) -> str:
    return f"""# {title} 前端技术设计

> 状态：草案
> 需求来源：
> 更新：{now()}
> 仓库/分支：

## 范围

- 包含：
- 不包含：

## 需求与验收

- 用户/角色：
- 核心流程：
- 明确不做：
- 未决问题：

## 页面、路由和组件

| 页面/入口 | 路由 | 复用组件 | 新增文件 | 备注 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 状态和数据流

```text
入口 -> 主流程 -> 成功/空/异常 -> 完成
```

## 接口和 mock

| 能力 | 接口/数据 | 当前实现 | 待确认 |
| --- | --- | --- | --- |
|  |  |  |  |

## 权限和 Bridge

- 登录：
- 页面权限：
- App Bridge：
- 业务差异：

## 实现记录

| 文件 | 新增/修改 | 说明 |
| --- | --- | --- |
|  |  |  |

## 验证

| 类型 | 命令/页面 | 结果 | 证据 |
| --- | --- | --- | --- |
|  |  |  |  |

## 未完成和风险

- 
"""


def template_02(title: str) -> str:
    return f"""# {title} 测试用例与结果

> 环境：
> 分支/提交：
> 更新：{now()}
> 执行方式：

## 结论

- 结果：
- 用例：通过 / 失败 / 阻塞 / 不适用
- 阻塞/不适用：

## 覆盖矩阵

| 类型 | 场景 | 需求来源 | 状态 |
| --- | --- | --- | --- |
| 正向 |  |  |  |
| 空态 |  |  |  |
| 异常 |  |  |  |
| 权限 |  |  |  |

## 用例与结果

### TC-001：用例名称

- 需求来源：
- 前置条件：
- 操作步骤：
  1. 
- 预期结果：
- 实际结果：
- 状态：通过 / 失败 / 阻塞 / 不适用
- 证据：

## 构建和 lint

| 项目 | 命令 | 结果 |
| --- | --- | --- |
|  |  |  |

## 阻塞/不适用和风险

- 
"""


def template_03(title: str) -> str:
    return f"""# {title} 后端业务与数据来源

> 前端仓库/分支：
> 后端仓库/分支：
> 状态：草案
> 更新：{now()}

## 接口清单

| 页面 | 方法 | 路径 | 鉴权 | 状态 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 字段映射

| 接口字段 | 前端字段 | 来源/计算 | 空值 | 前端落点 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 后端调用链

```text
Controller -> Service -> Logic -> DAO/Mapper -> Table/Redis/MQ/RPC
```

## 业务规则和数据来源

| 主题 | 后端事实 | 代码位置 | 影响前端字段 |
| --- | --- | --- | --- |
|  |  |  |  |

## 权限、租户和异步

- 权限：
- 租户/角色：
- MQ/Redis/RPC：
- 定时任务/第三方 API：

## 结论和未决问题

- 事实：
- 推断：
- 未验证：
"""


def write_file(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        print(f"跳过 {path}（已存在）")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"创建 {path}")
    return True


def state_yaml(
    feature: str,
    frontend: dict,
    backend: dict,
    frontend_pc: dict | None = None,
) -> str:
    artifacts = "\n".join(
        f"  {key}: {yaml_value('docs/' + feature + '/' + filename)}"
        for key, filename in ARTIFACTS
    )
    frontend_pc_block = ""
    if frontend_pc:
        frontend_pc_block = f"""  frontend_pc:
    path: {yaml_value(frontend_pc["path"])}
    branch: {yaml_value(frontend_pc["branch"])}
    commit: {yaml_value(frontend_pc["commit"])}
"""
    return f"""feature: {yaml_value(feature)}
updated_at: {yaml_value(now())}
phase: design
last_completed_phase: ""

repos:
  frontend:
    path: {yaml_value(frontend["path"])}
    branch: {yaml_value(frontend["branch"])}
    commit: {yaml_value(frontend["commit"])}
{frontend_pc_block}  backend:
    path: {yaml_value(backend["path"])}
    branch: {yaml_value(backend["branch"])}
    commit: {yaml_value(backend["commit"])}

feishu:
  folder:
    name: ""
    token: ""
    url: ""
  documents:
    frontend_spec: ""
    test_cases: ""
    backend_business: ""

artifacts:
{artifacts}

gates:
  design_confirmed: false
  build_passed: false
  test_passed: false
  integration_confirmed: false

open_questions: []
"""


def state_phase(text: str) -> str:
    match = re.search(r"(?m)^phase:\s*([a-z]+)", text)
    return match.group(1) if match else "design"


def state_gate(text: str, key: str) -> bool:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(true|false)\s*$", text)
    return bool(match and match.group(1) == "true")


def state_section_value(text: str, section: str, key: str) -> str:
    lines = text.splitlines()
    start = None
    section_indent = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        prefix = f"{section}:"
        if stripped == prefix or (stripped.startswith(prefix) and stripped[len(prefix) :].strip().startswith("#")):
            start = index
            section_indent = len(line) - len(line.lstrip())
            break
    if start is None:
        return ""

    for line in lines[start + 1 :]:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= section_indent:
            break
        stripped = line.strip()
        if stripped.startswith(f"{key}:"):
            return stripped.split(":", 1)[1].strip().strip('"')
    return ""


def create_backend_doc(feature_dir: Path, title: str, force: bool) -> None:
    write_file(feature_dir / "03-backend-business.md", template_03(title), force)


def cmd_init(args: argparse.Namespace) -> None:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        die(f"仓库不存在：{repo}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.feature):
        die("feature 只能使用小写字母、数字和连字符")
    if args.backend_branch and not args.backend:
        die("--backend-branch 需要同时提供 --backend")

    title = args.title or args.feature
    feature_dir = repo / "docs" / args.feature
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / "sources").mkdir(exist_ok=True)

    frontend = repo_info(repo)
    if args.frontend_branch:
        frontend["branch"] = args.frontend_branch

    frontend_pc = None
    if args.frontend_pc:
        frontend_pc_path = Path(args.frontend_pc).expanduser().resolve()
        if not frontend_pc_path.is_dir():
            die(f"PC 前端仓库不存在：{frontend_pc_path}")
        frontend_pc = repo_info(frontend_pc_path)

    backend = {"path": "", "branch": "", "commit": ""}
    if args.backend:
        backend_path = Path(args.backend).expanduser().resolve()
        if not backend_path.is_dir():
            die(f"后端仓库不存在：{backend_path}")
        backend = repo_info(backend_path)
        if args.backend_branch:
            backend["branch"] = args.backend_branch

    write_file(feature_dir / "01-frontend-tech-design.md", template_01(title), args.force)
    write_file(feature_dir / "02-test-cases-results.md", template_02(title), args.force)
    if args.backend:
        create_backend_doc(feature_dir, title, args.force)
    else:
        print("未提供后端仓库，跳过 03-backend-business.md（可选）。")

    write_file(
        feature_dir / "workflow-state.yaml",
        state_yaml(args.feature, frontend, backend, frontend_pc),
        args.force,
    )

    if not frontend["branch"]:
        print("提示：没有读到前端分支，请在 workflow-state.yaml 中补充。")
    if frontend_pc and not frontend_pc["branch"]:
        print("提示：没有读到 PC 前端分支，请在 workflow-state.yaml 中补充。")
    print(f"完成：{feature_dir}")
    print("下一步：填写 01；页面和用例完成后更新 02；有后端输入时再生成或填写 03。")


def cmd_check(args: argparse.Namespace) -> None:
    repo = Path(args.repo).expanduser().resolve()
    feature_dir = repo / "docs" / args.feature
    state_path = feature_dir / "workflow-state.yaml"
    if not state_path.exists():
        die(f"缺少状态文件：{state_path}")

    state_text = state_path.read_text(encoding="utf-8")
    phase = args.phase or state_phase(state_text)
    required = PHASE_REQUIRED.get(phase)
    if required is None:
        die(f"未知阶段：{phase}")

    failures: list[str] = []
    for key in required:
        path = feature_dir / ARTIFACT_FILES[key]
        if not path.exists():
            failures.append(f"缺少 {path}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            failures.append(f"空文件 {path}")
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            marker = next((item for item in PLACEHOLDERS if item in line), "")
            if marker:
                failures.append(f"{path}:{line_number} 包含未完成标记 {marker}")
                break

    if not state_section_value(state_text, "frontend", "branch"):
        failures.append("workflow-state.yaml 未记录前端分支")

    frontend_pc_path = state_section_value(state_text, "frontend_pc", "path")
    frontend_pc_branch = state_section_value(state_text, "frontend_pc", "branch")
    if frontend_pc_path and not frontend_pc_branch:
        failures.append("workflow-state.yaml 已记录 PC 前端，但未记录 PC 分支")

    backend_doc = feature_dir / "03-backend-business.md"
    if phase in {"integration", "done"} and backend_doc.exists():
        backend_text = backend_doc.read_text(encoding="utf-8")
        if not backend_text.strip():
            failures.append(f"空文件 {backend_doc}")

    if failures:
        print("检查失败：")
        for item in failures:
            print(f"- {item}")
        raise SystemExit(1)

    print("检查通过：当前阶段产物齐全，未发现占位符，分支已记录。")
    print("注意：脚本只检查结构，不验证业务结论和测试真实性。")


def cmd_gate(args: argparse.Namespace) -> None:
    repo = Path(args.repo).expanduser().resolve()
    feature_dir = repo / "docs" / args.feature
    state_path = feature_dir / "workflow-state.yaml"
    if not state_path.exists():
        die(f"缺少状态文件：{state_path}")

    text = state_path.read_text(encoding="utf-8")
    phase = args.phase or state_phase(text)
    required = GATE_REQUIRED.get(phase)
    if required is None:
        die(f"未知阶段：{phase}")

    failures = [gate for gate in required if not state_gate(text, gate)]
    if failures:
        print(f"门禁未通过：{args.feature} / {phase}")
        for gate in failures:
            print(f"- {gate}: false")
        raise SystemExit(1)
    print(f"门禁通过：{args.feature} / {phase}")


def cmd_status(args: argparse.Namespace) -> None:
    repo = Path(args.repo).expanduser().resolve()
    feature_dir = repo / "docs" / args.feature
    state_path = feature_dir / "workflow-state.yaml"
    if not state_path.exists():
        die(f"缺少状态文件：{state_path}")

    text = state_path.read_text(encoding="utf-8")
    print(f"feature: {args.feature}")
    print(f"phase: {state_phase(text)}")
    print(f"frontend: {state_section_value(text, 'frontend', 'branch')}")
    frontend_pc = state_section_value(text, "frontend_pc", "branch")
    if frontend_pc:
        print(f"frontend_pc: {frontend_pc}")
    print(f"backend: {state_section_value(text, 'backend', 'branch') or '未记录'}")
    for key in ("frontend_spec", "test_cases", "backend_business"):
        value = state_section_value(text, "documents", key)
        if value:
            print(f"feishu.{key}: {value}")
    print("artifacts:")
    for _, filename in ARTIFACTS:
        path = feature_dir / filename
        print(f"- {'OK' if path.exists() else 'MISSING'} {filename}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="初始化精简产物")
    init.add_argument("--repo", required=True, help="前端仓库路径")
    init.add_argument("--feature", required=True, help="kebab-case 需求标识")
    init.add_argument("--title", help="文档标题，默认使用 feature")
    init.add_argument("--frontend-pc", help="PC 前端仓库路径；同一需求同时改 H5 和 PC 时提供")
    init.add_argument("--backend", help="后端仓库路径；提供时生成 03")
    init.add_argument("--frontend-branch", help="覆盖自动读取的前端分支")
    init.add_argument("--backend-branch", help="覆盖自动读取的后端分支")
    init.add_argument("--force", action="store_true", help="覆盖已存在文件")
    init.set_defaults(func=cmd_init)

    check = sub.add_parser("check", help="检查当前阶段产物")
    check.add_argument("--repo", required=True)
    check.add_argument("--feature", required=True)
    check.add_argument("--phase", choices=sorted(PHASE_REQUIRED), help="覆盖状态文件中的 phase")
    check.set_defaults(func=cmd_check)

    gate = sub.add_parser("gate", help="检查当前阶段确认门禁")
    gate.add_argument("--repo", required=True)
    gate.add_argument("--feature", required=True)
    gate.add_argument("--phase", choices=sorted(GATE_REQUIRED), help="覆盖状态文件中的 phase")
    gate.set_defaults(func=cmd_gate)

    status_parser = sub.add_parser("status", help="查看阶段和产物")
    status_parser.add_argument("--repo", required=True)
    status_parser.add_argument("--feature", required=True)
    status_parser.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
