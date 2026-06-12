<p align="center">
  <img src="https://pub.hyperagent.com/api/published/pbf01KTXPDQTQ_89DH58ZP2APR11JR/hero.png" alt="Webwright × CloakBrowser" width="820">
</p>

<h1 align="center">Webwright&nbsp;×&nbsp;CloakBrowser</h1>

<p align="center">
  <b>A state-of-the-art web-agent brain in a bot-proof body.</b><br>
  <sub>Webwright decides &amp; acts. CloakBrowser makes sure nobody notices.</sub>
</p>

<p align="center">
  <a href="https://github.com/microsoft/Webwright">🧠 Webwright repo</a> &nbsp;•&nbsp;
  <a href="https://github.com/CloakHQ/CloakBrowser">🥷 CloakBrowser repo</a> &nbsp;•&nbsp;
  <a href="#quick-start">🚀 Quick start</a> &nbsp;•&nbsp;
  <a href="#why-combine-them">❓ Why</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-%E2%89%A53.10-blue" alt="python">
  <img src="https://img.shields.io/badge/engine-stealth%20Chromium-1c1f26" alt="engine">
  <img src="https://img.shields.io/badge/perception-ARIA%20%2B%20vision-3F6FF1" alt="perception">
  <img src="https://img.shields.io/badge/license-MIT%20(see%20notice)-green" alt="license">
</p>

---

## The one-sentence version

Two open-source projects each solve **one half** of "an AI that can use the web."
This repo bolts them together:

