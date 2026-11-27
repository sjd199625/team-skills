#!/usr/bin/env python3
"""生成独立 Playwright 回归测试包，不安装依赖。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        print(f"跳过 {path}（已存在）")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"创建 {path}")


def package_json() -> str:
    data = {
        "name": "iot-e2e",
        "private": True,
        "scripts": {
            "test": "playwright test",
            "test:headed": "playwright test --headed",
            "show-report": "playwright show-report",
        },
        "devDependencies": {"@playwright/test": "^1.49.0"},
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def config_ts(base_url: str, device: str) -> str:
    return f"""import {{ defineConfig, devices }} from '@playwright/test';

export default defineConfig({{
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [['list'], ['html', {{ open: 'never' }}]],
  use: {{
    baseURL: process.env.BASE_URL || {json.dumps(base_url)},
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  }},
  projects: [
    {{
      name: 'chromium',
      use: {{ ...devices[{json.dumps(device)}] }},
    }},
  ],
}});
"""


def smoke_spec() -> str:
    return """import { test, expect } from '@playwright/test';

test('页面可以打开', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('body')).toBeVisible();
});
"""


def readme(base_url: str, device: str) -> str:
    return f"""# E2E 测试包

- 目标地址：`{base_url}`
- 设备：`{device}`
- 运行：`npm test`
- 指定地址：`BASE_URL=<url> npm test`

首次使用前先获得确认，再安装依赖：

```bash
npm install
npx playwright install chromium
```

登录态优先使用 `storageState`，不要把账号密码或 cookie 提交到仓库。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="tests/e2e", help="测试包目录")
    parser.add_argument("--base-url", required=True, help="测试环境地址")
    parser.add_argument("--device", default="Desktop Chrome", help="Playwright 设备名")
    parser.add_argument("--force", action="store_true", help="覆盖已存在文件")
    args = parser.parse_args()

    target = Path(args.dir).expanduser().resolve()
    if target.exists() and not target.is_dir():
        die(f"目标不是目录：{target}")
    target.mkdir(parents=True, exist_ok=True)

    write_file(target / "package.json", package_json(), args.force)
    write_file(target / "playwright.config.ts", config_ts(args.base_url, args.device), args.force)
    write_file(target / "tests" / "smoke.spec.ts", smoke_spec(), args.force)
    write_file(target / "fixtures" / ".gitkeep", "", args.force)
    write_file(target / "README.md", readme(args.base_url, args.device), args.force)

    print("完成：只生成文件，没有安装依赖。")
    print("确认后执行：cd <dir> && npm install && npx playwright install chromium")


if __name__ == "__main__":
    main()
