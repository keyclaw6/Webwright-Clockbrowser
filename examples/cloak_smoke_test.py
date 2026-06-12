"""Webwright-Clockbrowser smoke test — no LLM required.

Drives Webwright's live-browser environment in CloakBrowser stealth mode
(browser_mode="cloak_launch") directly, the same way the agent loop would,
and prints the key automation signals plus the page's own verdict. This proves
the combine end to end without needing a model API key.

Run:
    pip install -e .
    python examples/cloak_smoke_test.py
    # optionally against a different detector:
    python examples/cloak_smoke_test.py https://browserscan.net/bot-detection
"""

from __future__ import annotations

import sys
from pathlib import Path

from webwright.environments.local_browser import LocalBrowserEnvironment

START_URL = sys.argv[1] if len(sys.argv) > 1 else "https://bot.incolumitas.com"

# The agent normally writes this Python; here we issue it directly as one step.
PROBE = (
    "signals = await page.evaluate('''() => ({\n"
    "  webdriver: navigator.webdriver,\n"
    "  plugins: navigator.plugins.length,\n"
    "  chrome: typeof window.chrome,\n"
    "  languages: navigator.languages,\n"
    "  ua: navigator.userAgent,\n"
    "})''')\n"
    "print('AUTOMATION SIGNALS:', signals)\n"
)


def main() -> int:
    env = LocalBrowserEnvironment(
        browser_mode="cloak_launch",
        headless=True,            # flip to False (under Xvfb) for hardest sites
        cloak_humanize=True,
        cloak_stealth_args=True,
        start_url=START_URL,
        output_dir=Path("outputs/cloak_smoke"),
    )

    print(f"[1/3] Launching CloakBrowser stealth Chromium -> {START_URL}")
    env.prepare(task="stealth smoke test", start_url=START_URL)

    print("[2/3] Probing automation signals through the live page")
    result = env.execute({"python_code": PROBE})
    obs = result["observation"]
    print("    URL  :", obs.get("url"))
    print("    TITLE:", obs.get("title"))
    print("    OK   :", obs.get("success"))
    if result.get("output"):
        print("   ", result["output"].strip())
    if obs.get("exception"):
        print("    EXC :", obs["exception"])

    print("[3/3] Closing")
    env.close()
    print("\nExpected on a real stealth browser: webdriver=False, plugins>0, "
          "chrome='object', UA contains 'Chrome/' (not 'HeadlessChrome').")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
