#!/usr/bin/env bash
set -euo pipefail

BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$BRIDGE_DIR/.." && pwd)"
DAEMON_PY="$BRIDGE_DIR/bridge_daemon.py"
PLIST_PATH="$HOME/Library/LaunchAgents/com.antigravity.figma-copilot-bridge.plist"
PYTHON_BIN="$(command -v python3 || true)"

if [ -z "$PYTHON_BIN" ]; then
  echo "❌ python3 not found. Please install Python 3.9+ first."
  exit 1
fi

echo "🚀 Installing Figma AI Copilot Bridge + Figma Console MCP..."

# 1. Start / Register Local CLI Bridge Daemon (port 9444)
if command -v launchctl >/dev/null 2>&1 && [ "$(uname)" = "Darwin" ]; then
  mkdir -p "$HOME/Library/LaunchAgents"
  cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.antigravity.figma-copilot-bridge</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON_BIN</string>
    <string>$DAEMON_PY</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/figma_bridge.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/figma_bridge.log</string>
</dict>
</plist>
EOF
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
  launchctl load -w "$PLIST_PATH"
  echo "✅ LaunchAgent installed: http://localhost:9444 (auto-starts on login)"
else
  nohup "$PYTHON_BIN" "$DAEMON_PY" >/tmp/figma_bridge.log 2>&1 &
  echo "✅ Bridge started in background: http://localhost:9444"
fi

# 2. Auto-configure figma-console-mcp (southleft/figma-console-mcp) in installed AI clients
if command -v npx >/dev/null 2>&1; then
  "$PYTHON_BIN" - <<'PYEOF'
import json, os

configs = [
    ("Claude Desktop", os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")),
    ("Cursor", os.path.expanduser("~/.cursor/mcp.json")),
    ("Antigravity", os.path.expanduser("~/.gemini/antigravity/mcp_config.json")),
]

entry = {
    "command": "npx",
    "args": ["-y", "figma-console-mcp@latest"],
    "env": {"ENABLE_MCP_APPS": "true"}
}

for label, path in configs:
    parent = os.path.dirname(path)
    if not os.path.exists(parent) and not os.path.exists(path):
        continue
    try:
        data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        if not isinstance(data, dict):
            continue
        servers = data.setdefault("mcpServers", {})
        if "figma-console" not in servers:
            servers["figma-console"] = entry
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Auto-wired figma-console-mcp into {label} ({path})")
        else:
            print(f"✓ figma-console-mcp already configured in {label}")
    except Exception as e:
        print(f"⚠️ Could not update {label}: {e}")
PYEOF
else
  echo "ℹ️ npx not found — skipping optional figma-console-mcp auto-config (Node.js 18+ needed only for external MCP clients)."
fi

echo ""
echo "🎉 All set! Now in Figma Desktop:"
echo "   Plugins → Development → Import plugin from manifest... → $REPO_DIR/manifest.json"
