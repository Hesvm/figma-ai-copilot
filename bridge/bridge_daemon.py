#!/usr/bin/env python3
"""
Figma AI Copilot — Real Antigravity CLI Bridge Daemon
Port: 9444 (outside figma-console-mcp's 9223-9232 range to prevent any collision)
Connects the Figma plugin directly to the local `agy` CLI with ZERO API keys.
"""
import base64
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HTTP_PORT = 9444
AGY_BIN = os.path.expanduser("~/.local/bin/agy")
EXTRA_PATH = os.path.expanduser("~/.local/bin") + ":/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".bridge-tmp")
os.makedirs(TMP_DIR, exist_ok=True)

def find_cli(name):
    env_path = EXTRA_PATH + ":" + os.environ.get("PATH", "")
    return shutil.which(name, path=env_path)

def detect_providers():
    agy_path = find_cli("agy") or (AGY_BIN if os.path.exists(AGY_BIN) else None)
    claude_path = find_cli("claude")
    cursor_path = find_cli("cursor-agent") or find_cli("agent")
    codex_path = find_cli("codex")
    gemini_path = find_cli("gemini")
    ollama_path = find_cli("ollama")
    return [
        {"id": "antigravity", "name": "Antigravity CLI", "bin": "agy", "available": bool(agy_path), "path": agy_path},
        {"id": "claude", "name": "Claude Code CLI", "bin": "claude", "available": bool(claude_path), "path": claude_path},
        {"id": "cursor", "name": "Cursor Agent CLI", "bin": "cursor-agent", "available": bool(cursor_path), "path": cursor_path},
        {"id": "codex", "name": "OpenAI Codex CLI", "bin": "codex", "available": bool(codex_path), "path": codex_path},
        {"id": "gemini", "name": "Gemini CLI", "bin": "gemini", "available": bool(gemini_path), "path": gemini_path},
        {"id": "ollama", "name": "Ollama (Local)", "bin": "ollama", "available": bool(ollama_path), "path": ollama_path},
        {"id": "custom", "name": "Custom CLI", "bin": "custom", "available": True, "path": None},
    ]

CACHED_SKILLS = None

def _parse_skill_meta(file_path, fallback_id, source):
    name = fallback_id
    desc = ""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(1600)
        m = re.match(r"^---\s*\n([\s\S]*?)\n---", head)
        if m:
            fm = m.group(1)
            nm = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
            dm = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
            if nm:
                name = nm.group(1).strip().strip('"').strip("'")
            if dm:
                desc = dm.group(1).strip().strip('"').strip("'")
    except Exception:
        pass
    return {"id": fallback_id, "name": name, "description": desc[:140], "source": source, "path": file_path}

def list_installed_skills(force=False):
    global CACHED_SKILLS
    if CACHED_SKILLS is not None and not force:
        return CACHED_SKILLS
    skills = []
    seen = set()
    sources = [
        (os.path.expanduser("~/.gemini/config/skills/*/SKILL.md"), "agy", True),
        (os.path.expanduser("~/.gemini/config/plugins/*/skills/*/SKILL.md"), "plugin", True),
        (os.path.expanduser("~/.gemini/antigravity/builtin/skills/*/SKILL.md"), "builtin", True),
        (os.path.expanduser("~/.agents/skills/*/SKILL.md"), "agent", True),
        (os.path.expanduser("~/.claude/skills/*/SKILL.md"), "claude", True),
        (os.path.expanduser("~/.claude/commands/*.md"), "claude", False),
        (os.path.expanduser("~/.cursor/skills/*/SKILL.md"), "cursor", True),
    ]
    for pattern, src, is_dir in sources:
        for p in sorted(glob.glob(pattern)):
            sid = os.path.basename(os.path.dirname(p)) if is_dir else os.path.splitext(os.path.basename(p))[0]
            if sid in seen:
                continue
            seen.add(sid)
            skills.append(_parse_skill_meta(p, sid, src))
    skills.sort(key=lambda s: s["name"].lower())
    CACHED_SKILLS = skills
    return skills

JOBS = {}
JOB_PROCS = {}
JOB_COUNTER = 0
JOB_LOCK = threading.Lock()
CONVERSATION_ID = None
CACHED_MODELS = None

