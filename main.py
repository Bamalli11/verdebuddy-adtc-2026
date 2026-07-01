from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
import chromadb, os, json
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

print("Loading VerdeBuddy...")
llm = Llama(model_path="model/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    n_ctx=2048, n_threads=4, n_gpu_layers=0, n_batch=512, verbose=False)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.create_collection("agri_knowledge")
for fn in os.listdir("data"):
    if fn.endswith(".txt"):
        with open(os.path.join("data", fn)) as f:
            content = f.read()
        for i, chunk in enumerate(content.split("\n\n")):
            if chunk.strip():
                collection.add(documents=[chunk],
                    embeddings=[embedder.encode(chunk).tolist()],
                    ids=[fn + "_" + str(i)])
print("VerdeBuddy is ready!")

SYSTEM = "You are VerdeBuddy, an offline AI for Nigerian farmers. Answer about crops, soil, weather, market prices. Max 3 sentences. Use only provided context."
HAUSA = ["yaushe","zan","wane","nawa","yaya","menene","gona","masara","shuka","taki","kasuwa","girbi","rani","damina"]
YORUBA = ["nigba","bawo","kini","elo","nibo","gbin","oja","ajile","irugbin","ikore","agbado","alubosa"]
IGBO = ["kedu","mgbe","ole","gini","ebe","aku","ugbo","ahia","nzu","ozuzo","onye"]

def ask(query):
    q = query.lower()
    note = ""
    if any(w in q for w in HAUSA): note = " Reply in Hausa."
    elif any(w in q for w in YORUBA): note = " Reply in Yoruba."
    elif any(w in q for w in IGBO): note = " Reply in Igbo."
    emb = embedder.encode(query).tolist()
    res = collection.query(query_embeddings=[emb], n_results=2)
    ctx = "\n\n".join(res["documents"][0])[:500]
    r = llm.create_chat_completion(messages=[
        {"role": "system", "content": SYSTEM + note},
        {"role": "user", "content": "Context:\n" + ctx + "\n\nQuestion: " + query}
    ], max_tokens=150, temperature=0.2)
    return r["choices"][0]["message"]["content"]


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
            ans = ask(body.get("question", ""))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"answer": ans}).encode())

print("VerdeBuddy running at http://127.0.0.1:7860")
Threaded(("127.0.0.1", 7860), H).serve_forever()
