#!/usr/bin/env python3
"""按项目输出一次紧凑的开发上下文，减少重复目录探索。"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path) -> str:
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def git(repo: Path, *args: str) -> str:
    return run("git", *args, cwd=repo)


def project_name(package: dict) -> str:
    return str(package.get("name") or package.get("displayName") or "").strip()


def project_line(package: dict) -> str:
    name = project_name(package)
    scripts = package.get("scripts") or {}
    interesting = ["build", "lint", "test", "hobber-build"]
    return f"{name or '未命名项目'}: " + ", ".join(f"{key}={scripts[key]}" for key in interesting if key in scripts)


def find_feature_files(repo: Path, feature: str, limit: int) -> list[Path]:
    roots = [repo / "src", repo / "docs"]
    tokens = [token for token in feature.lower().replace("_", "-").split("-") if token]
    matches: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".ts", ".tsx", ".vue", ".less", ".md", ".yaml", ".yml"}:
                continue
            relative = str(path.relative_to(repo))
            # tokens 由 feature 名派生，docs/<feature>/ 下的路径必然已命中 token，无需再判断父目录
            if any(token in relative.lower() for token in tokens):
                matches.append(path)
    return sorted(matches, key=lambda path: str(path))[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="项目仓库路径")
    parser.add_argument("--feature", help="feature 目录名，用于列出相关文件")
    parser.add_argument("--limit", type=int, default=40, help="相关文件数量上限")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    package_path = repo / "package.json"
    if not package_path.is_file():
        parser.error(f"找不到 package.json：{package_path}")

    package = json.loads(package_path.read_text(encoding="utf-8"))
    print(f"repo: {repo}")
    print(f"branch: {git(repo, 'branch', '--show-current') or '-'}")
    print(f"commit: {git(repo, 'rev-parse', '--short', 'HEAD') or '-'}")
    print(project_line(package))

    status = git(repo, "status", "--short")
    print("worktree: clean" if not status else "worktree:\n" + "\n".join(status.splitlines()[:20]))

    if args.feature:
        feature_dir = repo / "docs" / args.feature
        print(f"feature_dir: {'present' if feature_dir.is_dir() else 'missing'} {feature_dir}")
        files = find_feature_files(repo, args.feature, args.limit)
        print("feature_files:")
        print("\n".join(f"  {path.relative_to(repo)}" if path.is_relative_to(repo) else f"  {path}" for path in files) or "  -")

    print("read_next:")
    profile = SKILL_DIR / "references" / "project-profile.local.md"
    print(f"  {'references/project-profile.local.md' if profile.exists() else 'references/project-profile.md'}")
    if args.feature:
        print(f"  docs/{args.feature}/01-frontend-tech-design.md")
        print(f"  docs/{args.feature}/workflow-state.yaml")
    print("  nearest same-module page + API + route")


if __name__ == "__main__":
    try:
        main()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