SYSTEM_INSTRUCTIONS = """You are Figma AI Copilot running inside the user's Figma Desktop plugin.
Your job is to directly modify or create Figma designs by outputting executable Figma Plugin API JavaScript.

IMPORTANT RULES:
1. Do NOT call any MCP tools or shell commands (except `read_file` ONLY if an attached reference image path is provided below).
2. If the user is asking to create, edit, style, or organize something in Figma:
   - Respond with a brief, clear explanation (1-2 sentences). Match the language of the user prompt (English by default, or Persian if the user prompt is in Persian).
   - Output exactly ONE ```javascript ... ``` code block containing the Figma Plugin API code to execute.
3. If the user's message is purely conversational (e.g., greeting, thanks, feedback, or a general question not requesting a canvas change):
   - Reply briefly and naturally without any ```javascript ``` code block. Do NOT output a dummy code block. Match user's language.
4. The JavaScript code runs inside `async function(figma, selection)` where:
   - `figma` is the global Figma Plugin API object.
   - `selection` is `figma.currentPage.selection` (array of currently selected SceneNodes).
   - `documentAccess` is `dynamic-page`: ALWAYS use `await figma.getNodeByIdAsync(id)` instead of `figma.getNodeById(id)`.
5. CRITICAL Figma Plugin API rules:
   - Colors are 0-1 floats: `{ r: 0.05, g: 0.6, b: 1 }`, NEVER 0-255, and NO `a` key inside `color` (put `opacity` on the paint object).
   - Fills/strokes are read-only arrays: clone/assign a new array (`node.fills = [{ type: 'SOLID', color: {...} }]`).
   - Before modifying ANY text node's `characters`, ALWAYS load its font first:
     ```js
     if (node.fontName === figma.mixed) {
       const fonts = node.getRangeAllFontNames(0, node.characters.length);
       for (const f of fonts) await figma.loadFontAsync(f);
     } else {
       await figma.loadFontAsync(node.fontName);
     }
     ```
   - For Auto Layout: set `layoutMode` BEFORE setting `layoutSizingHorizontal`/`layoutSizingVertical`. Only set `'FILL'` on children AFTER appending them to an auto-layout parent.
   - Always `await` every async call. Do NOT call `figma.closePlugin()` or `figma.notify()`.
   - End the script with `return "Short summary of the result";`
"""


def parse_agy_models():
    global CACHED_MODELS
    if CACHED_MODELS is not None:
        return CACHED_MODELS
    try:
        env = os.environ.copy()
        env["PATH"] = "/Users/hesam/.local/bin:/usr/local/bin:/usr/bin:/bin:" + env.get("PATH", "")
        p = subprocess.run([AGY_BIN, "models"], capture_output=True, text=True, timeout=15, env=env)
        models = []
        for line in p.stdout.splitlines():
            clean = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]|\r", "", line).strip()
            if not clean or "Fetching" in clean:
                continue
            m = re.match(r"^([a-zA-Z0-9._-]+)\s+(.+)$", clean)
            if m:
                models.append({"id": m.group(1), "label": m.group(2).strip()})
        if models:
            CACHED_MODELS = models
        return models
    except Exception:
        return []


