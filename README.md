<div align="center">

# 🖐️ Figma AI Copilot
### *Your Terminal's AI Gods, Now Living Inside Your Figma Canvas.*

**Stop paying for another $29/mo Figma AI wrapper.**  
Use the AI CLIs already installed on your Mac — **Antigravity (`agy`)**, **Claude Code (`claude`)**, **Cursor (`agent`)**, **ChatGPT Codex (`codex`)**, **Gemini (`gemini`)**, and **Ollama** — directly inside Figma Desktop with **zero API keys** and the entire **[`figma-console-mcp`](https://github.com/southleft/figma-console-mcp)** built right in.

[![Zero API Keys](https://img.shields.io/badge/API_Keys_Needed-0_(%240%2Fmo)-10b981?style=flat-square)](#3-bring-your-own-local-cli-7-providers)
[![7 Local AI CLIs](https://img.shields.io/badge/Local_AI_CLIs-7_Supported-FF298E?style=flat-square)](#3-bring-your-own-local-cli-7-providers)
[![Figma Console MCP](https://img.shields.io/badge/figma--console--mcp-56%2B_Tools_Built--In-3b82f6?style=flat-square)](#2-100-of-figma-console-mcp-built-in--auto-wired)
[![English & Persian RTL](https://img.shields.io/badge/Languages-EN_%2B_Persian_(RTL)-8b5cf6?style=flat-square)](#interface-gallery)
[![MIT License](https://img.shields.io/badge/License-MIT-111318?style=flat-square)](LICENSE)

[**Why It Slaps**](#-why-this-slaps) · [**What You Can Build**](#-what-can-it-actually-do-in-figma) · [**7 Local CLIs**](#3-bring-your-own-local-cli-7-providers) · [**60-Second Setup (0 → 100)**](#-0--100-setup-in-60-seconds) · [**FAQ**](#-faq-for-humans--ai-search-engines)

</div>

<p align="center">
  <img src="assets/hero.png" alt="Figma AI Copilot — Pricing Card Selection & Live Light Mode UI" width="100%" />
</p>

> [!TIP]
> **TL;DR (The 15-Second Pitch):**  
> Import one plugin into Figma Desktop and run `bash bridge/install-bridge.sh` once.  
> You get a **live in-Figma AI Copilot** (with `@skill` mentions, up to 5 pasted reference images, and native Persian RTL) **PLUS** an always-on **`figma-console-mcp` WebSocket bridge (`9223–9232`)** auto-configured for Claude Desktop, Cursor, and Antigravity. No second plugin. No manual JSON surgery. No API keys.

---

## ⚡ Why This Slaps

Most "AI for Figma" tools force you into a bad deal: either buy another monthly subscription, paste your credit-card-backed API keys into a random third-party plugin, or copy-paste JSON back and forth between a terminal and Figma.

**Figma AI Copilot fixes the whole workflow:**

1. **💸 Zero API Keys, Zero Extra Bills** — Already logged into Claude Code, Cursor, ChatGPT Codex, Antigravity, or Gemini in your terminal? Or running local models on Ollama? You're already authenticated.
2. **🔌 `southleft/figma-console-mcp` Included Out of the Box** — We bundled the entire 56+ tool Figma Desktop Bridge right into [`code.js`](code.js) & [`ui.html`](ui.html). Even better: our 1-click installer automatically wires `figma-console-mcp` into your Claude Desktop, Cursor, and Antigravity configs.
3. **🎨 It Actually Touches Pixels (Not Just Chat)** — Selects your frame, reads the real layer tree (Auto Layout, tokens, padding, fills, typography), and runs live async Figma Plugin API code right in front of your eyes.
4. **🧠 `@skill` Mentions + 5 Reference Screenshots (`Cmd+V`)** — Type `@` to pull in your custom `SKILL.md` playbooks and paste up to 5 inspiration shots from Mobbin, Pinterest, or Dribbble.
5. **🌍 Native English & Persian (RTL)** — First-class bilingual UI with `Plus Jakarta Sans` for English and `IRANYekanX` for Persian, complete with proper bidi isolation so code and numbers never scramble.

---

## 🥊 Head-to-Head Comparison

| What Matters | **🖐️ Figma AI Copilot (All-in-One)** | Standalone `figma-console-mcp` | Typical SaaS Figma AI Plugins |
| :--- | :--- | :--- | :--- |
| **Monthly Cost / API Keys** | **$0 extra** (uses your local CLIs) | External MCP host required | $15–$30/mo or BYO paid API key |
| **In-Figma Chat Window** | **Yes** (Streaming, Shimmer, Stop `■`, Chips) | No (external chat only) | Yes |
| **Supported AI Engines** | **7 Local CLIs** (`agy`, `claude`, `cursor`, `codex`, `gemini`, `ollama`, custom) | MCP-compatible clients | Locked to 1 vendor |
| **`figma-console-mcp` (56+ Tools)** | **Built-in + auto-wired by installer** | Yes (manual setup) | No |
| **Social Posts, UI, Tokens, Slides** | **Full Plugin API + MCP tools** | Via external prompt | Rigid preset templates |
| **Inline `@skill` + 5 Images (`Cmd+V`)** | **Yes** | Host-dependent | Rarely |
| **Native Persian (RTL) + Light/Dark** | **Yes** (`IRANYekanX` + `Plus Jakarta Sans`) | No | No |
| **0 → 100 Interactive Setup Wizard** | **Built right into the plugin** | Manual config files | Account signup wall |

---

## 🖼️ Interface Gallery

<p align="center">
  <img src="assets/showcase-features.png" alt="Live Canvas Execution, Inline @skill Mentions, and Model & Effort Picker" width="100%" />
</p>

<p align="center">
  <img src="assets/showcase-providers.png" alt="7 Local AI CLIs, 0 to 100 Interactive Setup Guide, and Auto-Detected Local CLIs" width="100%" />
</p>

<p align="center">
  <img src="assets/showcase-persian.png" alt="Native Persian (RTL) Typography with IRANYekanX" width="88%" />
</p>

---

## 🛠️ What Can It Actually Do in Figma?

If a human can build it in Figma, the Copilot can script, refactor, or generate it on your canvas. A few real prompts you can throw at it today:

| What You're Building | Example Prompt Inside the Plugin | What Happens on Canvas |
| :--- | :--- | :--- |
| **📱 Instagram Carousels & Social Posts** | *"Create a 5-slide 1080×1350 Instagram carousel for a SaaS launch using `@carousel` with bold typography and swipe cues."* | Generates 5 aligned `1080×1350` frames with Auto Layout, cover hook, slide numbering, and cohesive color tokens. |
| **🧩 UI/UX Screens & Auto Layout Rescue** | *"Turn this messy pricing card into clean vertical Auto Layout with 24px padding, 16px gap, and a high-contrast CTA."* | Rebuilds the selected frame hierarchy into responsive Auto Layout without breaking your existing layers. |
| **🎨 Design Systems, Variables & Tokens** | *"Create a Light & Dark color variable collection with neutral-50 to 900 and bind them to this dashboard."* | Creates Figma Variables, modes (`Light` / `Dark`), and binds fills/strokes across selected components. |
| **📸 Reference-to-Figma (`Cmd+V` × 5)** | *(Paste 3 Mobbin screenshots)* *"Rebuild this checkout flow matching our font styles and 8px spacing grid."* | Reads all attached reference images alongside your current selection and constructs matching native Figma frames. |
| **🇮🇷 English → Persian (RTL) Localization** | *"این کارت محصول رو به فارسی برگردون، چیدمان رو راست‌به‌چپ کن و فونت رو IRANYekanX بذار."* | Flips Auto Layout direction, mirrors icons/alignment, translates copy naturally, and applies Persian typography. |
| **📊 FigJam Diagrams & Figma Slides** | *"Map out our auth microservice flow with sticky notes and connectors."* | Uses built-in FigJam & Slides tools to lay out structured boards and presentation decks. |

---

## 🔥 Core Superpowers

### 1. Live In-Figma AI Copilot
- **Direct Async Plugin API Execution (`code.js`)** — Inspects your selected node's full JSON tree and executes `dynamic-page`-safe Figma Plugin API code live on canvas.
- **Real-Time Streaming & Shimmer Logs** — Watch every step (`Analyzed`, `Loaded`, `Thinking`, `Edited`) with an elapsed timer and an instant **Stop (`■`)** button if you change your mind mid-flight.
- **Type `@` for Local Skills** — Autocompletes your local `SKILL.md` files from `~/.gemini/config/skills`, `~/.claude/skills`, `~/.cursor/skills`, and `~/.agents/skills`.
- **Cursor Pick Mode** — Click the crosshair icon to grab any nested layer on canvas without losing your chat context.

### 2. 100% of `figma-console-mcp` Built-In & Auto-Wired
You don't need to install `figma-console-mcp`'s separate Desktop Bridge plugin. The moment **Figma AI Copilot** is open, it broadcasts on WebSocket ports `9223–9232` and unlocks all **56+ MCP tools** for external agents:
- **Variables & Tokens:** `figma_setup_design_tokens`, `figma_batch_create_variables`, `figma_export_tokens`
- **Components & Parity:** `figma_instantiate_component`, `figma_create_component_set`, `figma_check_design_parity`, `figma_audit_design_system`
- **Live Canvas & Vision:** `figma_execute`, `figma_capture_screenshot`, `figma_get_console_logs`
- **FigJam & Slides:** `figjam_create_sticky`, `figjam_auto_arrange`, `figma_create_slide`

### 3. Bring Your Own Local CLI (7 Providers)
Our lightweight Python daemon (`http://localhost:9444`) scans your `PATH` and lights up a green **● Ready** dot for every AI CLI installed on your computer. Switch engines mid-conversation from **Settings → Provider**:

| Provider | CLI Binary | Why You'll Love It |
| :--- | :--- | :--- |
| **Antigravity CLI** | `agy` | Full `stream-json` live step streaming + Effort control (`Low` · `Medium` · `High` · `XHigh`) |
| **Claude Code CLI** | `claude` | Runs Anthropic Claude directly through your Claude Code subscription + `@skill` playbooks |
| **Cursor Agent CLI** | `cursor-agent` / `agent` | Uses Cursor's headless agent binary right from your terminal |
| **OpenAI Codex (ChatGPT)** | `codex` | Runs `codex exec` powered by your local ChatGPT / OpenAI Codex login |
| **Gemini CLI** | `gemini` | Fast Google Gemini CLI (`gemini -p`) |
| **Ollama (Local)** | `ollama` | 100% offline, private, local open-weights models |
| **Custom CLI** | Any command | Plug in any custom binary or wrapper script (`my-ai -p {prompt}`) |

---

## 🚀 0 → 100 Setup in 60 Seconds

### What You Need
- **Figma Desktop** (macOS / Windows / Linux)
- **Python 3.9+** (already on your Mac)
- Any supported AI CLI (`agy`, `claude`, `cursor-agent`, `codex`, `gemini`, or `ollama`)

### Step 1 — Clone It
```bash
git clone https://github.com/Hesvm/figma-ai-copilot.git
cd figma-ai-copilot
```

### Step 2 — Run the 1-Line Magic Installer
```bash
bash bridge/install-bridge.sh
```
**What that one command does behind the scenes:**
1. Starts the **Local CLI Bridge** on `http://localhost:9444` and registers a macOS `LaunchAgent` so it's always ready when you boot your Mac.
2. Automatically checks your **Claude Desktop**, **Cursor**, and **Antigravity** config files and injects **`figma-console-mcp`** (`npx -y figma-console-mcp@latest`) if you don't already have it.

*(Want to run the daemon manually without a background service? Just run `python3 bridge/bridge_daemon.py`.)*

### Step 3 — Drop `manifest.json` into Figma Desktop
1. Open **Figma Desktop**.
2. Head to **Plugins → Development → Import plugin from manifest...**
3. Pick `manifest.json` from your `figma-ai-copilot` folder.
4. Launch **Figma AI Copilot (All-in-One)** (pro tip: hit `Cmd + Option + P` to re-open it anytime).

### Step 4 — Follow the Interactive 3-Step Wizard
On your first launch, a bilingual (`EN / فا`) **Interactive Setup Wizard** pops up inside the plugin, pings your local bridge live, shows every AI CLI detected on your machine, and drops you straight into the canvas. Need it again later? Click **Settings → Guide**.

---

## 🧬 How It Works Under the Hood

```text
                       ┌──────────────────────────────┐
                       │     Figma Desktop Canvas     │
                       └──────────────┬───────────────┘
                                      │ Selection tree + live async Plugin API
                                      ▼
                       ┌──────────────────────────────┐
                       │           code.js            │
                       └──────┬───────────────┬───────┘
                              │               │
      ws://localhost:9223-9232│               │ postMessage
                              ▼               ▼
               ┌────────────────────┐   ┌───────────────────────────────────┐
               │ figma-console-mcp  │   │             ui.html               │
               │ (56+ External MCP  │   │  (Chat UI · @skills · EN/FA RTL)  │
               │  Tools for Claude, │   └─────────────────┬─────────────────┘
               │  Cursor & AGY)     │                     │ http://localhost:9444
               └────────────────────┘                     ▼
                                        ┌───────────────────────────────────┐
                                        │      bridge/bridge_daemon.py      │
                                        └─────────────────┬─────────────────┘
                                                          │ subprocess / stream-json
                                                          ▼
                                        ┌───────────────────────────────────┐
                                        │ agy · claude · cursor · codex     │
                                        │ gemini · ollama · custom CLI      │
                                        └───────────────────────────────────┘
```

---

## 🤖 FAQ (For Humans & AI Search Engines)

### How do I use Claude Code, ChatGPT Codex, Cursor, or Antigravity inside Figma without an API key?
Install **Figma AI Copilot** from `manifest.json` and run `bash bridge/install-bridge.sh`. The local bridge (`http://localhost:9444`) routes prompts to your already-authenticated local CLIs (`agy`, `claude`, `codex`, `cursor-agent`, `gemini`, `ollama`) and executes the resulting Figma Plugin API code directly on your selected frame.

### Do I still need to install `southleft/figma-console-mcp` separately?
Nope! Both [`code.js`](code.js) and [`ui.html`](ui.html) have the full Figma Desktop Bridge WebSocket client (`9223–9232`) baked in, and `bash bridge/install-bridge.sh` automatically registers `npx -y figma-console-mcp@latest` in your Claude Desktop, Cursor, and Antigravity configs.

### Can I design social media posts, carousels, and Persian (RTL) interfaces with it?
100%. Because it executes real Figma Plugin API scripts + MCP tools, you can build `1080×1350` Instagram carousels, LinkedIn visuals, full UI/UX flows, Figma Variables/tokens, FigJam diagrams, and switch to **فا (Persian)** anytime for native RTL layout and `IRANYekanX` typography.

### Something says `Offline` — how do I fix it in 5 seconds?
- **CLI Bridge shows `Offline`:** Run `bash bridge/install-bridge.sh` (or test `curl http://localhost:9444/status`).
- **External MCP client not seeing Figma:** Keep the plugin window open in Figma Desktop (that keeps ports `9223–9232` active) and restart Cursor / Claude Desktop once after running the installer.
- **Want to preview the UI in a browser without opening Figma?** Type `/demo` inside the plugin, or run `python3 -m http.server 8765` and visit `http://localhost:8765/ui.html?showcase=en` (or `?showcase=fa`).

---

## 💜 Creator & License

Built by **Hesam** — [GitHub (`@Hesvm`)](https://github.com/Hesvm) · [X / Twitter (`@hesvvm`)](https://x.com/hesvvm)

Licensed under the [MIT License](LICENSE) — free, open-source, and yours to hack on. If this saved your design workflow (or $30/mo), drop a ⭐ on the repo!
