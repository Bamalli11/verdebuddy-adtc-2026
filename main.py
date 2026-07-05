import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
import json
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

import subprocess, threading
print("Loading VerdeBuddy...")
worker = subprocess.Popen(
    ["python3", "/home/servi/VerdeBuddy/worker.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
)
# Wait for worker ready
worker.stdout.readline()
worker_lock = threading.Lock()

def llm_ask(prompt):
    with worker_lock:
        worker.stdin.write(json.dumps({"prompt": prompt}) + "\n")
        worker.stdin.flush()
        line = worker.stdout.readline()
        return json.loads(line)["answer"]
# Simple keyword-based RAG
docs = []
for fn in os.listdir("data"):
    if fn.endswith(".txt"):
        with open(os.path.join("data", fn)) as f:
            content = f.read()
        for chunk in content.split("\n\n"):
            if chunk.strip():
                docs.append(chunk.strip())

def retrieve(query, n=2):
    q = query.lower()
    scored = []
    for doc in docs:
        score = sum(1 for w in q.split() if w in doc.lower())
        scored.append((score, doc))
    scored.sort(reverse=True)
    return [d for s,d in scored[:n] if s > 0] or [docs[0]]
print("VerdeBuddy is ready!")

SYSTEM = "You are VerdeBuddy, an offline AI assistant for Nigerian farmers and for local and foreign investors exploring agricultural opportunities in Nigeria. Answer questions about crops, soil health, weather patterns, market prices, and investment opportunities. Give clear practical advice in 2-3 sentences. Use only the provided context. Do not repeat yourself."
HAUSA = ["yaushe","zan","wane","nawa","yaya","menene","gona","masara","shuka","taki","kasuwa","girbi","rani","damina"]

def ask(query, lang='en'):
    q = query.lower()
    lang_map = {
        'ha': ' The farmer speaks Hausa. You MUST reply entirely in Hausa language only. Do not use English.',
        'en': ''
    }
    note = lang_map.get(lang, '')
    if not note:
        if any(w in q for w in HAUSA): note = lang_map['ha']
    ctx = " ".join(retrieve(query))[:300]
    examples = ""
    if "Hausa" in note:
        examples = "\nExample Q: Yaushe zan shuka masara?\nExample A: Shuka masara a farkon damina, watanni na Mayu zuwa Yuni. Tabbatar da ruwan sama ya isa kafin shuka."
    prompt = "<|im_start|>system\n" + SYSTEM + note + examples + "<|im_end|>\n<|im_start|>user\nContext: " + ctx + "\nQuestion: " + query + "<|im_end|>\n<|im_start|>assistant\n"
    return llm_ask(prompt)

PAGE = open('/home/servi/VerdeBuddy/templates/page.html').read()


class Threaded(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class H(BaseHTTPRequestHandler):
    def log_message(self, f, *a): pass
    def do_GET(self):
        import mimetypes
        p = self.path
        if p.startswith("/static/"):
            fpath = "/home/servi/VerdeBuddy" + p
            try:
                data = open(fpath,"rb").read()
                mt = mimetypes.guess_type(fpath)[0] or "text/plain"
                self.send_response(200)
                self.send_header("Content-type", mt)
                self.end_headers()
                self.wfile.write(data)
            except:
                self.send_response(404)
                self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(PAGE.encode("utf-8"))
    def do_POST(self):
        if self.path == "/ask":
            n = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(n))
            try:
                ans = ask(body.get("question", ""), body.get("lang", "en"))
            except Exception as e:
                ans = "Sorry, I could not process that. Please try again."
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"answer": ans}).encode())

print("VerdeBuddy running at http://127.0.0.1:7860")
Threaded(("127.0.0.1", 7860), H).serve_forever()