def clean_reply_text(text):
    if not text:
        return ""
    s = text
    # Convert common HTML tags into clean plain/markdown formatting if an LLM emitted HTML wrappers
    s = re.sub(r"<\s*br\s*/?>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<\s*/\s*(?:p|div|li|ul|ol|h[1-6])\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<\s*li[^>]*>", "\n• ", s, flags=re.IGNORECASE)
    s = re.sub(r"<\s*(?:b|strong)[^>]*>(.*?)<\s*/\s*(?:b|strong)\s*>", r"**\1**", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<\s*code[^>]*>(.*?)<\s*/\s*code\s*>", r"`\1`", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def extract_code_and_message(raw_text):
    code_match = re.search(r"```(?:javascript|js)?\s*\n([\s\S]*?)```", raw_text)
    code = code_match.group(1).strip() if code_match else ""
    message = re.sub(r"```(?:javascript|js)?\s*\n[\s\S]*?```", "", raw_text)
    message = clean_reply_text(message)
    if not message:
        message = "Changes are ready and being applied to your Figma canvas." if code else ""
    return message, code


def run_provider_job(job_id, prompt_text, selection, image_b64, image_mime, model_id, provider="antigravity", custom_cmd="", skills=None, images=None):
    global CONVERSATION_ID
    start_ts = time.time()

    try:
        # Support up to 5 images (images array takes precedence; falls back to legacy single image_b64)
        img_items = []
        if isinstance(images, list) and len(images) > 0:
            for it in images[:5]:
                if isinstance(it, dict) and it.get("base64"):
                    img_items.append({
                        "base64": it.get("base64"),
                        "mime": it.get("mime") or "image/png",
                        "name": it.get("name") or "reference.png"
                    })
        elif image_b64:
            img_items.append({"base64": image_b64, "mime": image_mime or "image/png", "name": "reference.png"})

        saved_img_paths = []
        for idx, it in enumerate(img_items):
            ext = "png"
            mime = it["mime"]
            if "jpeg" in mime or "jpg" in mime:
                ext = "jpg"
            elif "webp" in mime:
                ext = "webp"
            elif "svg" in mime:
                ext = "svg"
            img_path = os.path.join(TMP_DIR, f"ref_{job_id}_{idx + 1}.{ext}")
            try:
                with open(img_path, "wb") as f:
                    f.write(base64.b64decode(it["base64"]))
                saved_img_paths.append((img_path, it["name"]))
            except Exception:
                pass

        img_note = ""
        if saved_img_paths:
            lines_list = "\n".join([f"- {p} ({nm})" for p, nm in saved_img_paths])
            img_note = f"\n\nATTACHED REFERENCE IMAGE PATHS (use read_file to inspect them):\n{lines_list}\n"

        skills_note = ""
        loaded_skill_names = []
        if skills and isinstance(skills, list):
            all_skills = {s["id"]: s for s in list_installed_skills()}
            for s_item in skills[:3]:
                sid = s_item.get("id") if isinstance(s_item, dict) else str(s_item)
                s_meta = all_skills.get(sid)
                s_path = s_meta["path"] if s_meta else (s_item.get("path") if isinstance(s_item, dict) else None)
                if s_path and os.path.exists(s_path):
                    try:
                        with open(s_path, "r", encoding="utf-8", errors="ignore") as sf:
                            s_content = sf.read(5000)
                        skills_note += f"\n--- ACTIVE SKILL (@{sid}) ---\n{s_content}\n"
                        loaded_skill_names.append(sid)
                    except Exception:
                        pass

        sel_json = json.dumps(selection, ensure_ascii=False) if selection else "null (nothing selected)"
        if len(sel_json) > 18000:
            sel_json = sel_json[:18000] + "... [truncated]"

        full_prompt = (
            f"{SYSTEM_INSTRUCTIONS}\n\n"
            f"{skills_note}"
            f"CURRENT FIGMA SELECTION JSON:\n{sel_json}\n"
            f"{img_note}\n"
            f"USER REQUEST:\n{prompt_text}"
        )

        env = os.environ.copy()
        env["PATH"] = EXTRA_PATH + ":" + env.get("PATH", "")

        cmd = None
        stdin_input = None

        sel_label = ""
        if isinstance(selection, dict) and selection.get("name"):
            sel_label = f"{selection.get('type', 'NODE')} · {selection.get('name')}"
        with JOB_LOCK:
            init_steps = [{"verb": "Analyzed", "icon": "analyze", "target": selection.get("name") if isinstance(selection, dict) and selection.get("name") else "Canvas context", "detail": sel_label}]
            for sname in loaded_skill_names:
                init_steps.append({"verb": "Loaded", "icon": "tool", "target": f"@{sname}"})
            for _, nm in saved_img_paths:
                init_steps.append({"verb": "Loaded", "icon": "image", "target": nm})
            init_steps.append({"verb": "Thinking", "target": model_id})
            JOBS[job_id]["steps"] = init_steps
            JOBS[job_id]["stream_text"] = ""

        if provider == "antigravity":
            bin_path = find_cli("agy") or AGY_BIN
            cmd = [
                bin_path,
                "-p", full_prompt,
                "--model", model_id,
                "--output-format", "stream-json",
                "--disable-slash-commands",
                "--dangerously-skip-permissions",
            ]
            if CONVERSATION_ID:
                cmd.extend(["--conversation", CONVERSATION_ID])
        elif provider == "claude":
            bin_path = find_cli("claude")
            if not bin_path:
                raise RuntimeError("Claude Code CLI ('claude') not found in PATH.")
            cmd = [bin_path, "-p", full_prompt, "--output-format", "json", "--dangerously-skip-permissions"]
        elif provider == "cursor":
            bin_path = find_cli("cursor-agent") or find_cli("agent")
            if not bin_path:
                raise RuntimeError("Cursor Agent CLI ('cursor-agent' or 'agent') not found in PATH.")
            cmd = [bin_path, "-p", full_prompt, "--output-format", "json"]
        elif provider == "codex":
            bin_path = find_cli("codex")
            if not bin_path:
                raise RuntimeError("OpenAI Codex CLI ('codex') not found in PATH.")
            cmd = [bin_path, "exec", full_prompt]
        elif provider == "gemini":
            bin_path = find_cli("gemini")
            if not bin_path:
                raise RuntimeError("Gemini CLI ('gemini') not found in PATH.")
            cmd = [bin_path, "-p", full_prompt]
        elif provider == "ollama":
            bin_path = find_cli("ollama")
            if not bin_path:
                raise RuntimeError("Ollama CLI ('ollama') not found in PATH.")
            cmd = [bin_path, "run", model_id or "llama3.2", full_prompt]
        elif provider == "custom":
            if not custom_cmd or not custom_cmd.strip():
                raise RuntimeError("Custom CLI command is empty. Please configure it in Settings -> Providers.")
            if "{prompt}" in custom_cmd:
                parts = shlex.split(custom_cmd)
                cmd = [p.replace("{prompt}", full_prompt) for p in parts]
            else:
                cmd = shlex.split(custom_cmd)
                stdin_input = full_prompt
        else:
            raise RuntimeError(f"Unsupported provider: {provider}")

        raw_response = ""
        stderr_text = ""
        returncode = 0

        if provider == "antigravity":
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
            )
            with JOB_LOCK:
                JOB_PROCS[job_id] = proc
            accumulated_lines = []
            partial_text = ""
            if proc.stdout:
                for line in proc.stdout:
                    line_s = line.strip()
                    if not line_s:
                        continue
                    accumulated_lines.append(line_s)
                    try:
                        evt = json.loads(line_s)
                        if not isinstance(evt, dict):
                            continue
                        etype = evt.get("event") or evt.get("type") or ""
                        step_upd = evt.get("step_update") if isinstance(evt.get("step_update"), dict) else {}
                        # Handle tool call events
                        tname = (
                            evt.get("tool_name")
                            or evt.get("name")
                            or step_upd.get("tool_name")
                            or ""
                        )
                        if etype in ("tool_call", "tool_use", "function_call") or tname:
                            tname = tname or "tool"
                            with JOB_LOCK:
                                JOBS[job_id]["steps"].append({
                                    "verb": "Ran",
                                    "icon": "tool",
                                    "target": tname,
                                    "detail": ""
                                })
                        # Handle streaming text delta events (agy uses step_update.text_delta)
                        delta_chunk = (
                            step_upd.get("text_delta")
                            or evt.get("delta")
                            or evt.get("text")
                            or (evt.get("content_block") or {}).get("text")
                            or ""
                        )
                        if isinstance(delta_chunk, str) and delta_chunk and etype != "result":
                            partial_text += delta_chunk
                            clean_partial = re.sub(r"```[\s\S]*$", "", partial_text)
                            clean_partial = clean_reply_text(clean_partial)
                            if clean_partial:
                                with JOB_LOCK:
                                    JOBS[job_id]["stream_text"] = clean_partial
                        # Handle final result event
                        if etype == "result" and isinstance(evt.get("result"), dict):
                            res_obj = evt["result"]
                            if res_obj.get("status") == "ERROR" and res_obj.get("error"):
                                raise RuntimeError(res_obj["error"])
                            raw_response = res_obj.get("response") or partial_text
                            if res_obj.get("conversation_id"):
                                CONVERSATION_ID = res_obj["conversation_id"]
                    except RuntimeError:
                        raise
                    except Exception:
                        pass
            proc.wait(timeout=180)
            returncode = proc.returncode
            stderr_text = proc.stderr.read().strip() if proc.stderr else ""
            if not raw_response:
                raw_response = partial_text or "\n".join(accumulated_lines)
        else:
            proc = subprocess.run(cmd, input=stdin_input, capture_output=True, text=True, timeout=180, env=env)
            returncode = proc.returncode
            stdout = proc.stdout.strip()
            stderr_text = proc.stderr.strip()
            raw_response = stdout
            try:
                json_start = stdout.find("{")
                if json_start != -1:
                    parsed = json.loads(stdout[json_start:])
                    if isinstance(parsed, dict):
                        raw_response = parsed.get("response") or parsed.get("result") or parsed.get("content") or stdout
            except Exception:
                pass

        elapsed = round(time.time() - start_ts, 1)

        if returncode != 0 and not raw_response:
            err_msg = stderr_text or f"{provider} exited with code {returncode}"
            with JOB_LOCK:
                JOBS[job_id].update({
                    "status": "error",
                    "error": err_msg,
                    "duration": elapsed
                })
            return

        message, code = extract_code_and_message(raw_response)

        with JOB_LOCK:
            if code:
                JOBS[job_id]["steps"].append({
                    "verb": "Generated",
                    "icon": "code",
                    "target": "Figma script",
                    "add": f"+{len(code.splitlines())}"
                })
            JOBS[job_id].update({
                "status": "done",
                "reply": message,
                "code": code,
                "model": model_id,
                "provider": provider,
                "duration": elapsed,
                "conversation_id": CONVERSATION_ID
            })

    except subprocess.TimeoutExpired:
        CONVERSATION_ID = None
        with JOB_LOCK:
            JOBS[job_id].update({
                "status": "error",
                "error": "Model processing timed out (180s).",
                "duration": round(time.time() - start_ts, 1)
            })
    except Exception as e:
        CONVERSATION_ID = None
        with JOB_LOCK:
            JOBS[job_id].update({
                "status": "error",
                "error": str(e),
                "duration": round(time.time() - start_ts, 1)
            })


class BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/status":
            self._send_json(200, {
                "status": "running",
                "port": HTTP_PORT,
                "agy_available": os.path.exists(AGY_BIN),
                "conversation_id": CONVERSATION_ID
            })
        elif self.path == "/providers":
            self._send_json(200, {"providers": detect_providers()})
        elif self.path == "/skills":
            self._send_json(200, {"skills": list_installed_skills()})
        elif self.path == "/models":
            self._send_json(200, {"models": parse_agy_models()})
        elif self.path.startswith("/job/"):
            job_id = self.path.split("/job/", 1)[1].strip()
            with JOB_LOCK:
                job = JOBS.get(job_id)
            if not job:
                self._send_json(404, {"error": "Job not found"})
            else:
                self._send_json(200, job)
        else:
            self._send_json(200, {"ok": True, "service": "figma-ai-copilot-bridge"})

    def do_POST(self):
        global JOB_COUNTER, CONVERSATION_ID
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if self.path == "/reset":
            CONVERSATION_ID = None
            self._send_json(200, {"status": "reset"})
            return

        if self.path.startswith("/cancel/"):
            job_id = self.path.split("/cancel/", 1)[1].strip()
            with JOB_LOCK:
                proc = JOB_PROCS.pop(job_id, None)
                job = JOBS.get(job_id)
                if job and job.get("status") == "running":
                    job["status"] = "cancelled"
                    job["duration"] = round(time.time() - job.get("started_at", time.time()), 1)
            if proc:
                try:
                    proc.terminate()
                except Exception:
                    pass
            self._send_json(200, {"status": "cancelled", "job_id": job_id})
            return

        if self.path == "/prompt":
            prompt_text = (data.get("prompt") or "").strip()
            selection = data.get("selection")
            image_b64 = data.get("image")
            image_mime = data.get("imageMime", "image/png")
            images_list = data.get("images") or []
            model_id = data.get("model") or "gemini-3.8-flash-low"
            provider = data.get("provider") or "antigravity"
            custom_cmd = data.get("customCommand") or ""
            skills = data.get("skills") or []

            with JOB_LOCK:
                JOB_COUNTER += 1
                job_id = str(JOB_COUNTER)
                JOBS[job_id] = {
                    "id": job_id,
                    "status": "running",
                    "model": model_id,
                    "provider": provider,
                    "started_at": time.time()
                }

            t = threading.Thread(
                target=run_provider_job,
                args=(job_id, prompt_text, selection, image_b64, image_mime, model_id, provider, custom_cmd, skills, images_list),
                daemon=True
            )
            t.start()

            self._send_json(200, {"status": "running", "job_id": job_id, "model": model_id, "provider": provider})
            return

        self._send_json(404, {"error": "Not found"})


def main():
    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer(("", HTTP_PORT), BridgeHandler)
    print(f"Figma AI Copilot Antigravity CLI Bridge listening on http://localhost:{HTTP_PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
