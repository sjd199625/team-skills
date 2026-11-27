#!/usr/bin/env python3
"""读取飞书文档并保存带来源信息的 Markdown 快照。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def resolve_lark_cli(value: str) -> str:
    path = shutil.which(value)
    if not path:
        die(f"找不到 lark-cli：{value}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc", required=True, help="飞书文档 URL")
    parser.add_argument("--out", required=True, help="保存路径，例如 docs/<feature>/sources/feishu-xxx.md")
    parser.add_argument("--lark-cli", default="lark-cli", help="lark-cli 命令或绝对路径")
    parser.add_argument("--timeout", type=int, default=120, help="读取超时秒数")
    parser.add_argument("--force", action="store_true", help="覆盖已存在文件")
    args = parser.parse_args()

    output = Path(args.out).expanduser().resolve()
    if output.exists() and not args.force:
        die(f"文件已存在：{output}；需要覆盖时加 --force")

    lark_cli = resolve_lark_cli(args.lark_cli)
    command = [
        lark_cli,
        "docs",
        "+fetch",
        "--doc",
        args.doc,
        "--doc-format",
        "markdown",
        "--detail",
        "simple",
        "--as",
        "user",
    ]

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired:
        die(f"读取超时（{args.timeout}s）：{args.doc}")

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        if "need_user_authorization" in detail or "token_missing" in detail:
            print(
                "提示：lark-cli 登录态已过期。先运行 "
                "`lark-cli auth login --scope \"docx:document:readonly\" --no-wait --json`，"
                "打开 verification_url 授权后，再运行 `lark-cli auth login --device-code <code>`。",
                file=sys.stderr,
            )
        die(f"lark-cli 读取失败：\n{detail}")

    snapshot = proc.stdout.strip()
    try:
        payload = json.loads(snapshot)
        if isinstance(payload, dict):
            data = payload.get("data")
            document = data.get("document") if isinstance(data, dict) else None
            if isinstance(document, dict) and document.get("content"):
                snapshot = document["content"]
    except json.JSONDecodeError:
        pass

    if not snapshot:
        die("飞书文档返回为空，未写入文件")

    content = (
        f"> 来源：{args.doc}\n"
        f"> 获取时间：{now()}\n"
        "> 读取范围：全文\n"
        "> 工具：lark-cli docs +fetch\n\n"
        f"{snapshot}\n"
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"已保存：{output}")
    print(f"行数：{len(content.splitlines())}")


if __name__ == "__main__":
    main()
