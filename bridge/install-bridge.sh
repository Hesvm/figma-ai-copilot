#!/usr/bin/env bash
set -euo pipefail

BRIDGE_DIR="$(cd "$(dirname "$0")" && pwd)"
DAEMON_PY="$BRIDGE_DIR/bridge_daemon.py"
PLIST_PATH="$HOME/Library/LaunchAgents/com.antigravity.figma-copilot-bridge.plist"
PYTHON_BIN="$(command -v python3)"

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

echo "Figma AI Copilot Bridge installed & started on http://localhost:9444"
