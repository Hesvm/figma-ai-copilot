#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.request
import urllib.error
import subprocess
import os

PORT = 9224
LAST_PROMPT = None

class BridgeHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        global LAST_PROMPT
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path == '/status':
            self.wfile.write(json.dumps({"status": "running", "mcp": "ready"}).encode())
        elif self.path == '/latest':
            self.wfile.write(json.dumps({"prompt": LAST_PROMPT}).encode())
        else:
            self.wfile.write(json.dumps({"ok": True}).encode())

    def do_POST(self):
        global LAST_PROMPT
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode()) if post_data else {}

        if self.path == '/execute':
            # Execute JS on Figma directly via code runner or MCP
            code = data.get('code', '')
            pass

def run():
    with socketserver.TCPServer(("", PORT), BridgeHandler) as httpd:
        print(f"Server on {PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
