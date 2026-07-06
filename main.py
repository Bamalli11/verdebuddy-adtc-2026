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

STOPWORDS = {"the","a","an","in","of","for","is","are","what","which","give","to","do","does","my","i","on","and","or","with","this","that","how","when","where","who","can","will","should","about","from","as","it","be","get","good","should","would"}

import json as _json
with open("data/qa_pairs.json") as _f:
    QA_PAIRS = _json.load(_f)

SYNONYMS = {
    "roi": "roi", "return": "roi", "returns": "roi", "profitable": "roi",
    "profit": "roi", "profits": "roi", "investment": "roi", "investing": "roi",
}

def _normalize(text):
    words = []
    for w in text.lower().split():
        w = w.strip(".,?!:;")
        if not w:
            continue
        w = SYNONYMS.get(w, w)
        if len(w) > 3 and w.endswith("s"):
            w = w[:-1]
        if w in STOPWORDS:
            continue
        words.append(w)
    return set(words)

def find_qa_match(query):
    q_words = _normalize(query)
    if not q_words:
        return None
    best_score = 0.0
    best_answer = None
    for pair in QA_PAIRS:
        pair_words = _normalize(pair["q"])
        if not pair_words:
            continue
        overlap = len(q_words & pair_words)
        ratio = overlap / len(pair_words)
        if ratio > best_score and overlap >= 2:
            best_score = ratio
            best_answer = pair["a"]
    if best_score >= 0.5:
        return best_answer
    return None

def retrieve(query, n=2):
    q = query.lower()
    q_words = [w for w in q.split() if len(w) > 2]
    scored = []
    for doc in docs:
        d = doc.lower()
        score = sum(1 for w in q_words if w in d)
        # Boost score for state name matches
        if any(w in d for w in q_words if len(w) > 4):
            score += 2
        scored.append((score, doc))
    scored.sort(reverse=True)
    return [d for s,d in scored[:n] if s > 0] or [docs[0]]
print("VerdeBuddy is ready!")

SYSTEM = "You are VerdeBuddy, an agricultural intelligence assistant for Nigerian farmers and investors. When a question is simple, answer in 2-3 sentences. When a question is complex (investment, export, full crop guide, market analysis), first ask the user if they want a quick summary or full detailed analysis before answering. Be conversational and helpful. Use bullet points only for lists. Use only the provided context."
HAUSA = ["yaushe","zan","wane","nawa","yaya","menene","gona","masara","shuka","taki","kasuwa","girbi","rani","damina"]

def ask(query, lang='en'):
    qa_hit = find_qa_match(query)
    if qa_hit:
        return qa_hit
    q = query.lower()
    note = ''
    if any(w in q for w in HAUSA): note = ' Reply entirely in Hausa only.'

    more_triggers = ['tell me more', 'full detailed', 'more detail', 'elaborate', 'kara bayani', 'regarding this topic']
    is_more = any(t in q for t in more_triggers)

    if is_more:
        original = query.replace('Regarding this topic -', '').replace('- please give more detailed information', '').strip()
        ctx = " ".join(retrieve(original, n=2))[:300]
        instruction = "Give detailed bullet-point information about: " + original
    else:
        ctx = " ".join(retrieve(query, n=2))[:300]
        instruction = query

    examples = ""
    if note:
        examples = "\nMisal: Shuka masara a farkon damina, watanni na Mayu zuwa Yuni."

    prompt = "<|im_start|>system\n" + SYSTEM + note + examples + "<|im_end|>\n<|im_start|>user\nContext:\n" + ctx + "\n\n" + instruction + "<|im_end|>\n<|im_start|>assistant\n"
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
