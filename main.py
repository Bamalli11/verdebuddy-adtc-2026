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
        for chunk in content.split("---"):
            if chunk.strip():
                docs.append(chunk.strip())

CROP_WORDS = ['cassava','maize','tomato','rice','yam','groundnut','soybean','pepper',
              'onion','ginger','sesame','cocoa','cashew','plantain','cowpea','sorghum',
              'millet','wheat','banana','mango','pineapple','papaya','avocado','coconut',
              'orange','lemon','lime','guava','carrot','cabbage','cucumber','potato',
              'garlic','okra','watermelon','moringa','hibiscus']
STATE_WORDS = ['kano','benue','oyo','kaduna','plateau','niger','kebbi','ondo','cross river',
               'sokoto','kogi','nasarawa','taraba','adamawa','bauchi','gombe','borno','kwara',
               'enugu','anambra','imo','abia','ebonyi','rivers','delta','edo','lagos','ogun',
               'osun','ekiti','zamfara','katsina','jigawa','yobe','akwa ibom','bayelsa','fct']

def retrieve(query, n=2):
    q = query.lower()
    chunks = []

    # Step 1: Direct crop match - find the exact crop section
    matched_crop = None
    for cw in CROP_WORDS:
        if cw in q:
            matched_crop = cw
            break

    if matched_crop:
        for doc in docs:
            first_line = doc.strip().split('\n')[0].lower()
            if matched_crop in first_line:
                chunks.append(doc)
                break

    # Step 2: Direct state match - find state/weather/investment sections mentioning the state
    matched_state = None
    q_clean = q.replace('nigeria', '')
    for st in STATE_WORDS:
        if st in q_clean:
            matched_state = st
            break

    if matched_state and len(chunks) < n:
        for doc in docs:
            if doc in chunks:
                continue
            if matched_state in doc.lower() and ('Other states found' in doc or 'best planting states' in doc.lower()):
                chunks.append(doc)
                break

    # Step 2.5: Investment/ROI topic match - prioritize the sector opportunities chunk
    invest_triggers = ['invest', 'roi', 'return', 'profit', 'export', 'finance', 'loan', 'credit']
    if any(t in q for t in invest_triggers) and len(chunks) < n:
        priority_headers = ['top investment opportunities', 'nigeria agricultural overview']
        for ph in priority_headers:
            for doc in docs:
                if doc in chunks:
                    continue
                fl = doc.strip().split('\n')[0].lower()
                if ph in fl:
                    chunks.append(doc)
                    break
            if len(chunks) >= n:
                break
        # Fill any remaining with general investment chunks
        if len(chunks) < n:
            for doc in docs:
                if doc in chunks:
                    continue
                fl = doc.strip().split('\n')[0].lower()
                if 'invest' in fl or 'roi' in fl or 'export' in fl:
                    chunks.append(doc)
                    if len(chunks) >= n:
                        break

    # Step 3: Fill remaining slots with keyword-scored fallback
    if len(chunks) < n:
        q_words = [w for w in q.split() if len(w) > 4]
        scored = []
        for doc in docs:
            if doc in chunks:
                continue
            d = doc.lower()
            score = sum(1 for w in q_words if w in d)
            if len(d) > 800:
                score -= 3
            scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        for s, d in scored:
            if s <= 0:
                break
            chunks.append(d)
            if len(chunks) >= n:
                break

    return chunks[:n] if chunks else [docs[0]]
print("VerdeBuddy is ready!")

SYSTEM = "You are VerdeBuddy, an expert agricultural AI assistant for Nigerian farmers and investors. Answer ALL parts of every question completely and accurately. For multi-part questions, address each part clearly. Use bullet points for lists of 3 or more items. Keep total response under 200 words. After answering, ask if the user wants more details. Use only the provided context."
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
    ctx = " ".join(retrieve(query, n=3))[:800]
    examples = ""
    if "Hausa" in note:
        examples = "\nExample Q: Yaushe zan shuka masara?\nExample A: Shuka masara a farkon damina, watanni na Mayu zuwa Yuni. Tabbatar da ruwan sama ya isa kafin shuka."
    prompt = "<|im_start|>system\nYou are VerdeBuddy. Copy facts EXACTLY from Context below. Never invent variety names, numbers, or facts not in Context. If Context lacks an answer, say 'not specified in available data'." + note + "<|im_end|>\n<|im_start|>user\nContext:\n" + ctx + "\n\nQuestion: " + query + "<|im_end|>\n<|im_start|>assistant\n"
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
                import traceback
                traceback.print_exc()
                ans = "Sorry, I could not process that. Please try again."
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"answer": ans}).encode())

print("VerdeBuddy running at http://127.0.0.1:7860")
Threaded(("127.0.0.1", 7860), H).serve_forever()
