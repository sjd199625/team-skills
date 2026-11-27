#!/usr/bin/env python3
"""按角色执行 lint/build，默认只打印命令。"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROLES = {
    "mobile-h5": {
        "min_node": (16, 0),
        "commands": [["npm", "run", "build"]],
    },
    "desktop-admin": {
        "min_node": (16, 0),
        "commands": [["npm", "run", "lint"], ["npm", "run", "build"]],
    },
    "servicer-ssr": {
        "min_node": (16, 0),
        "commands": [["npm", "run", "build"]],
    },
}


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def node_version() -> tuple[int, int]:
    try:
        proc = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        die("找不到 node")
    match = re.search(r"v(\d+)\.(\d+)", proc.stdout)
    if proc.returncode != 0 or not match:
        die(f"无法读取 Node 版本：{proc.stdout}{proc.stderr}")
    return int(match.group(1)), int(match.group(2))


def check_node(config: dict, version: tuple[int, int]) -> str:
    required = config["min_node"]
    if version < required:
        return f"需要 Node >= {required[0]}.{required[1]}，当前 {version[0]}.{version[1]}"
    return ""


def run_command(command: list[str], repo: Path) -> None:
    print(f"$ {' '.join(command)}")
    proc = subprocess.run(command, cwd=repo, check=False)
    if proc.returncode != 0:
        die(f"命令失败：{' '.join(command)}", proc.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="项目仓库路径")
    parser.add_argument("--role", required=True, choices=sorted(ROLES), help="项目角色")
    parser.add_argument("--run", action="store_true", help="真正执行命令")
    parser.add_argument("--ignore-node", action="store_true", help="忽略 Node 版本检查")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    package_path = repo / "package.json"
    if not package_path.exists():
        die(f"找不到 package.json：{package_path}")

    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"package.json 无法解析：{exc}")

    config = ROLES[args.role]
    version = node_version()
    problem = check_node(config, version)
    print(f"项目：{package.get('name', args.role)}")
    print(f"角色：{args.role}")
    print(f"Node：{version[0]}.{version[1]}")
    sys.stdout.flush()
    if problem:
        print(f"警告：{problem}", file=sys.stderr)
        if not args.ignore_node:
            die("Node 版本不符合要求；切换后再运行，或加 --ignore-node", 3)

    commands = [list(command) for command in config["commands"]]
    for command in commands:
        print(f"{'执行' if args.run else '将执行'}：{' '.join(command)}")
    if not args.run:
        print("这是 dry-run；确认后加 --run 执行。")
        return

    if shutil.which("npm") is None:
        die("找不到 npm")
    for command in commands:
        run_command(command, repo)
    print("命令全部完成。")


if __name__ == "__main__":
    main()
