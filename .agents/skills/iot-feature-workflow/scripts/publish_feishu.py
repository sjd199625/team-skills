#!/usr/bin/env python3
"""通过 lark-cli 把本地 Markdown 创建或更新成飞书文档。"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", help="飞书文档标题；创建时必填")
    parser.add_argument("--doc", help="已有飞书文档 URL 或 token；提供时执行更新")
    parser.add_argument("--command", choices=["append", "overwrite"], default="append", help="更新方式，默认 append")
    parser.add_argument("--content", required=True, help="本地 Markdown 文件")
    parser.add_argument("--parent-token", help="目标文件夹或 Wiki 节点 token")
    parser.add_argument("--parent-position", help="目标位置，例如 my_library")
    parser.add_argument("--as", dest="identity", choices=["user", "bot"], default="user")
    parser.add_argument("--format", choices=["json", "pretty"], default="pretty")
    parser.add_argument("--dry-run", action="store_true", help="只打印请求，不创建")
    parser.add_argument("--confirm", action="store_true", help="确认执行写操作")
    parser.add_argument("--lark-cli", default="lark-cli")
    args = parser.parse_args()

    if args.doc and (args.title or args.parent_token or args.parent_position):
        die("更新已有文档时不要传 --title/--parent-token/--parent-position")
    if not args.doc and not args.title:
        die("创建文档需要 --title", 2)
    if args.parent_token and args.parent_position:
        die("--parent-token 和 --parent-position 不能同时使用")
    if not args.dry_run and not args.confirm:
        die("发布飞书文档是写操作；确认后加 --confirm，或先加 --dry-run", 2)

    content_path = Path(args.content).expanduser().resolve()
    if not content_path.is_file():
        die(f"Markdown 文件不存在：{content_path}")
    content = content_path.read_text(encoding="utf-8")
    if not content.strip():
        die(f"Markdown 文件为空：{content_path}")

    lark_cli = shutil.which(args.lark_cli)
    if not lark_cli:
        die(f"找不到 lark-cli：{args.lark_cli}")

    if args.doc:
        command = [
            lark_cli,
            "docs",
            "+update",
            "--doc",
            args.doc,
            "--command",
            args.command,
            "--content",
            "-",
            "--doc-format",
            "markdown",
            "--as",
            args.identity,
            "--format",
            args.format,
        ]
    else:
        command = [
            lark_cli,
            "docs",
            "+create",
            "--title",
            args.title,
            "--content",
            "-",
            "--doc-format",
            "markdown",
            "--as",
            args.identity,
            "--format",
            args.format,
        ]
        if args.parent_token:
            command.extend(["--parent-token", args.parent_token])
        if args.parent_position:
            command.extend(["--parent-position", args.parent_position])
    if args.dry_run:
        command.append("--dry-run")

    proc = subprocess.run(
        command,
        input=content,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        die(f"飞书文档发布失败：\n{detail}")
    if not args.dry_run:
        print("飞书文档已更新。" if args.doc else "飞书文档已创建。")


if __name__ == "__main__":
    main()