> **[Webwright](https://github.com/microsoft/Webwright)** is the best *brain* — it
> decides what to do and writes the code to do it.
> **[CloakBrowser](https://github.com/CloakHQ/CloakBrowser)** is the best *body* —
> a real browser that bot-detectors can't tell apart from a human's.
>
> **Webwright × CloakBrowser** = a top-tier web agent that can actually operate on
> protected sites, because it never gets flagged as a bot.

---

## Meet the two halves

<table>
<tr>
<th width="50%">🧠 Webwright — the brain</th>
<th width="50%">🥷 CloakBrowser — the body</th>
</tr>
<tr>
<td valign="top">

**[github.com/microsoft/Webwright](https://github.com/microsoft/Webwright)**
*(Microsoft Research · MIT)*

A **code-as-action** web-agent harness. Instead of guessing pixel clicks, the
model writes real Playwright code, runs it, reads the page, and fixes its own
mistakes — like a human engineer iterating on a script.

**Why it's great**
- 🏆 **State of the art** — 86.7% on Online-Mind2Web, 60.1% on long-horizon
  Odysseys (+15.6 pts over the prior best).
- 🧩 **Robust** — writes loops & waits in code instead of brittle one-click-at-a-time
  guesses, so long multi-step tasks don't fall apart.
- 💸 **Efficient** — reads the page's accessibility tree (text) and only looks at
  screenshots when it needs to; far fewer tokens.
- 🔁 **Reusable** — every task becomes a re-runnable script you can keep.

**Its weakness:** it drives a *normal* Playwright browser that bot-detectors flag
on sight (`navigator.webdriver = true`, "HeadlessChrome", a fake TLS fingerprint).
On a protected site it gets a CAPTCHA wall before it can even start.

</td>
<td valign="top">

**[github.com/CloakHQ/CloakBrowser](https://github.com/CloakHQ/CloakBrowser)**
*(CloakHQ · MIT wrapper)*

A **stealth Chromium**. The fingerprints are patched at the **C++ source level**
and compiled into the binary — not a fragile JavaScript hack. Detectors score it
as a normal browser *because it is one*.

**Why it's great**
- 🛡️ **Passes the hard checks** — Cloudflare Turnstile, reCAPTCHA v3 (**0.9**,
  human-level), FingerprintJS, BrowserScan, 30+ detectors.
- 🧬 **58 source-level patches** — canvas, WebGL, audio, GPU, WebRTC, and a TLS
  fingerprint **identical to real Chrome**.
- 🚶 **`humanize`** — human-like mouse curves, typing rhythm, and scrolling.
- 🔌 **Drop-in** — it's the same Playwright API, just a different browser binary.

**Its weakness:** it's *only* a browser. It has no brain — you still have to tell
it exactly what to do, step by step.

</td>
</tr>
</table>

---

## Why combine them

They fix **each other's only weakness**, and they live at completely different
layers — so combining them is pure addition, no conflict:

```
        ┌─────────────────────────────────────────────┐
        │  🧠 WEBWRIGHT  — decides & acts                │
        │     writes Playwright code, reads the page,   │
        │     verifies with screenshots, repairs itself │
        └───────────────────────┬─────────────────────┘
                                 │  drives
                                 ▼
        ┌─────────────────────────────────────────────┐
        │  🥷 CLOAKBROWSER — executes, undetected        │
        │     stealth Chromium + humanized behaviour    │
        └─────────────────────────────────────────────┘
```

There's even a happy accident: stock Webwright had to fall back to **Firefox**
because Playwright **Chromium** tripped `ERR_HTTP2_PROTOCOL_ERROR` on
Akamai-class sites (a TLS fingerprinting artifact). CloakBrowser's TLS
fingerprint matches real Chrome, so that error simply disappears — you get a
real Chromium engine **and** full evasion at once.

---

## What this repo actually is

Webwright's harness (vendored & lightly modified), wired to launch CloakBrowser
instead of a vanilla browser. **CloakBrowser is a normal dependency** (`pip install
cloakbrowser`) — not copied in — so its auto-updating stealth binary always stays
current. The change is deliberately tiny:

- **`src/webwright/environments/local_browser.py`** — new `browser_mode`s
  `cloak_launch` (fresh stealth browser per run) and `cloak_persistent` (keeps
  cookies/sessions), launched with `humanize=True`.
- **`src/webwright/config/cloak_browser.yaml`** — turn it on with one extra flag.
- Everything else about Webwright — its loop, perception, and self-verification —
  is unchanged.

> Two optional alternate wirings are also included for advanced setups (running the
> browser as a separate `cloakserve` process, and teaching the agent to emit
> stealth scripts). You can ignore them — the default above is all you need.

---

## Quick start

```bash
# 1. Install (Python 3.10+). Pulls in cloakbrowser; the stealth Chromium
#    binary (~200 MB) auto-downloads on first launch.
pip install -e .

# 2. Prove the stealth works — no LLM key needed.
python examples/cloak_smoke_test.py
#    Expect: webdriver=False, plugins>0, chrome='object', UA "Chrome/..." (not "HeadlessChrome").

# 3. Run a real agent task. Set your model key, then go.
export ANTHROPIC_API_KEY=...        # or OPENAI_API_KEY with model_openai.yaml
python -m webwright.run.cli \
  -c base.yaml -c cloak_browser.yaml -c model_claude.yaml \
  -t "Open https://bot.incolumitas.com and report the detection verdict"
```

**Against protected sites**, add a residential proxy and run headed (in
`cloak_browser.yaml`):

```yaml
environment:
  cloak_proxy: "http://user:pass@residential-host:port"
  cloak_geoip: true     # match timezone/locale + WebRTC IP to the proxy's exit
  headless: false       # some sites still flag headless even with C++ patches
```

---

## Verified working

The combine was tested end to end driving the stealth browser **through
Webwright's environment**:

| Check | Result |
|-------|--------|
| Launch CloakBrowser via Webwright's `cloak_launch` | ✅ |
| `navigator.webdriver` | ✅ `false` |
| `navigator.plugins` / `window.chrome` | ✅ `5` / `object` |
| User-Agent | ✅ `Chrome/146.0.0.0` (not `HeadlessChrome`) |
| Humanized ARIA-role click + ARIA snapshot + screenshot capture | ✅ |

---

## Honest limits

- **Headless still leaks on the hardest sites** — run headed (`headless: false`,
  under Xvfb in a container) for maximum evasion.
- **Bring your own residential proxies** — CloakBrowser doesn't rotate proxies or
  solve CAPTCHAs; it *prevents* them.
- **For logged-in flows**, use `cloak_persistent` so cookies/sessions survive.

---

## Credits & license

This is an independent integration — **not** affiliated with or endorsed by
Microsoft or CloakHQ. It stands entirely on their work:

- **[Webwright](https://github.com/microsoft/Webwright)** © Microsoft Corporation — MIT.
- **[CloakBrowser](https://github.com/CloakHQ/CloakBrowser)** © CloakHQ — MIT wrapper;
  the stealth binary ships under CloakHQ's own Binary License.

Full details in **[ATTRIBUTION.md](ATTRIBUTION.md)**.

> ⚖️ **Use responsibly.** For legitimate automation, testing, and research only.
> Respect each site's Terms of Service, `robots.txt`, rate limits, and the law.
