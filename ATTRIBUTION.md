# Attribution & Licenses

Webwright-Clockbrowser is a combination of two upstream open-source projects.
It is an independent integration and is **not** affiliated with, endorsed by, or
sponsored by Microsoft or CloakHQ.

## 1. Webwright — the agent harness (vendored & modified)

- Source: https://github.com/microsoft/Webwright
- Author: Microsoft Research (Lu, Xu, Huang, Awadallah)
- License: MIT (© Microsoft Corporation) — see [`LICENSE`](LICENSE)

Webwright's `src/webwright/` tree is vendored into this repository and modified.
The modifications (CloakBrowser stealth browser modes, config overlays, and
prompt edits) are described in the project [`README.md`](README.md) and remain
under the MIT License.

## 2. CloakBrowser — the stealth browser (upstream dependency)

- Source: https://github.com/CloakHQ/CloakBrowser
- Author: CloakHQ
- Wrapper license: MIT (© 2026 CloakHQ)
- **Binary license: separate.** The compiled stealth Chromium binary that
  `cloakbrowser` downloads at runtime is distributed under CloakHQ's
  **CloakBrowser Binary License v1.0**, *not* MIT. Review CloakHQ's
  `BINARY-LICENSE.md` before any commercial or redistribution use:
  https://github.com/CloakHQ/CloakBrowser/blob/main/BINARY-LICENSE.md

CloakBrowser is consumed as a normal PyPI dependency (`pip install cloakbrowser`)
rather than vendored, so its auto-updating stealth binary stays current. No
CloakBrowser source code is copied into this repository.

## 3. Chromium

CloakBrowser's binary is built on Chromium, which is licensed under the BSD
3-Clause License and other licenses. See https://www.chromium.org/.

## Responsible use

This project is for legitimate automation, testing, and research. Respect each
site's Terms of Service, `robots.txt`, rate limits, and applicable law. Bot-
detection evasion is provided for authorized use only; you are responsible for
how you use it.
