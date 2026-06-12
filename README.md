# Webwright‑Clockbrowser

**A state‑of‑the‑art web‑agent brain in a bot‑proof body.**

Webwright‑Clockbrowser fuses two open‑source projects that solve *different
halves* of the same problem:

| Layer | Project | What it contributes |
|-------|---------|---------------------|
| 🧠 **The brain** — how the agent decides & acts | [**Webwright**](https://github.com/microsoft/Webwright) (Microsoft Research) | A *code‑as‑action* web‑agent harness. The model writes free‑form Playwright Python, runs it, inspects ARIA + screenshots, and repairs — SOTA on Online‑Mind2Web (86.7%) and long‑horizon Odysseys (60.1%). |
| 🥷 **The body** — what executes those actions | [**CloakBrowser**](https://github.com/CloakHQ/CloakBrowser) (CloakHQ) | A stealth Chromium with **58 source‑level C++ fingerprint patches** that pass Cloudflare Turnstile, reCAPTCHA v3 (0.9), FingerprintJS, and BrowserScan — plus `humanize` mouse/keyboard/scroll. |

Stock Webwright drives a vanilla Playwright browser that bot‑detection systems
flag instantly. Stock CloakBrowser is a brilliant browser with no brain. This
repo wires Webwright's agent loop to launch CloakBrowser instead of vanilla
Playwright — so a SOTA agent can now operate on sites it could never reach
before, without tripping the bouncer at the door.

> ⚠️ **For authorized automation, testing, and research only.** Respect each
> site's Terms of Service, `robots.txt`, rate limits, and the law. See
> [ATTRIBUTION.md](ATTRIBUTION.md).

---

## Why this exists

Two independent observations made the combine almost inevitable:

1. **Webwright is the best *decision* layer, but it's blind to detection.** Its
   "browser is disposable, the workspace (code + logs + screenshots) is the
   state" philosophy makes it robust and token‑efficient — but the browser it
   launches is a stock Playwright Chromium that announces `navigator.webdriver =
   true`, ships a `HeadlessChrome` UA, and has a TLS fingerprint no real user
   has. On any protected site the agent's brilliance is wasted: it gets a
   CAPTCHA wall or a 403 before it can act.

2. **CloakBrowser is the best *evasion* layer, but it's just a launcher.** It
   ships a real Chromium with fingerprints patched at the C++ source level
   ("antibot systems score it as a normal browser — because it *is* a normal
   browser"), but it has no agent: you still have to tell it what to do.

They live at **orthogonal layers**, so composing them is addition, not
conflict. And there's a bonus: stock Webwright had to fall back to **Firefox**
because Playwright **Chromium** hit `ERR_HTTP2_PROTOCOL_ERROR` on Akamai‑class
sites (a TLS/H2 fingerprinting artifact). CloakBrowser's ja3/ja4/akamai
fingerprint is *identical to real Chrome*, so that error disappears — the agent
gets a real Chromium engine **and** evasion at the same time.

**The result:** Webwright's code‑as‑action loop, ARIA perception, and
vision‑based self‑reflection — now executing inside a browser that doesn't get
caught.

---

## What changed vs. upstream Webwright

The integration is deliberately small and lives entirely inside the vendored
Webwright tree:

- **`src/webwright/environments/local_browser.py`** — two new `browser_mode`s:
  - `cloak_launch` — a fresh stealth Chromium per run (in‑process).
  - `cloak_persistent` — stealth Chromium backed by a persistent profile dir
    (keeps cookies/sessions, bypasses incognito detection).

  Both call CloakBrowser's `launch_async` / `launch_persistent_context_async`
  with `humanize=True`, so the live agent loop inherits **fingerprint stealth +
  behavioral humanization** transparently. Everything else (ARIA capture,
  screenshots, step execution, observation format) is unchanged.
- **`src/webwright/config/cloak_browser.yaml`** — Path 1 overlay (in‑process).
- **`src/webwright/config/cloak_cdp.yaml`** — Path 2 overlay (out‑of‑process via
  `cloakserve`).
- **`src/webwright/config/base.yaml`** + **`skills/webwright/…`** — Path 3:
  the prompt that teaches the agent to write `final_script.py` now instructs it
  to launch via `from cloakbrowser import launch_async` instead of vanilla
  Playwright.
- **`pyproject.toml`** — adds `cloakbrowser` as a dependency.

CloakBrowser itself is **not vendored** — it's a normal PyPI dependency, so its
auto‑updating stealth binary always stays current (its single most important
feature).

---

## The three integration paths

This build ships all three ways to wire the two tools, matching Webwright's two
execution modes:

### Path 1 — In‑process live loop *(recommended; stealth + humanize)*
Webwright's live‑browser environment launches the stealth binary directly.

```bash
pip install -e .                       # pulls in cloakbrowser; binary auto-downloads
python -m webwright.run.cli \
  -c base.yaml -c cloak_browser.yaml -c model_claude.yaml \
  -t "Open https://bot.incolumitas.com and report the detection verdict"
```

### Path 2 — Out‑of‑process via `cloakserve` (CDP)
Run CloakBrowser as a stealth CDP server; Webwright attaches via its existing
`local_cdp` mode. Fingerprint stealth travels over CDP for free; `humanize`
does **not** (it's wrapper‑level) — use Path 1 if you need behavioral mimicry.

```bash
docker run -d --name cloak -p 127.0.0.1:9222:9222 \
  cloakhq/cloakbrowser cloakserve --headless=false
python -m webwright.run.cli \
  -c base.yaml -c cloak_cdp.yaml -c model_claude.yaml \
  -t "Open https://browserscan.net/bot-detection and report the verdict"
```

### Path 3 — Script‑mode prompt (agent writes stealth scripts)
In Webwright's benchmark/script mode the model authors a reusable
`final_script.py`. The prompt now makes that script launch CloakBrowser, so the
generated artifact is stealthy and re‑runnable on its own.

```bash
python -m webwright.run.cli \
  -c base.yaml -c model_openai.yaml \
  -t "Search Google Flights SEA->JFK 2026-08-15 to 2026-08-20" \
  --start-url https://www.google.com/flights --task-id demo -o outputs/default
```

---

## Quick start

```bash
# 1. Install (Python 3.10+). Pulls in cloakbrowser; the stealth Chromium binary
#    (~200MB) auto-downloads on first launch.
pip install -e .

# 2. No-LLM smoke test — proves the combine end to end.
python examples/cloak_smoke_test.py
#    Expect: webdriver=False, plugins>0, chrome='object', UA "Chrome/..." not "HeadlessChrome".

# 3. Full agent run — set your model key, then use Path 1.
export ANTHROPIC_API_KEY=...           # or OPENAI_API_KEY with model_openai.yaml
python -m webwright.run.cli \
  -c base.yaml -c cloak_browser.yaml -c model_claude.yaml \
  -t "Go to https://nowsecure.nl and tell me whether the page loaded past the challenge"
```

### Going against protected sites
Add a residential proxy, match geo, and run headed:

```yaml
# in cloak_browser.yaml -> environment:
cloak_proxy: "http://user:pass@residential-host:port"
cloak_geoip: true        # match timezone/locale + WebRTC IP to the proxy exit
headless: false          # some sites still flag headless even with C++ patches
```

---

## How it fits together

```
        ┌──────────────────────────────────────────────┐
        │  WEBWRIGHT  — the brain / control loop         │
        │  • model writes free-form Playwright Python    │
        │  • ARIA accessibility tree = primary perception│
        │  • screenshots + image_qa + self_reflection    │
        │    (vision) verify before declaring done       │
        └───────────────────────┬──────────────────────┘
                                 │ launches / drives
                                 ▼
        ┌──────────────────────────────────────────────┐
        │  CLOAKBROWSER — the body / transport           │
        │  • stealth Chromium, 58 C++ fingerprint patches│
        │  • humanize: human mouse / keyboard / scroll   │
        │  • proxy + geoip + persistent stealth profiles │
        └──────────────────────────────────────────────┘
```

The agent never has to know it's driving a stealth browser — it issues the same
Playwright calls; the evasion is in the binary underneath.

---

## Caveats & honest limits

- **Headless still leaks on the hardest sites.** The C++ patches cover
  fingerprints, but a few behavioral detectors still flag headless. Run headed
  (`headless: false`, under Xvfb in a container) for maximum evasion.
- **`humanize` is in‑process only.** Over CDP (Path 2) you get fingerprint
  stealth but not behavioral humanization. Path 1 gives you both.
- **Proxies matter.** CloakBrowser doesn't rotate proxies or solve CAPTCHAs —
  bring your own *residential* IPs for protected targets.
- **Identity vs. disposability.** Webwright's default is a fresh browser per
  run. For logged‑in flows use `cloak_persistent` + a profile dir (or a stable
  `cloakserve` fingerprint seed).
- **Binary license.** The stealth Chromium binary ships under CloakHQ's own
  Binary License (not MIT) — see [ATTRIBUTION.md](ATTRIBUTION.md).

---

## Credits

Built by combining the work of others — see [ATTRIBUTION.md](ATTRIBUTION.md).

- **Webwright** © Microsoft Corporation — MIT.
- **CloakBrowser** © CloakHQ — MIT wrapper; binary under CloakBrowser Binary License.

This is an independent integration, not affiliated with or endorsed by Microsoft
or CloakHQ.
