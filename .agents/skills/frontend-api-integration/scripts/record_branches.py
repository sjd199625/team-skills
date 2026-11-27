#!/usr/bin/env python3
"""记录前后端仓库、分支、提交和工作区状态。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def git(repo: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        die("找不到 git")
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def repo_info(repo: Path) -> dict:
    if not repo.is_dir():
        die(f"目录不存在：{repo}")
    toplevel = git(repo, "rev-parse", "--show-toplevel")
    if not toplevel:
        die(f"不是 git 仓库：{repo}")
    return {
        "path": Path(toplevel).resolve(),
        "branch": git(repo, "branch", "--show-current"),
        "commit": git(repo, "rev-parse", "--short", "HEAD"),
        "subject": git(repo, "log", "-1", "--format=%h %s"),
        "status": git(repo, "status", "--short"),
    }


def block(role: str, info: dict | None) -> str:
    if info is None:
        return f"### {role}\n\n- 仓库：未提供\n- 分支：未确认\n\n"
    status = [line for line in info["status"].splitlines() if line.strip()]
    state = "有未提交修改" if status else "干净"
    lines = [
        f"### {role}",
        "",
        f"- 仓库：`{info['path']}`",
        f"- 分支：`{info['branch'] or '未确认'}`",
        f"- 提交：`{info['commit'] or '未确认'}`",
        f"- 最近提交：{info['subject'] or '未确认'}",
        f"- 工作区：{state}",
    ]
    if status:
        lines.append("- 修改：")
        lines.extend(f"  - `{item}`" for item in status)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontend", required=True, help="前端仓库路径")
    parser.add_argument("--frontend-pc", help="PC 前端仓库路径；同一需求同时改 H5 和 PC 时提供")
    parser.add_argument("--backend", help="后端仓库路径")
    parser.add_argument("--out", help="写入文件；默认输出到 stdout")
    parser.add_argument("--append", action="store_true", help="追加到 --out")
    parser.add_argument("--force", action="store_true", help="覆盖 --out")
    parser.add_argument("--require-backend", action="store_true", help="后端分支未确认时失败")
    args = parser.parse_args()

    frontend_path = Path(args.frontend).expanduser().resolve()
    frontend_pc_path = Path(args.frontend_pc).expanduser().resolve() if args.frontend_pc else None
    backend_path = Path(args.backend).expanduser().resolve() if args.backend else None
    frontend = repo_info(frontend_path)
    frontend_pc = repo_info(frontend_pc_path) if frontend_pc_path else None
    backend = repo_info(backend_path) if backend_path else None

    if args.require_backend:
        if backend is None:
            die("未提供后端仓库，不能进入联调", 2)
        if not backend["branch"]:
            die("后端分支为空，不能进入联调", 2)

    lines = [
        "## 仓库状态",
        "",
        f"> 记录时间：{now()}",
        "",
        "| 角色 | 仓库 | 分支 | 提交 | 工作区 |",
        "| --- | --- | --- | --- | --- |",
    ]
    repos = [("前端", frontend)]
    if frontend_pc is not None:
        repos.append(("前端 PC", frontend_pc))
    repos.append(("后端", backend))

    for role, info in repos:
        if info is None:
            lines.append(f"| {role} | 未提供 | 未确认 |  |  |")
        else:
            state = "有未提交修改" if info["status"] else "干净"
            lines.append(
                f"| {role} | `{info['path']}` | `{info['branch'] or '未确认'}` | "
                f"`{info['commit'] or '未确认'}` | {state} |"
            )
    blocks = [block("前端", frontend)]
    if frontend_pc is not None:
        blocks.append(block("前端 PC", frontend_pc))
    blocks.append(block("后端", backend))
    lines.extend(["", *blocks])
    markdown = "\n".join(lines).rstrip() + "\n"

    if args.out:
        output = Path(args.out).expanduser().resolve()
        if output.exists() and not args.append and not args.force:
            die(f"文件已存在：{output}；使用 --append 或 --force")
        output.parent.mkdir(parents=True, exist_ok=True)
        if args.append and output.exists():
            with output.open("a", encoding="utf-8") as handle:
                handle.write("\n" + markdown)
        else:
            output.write_text(markdown, encoding="utf-8")
        print(f"已写入：{output}", file=sys.stderr)
    else:
        print(markdown)

    if backend is not None and not backend["branch"]:
        print("WARN: 后端分支为空，联调前必须确认。", file=sys.stderr)


if __name__ == "__main__":
    main()
