#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.request
import urllib.error
import subprocess
import os
import sys

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
            self.wfile.write(json.dumps({"status": "running", "port": PORT}).encode())
        elif self.path == '/latest':
            self.wfile.write(json.dumps({"prompt": LAST_PROMPT}).encode())
        else:
            self.wfile.write(json.dumps({"ok": True}).encode())

    def do_POST(self):
        global LAST_PROMPT
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode()) if post_data else {}

        if self.path == '/prompt':
            LAST_PROMPT = data
            prompt_text = data.get("prompt", "")
            selection_data = data.get("selection")
            image_data = data.get("image")

            print(f"\n[Figma Copilot Prompt Received]: {prompt_text}")
            if selection_data:
                print(f"Target Selection: {selection_data.get('name')} ({selection_data.get('type')})")

            # We can also call Gemini CLI / API directly from Python if needed!
            # Or return queued status
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received", "prompt": prompt_text}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), BridgeHandler) as httpd:
        print(f"Figma Copilot Bridge running on http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
