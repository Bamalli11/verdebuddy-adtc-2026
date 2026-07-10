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

def _first_line(doc):
    return doc.strip().split('\n')[0].lower()

def _find_by_heading(keywords, exclude):
    for doc in docs:
        if doc in exclude:
            continue
        fl = _first_line(doc)
        if any(k in fl for k in keywords):
            return doc
    return None

def retrieve(query, n=3):
    q = query.lower().replace('nigeria', '')
    chunks = []

    # 1. Crop match - always highest priority if a crop is mentioned
    for cw in CROP_WORDS:
        if cw in q:
            match = _find_by_heading([cw], chunks)
            if match:
                chunks.append(match)
            break

    # 2. Soil topic match
    soil_triggers = ['soil', 'ph', 'acid', 'alkaline', 'lime', 'sandy', 'clay', 'loam', 'fertile', 'fertility']
    if any(t in q for t in soil_triggers) and len(chunks) < n:
        match = _find_by_heading(['soil ph', 'soil nutrient'], chunks) or \
                _find_by_heading(['sandy soil', 'clay soil', 'loamy soil', 'laterite', 'alluvial', 'hydromorphic'], chunks) or \
                _find_by_heading(['soil'], chunks)
        if match:
            chunks.append(match)

    # 3. Weather/climate topic match
    weather_triggers = ['rain', 'rainfall', 'weather', 'climate', 'drought', 'flood', 'season', 'harmattan', 'temperature']
    if any(t in q for t in weather_triggers) and len(chunks) < n:
        match = _find_by_heading(['monthly farming calendar'], chunks) or \
                _find_by_heading(['savanna zone', 'rainforest', 'sahel', 'montane'], chunks) or \
                _find_by_heading(['weather', 'drought', 'flooding', 'harmattan'], chunks)
        if match:
            chunks.append(match)

    # 4. Market/price topic match
    market_triggers = ['price', 'market', 'sell', 'cost', 'buy', 'cheap', 'expensive']
    if any(t in q for t in market_triggers) and len(chunks) < n:
        match = _find_by_heading(['commodity price tracker'], chunks) or \
                _find_by_heading(['market price seasonality'], chunks) or \
                _find_by_heading(['dawanau', 'mile 12', 'makurdi', 'major agricultural markets'], chunks)
        if match:
            chunks.append(match)

    # 5. Investment/export topic match
    invest_triggers = ['invest', 'roi', 'return', 'profit', 'export', 'finance', 'loan', 'credit']
    if any(t in q for t in invest_triggers) and len(chunks) < n:
        match = _find_by_heading(['top investment opportunities'], chunks) or \
                _find_by_heading(['nigeria agricultural overview'], chunks) or \
                _find_by_heading(['invest', 'roi', 'export'], chunks)
        if match:
            chunks.append(match)

    # 6. State match (crop/investment context) - only if not already covered
    for st in STATE_WORDS:
        if st in q and len(chunks) < n:
            match = _find_by_heading([st], chunks)
            if match:
                chunks.append(match)
            break

    # 7. Fallback keyword scoring for anything not caught above
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

from hausa_templates import HAUSA_TEMPLATES, classify_hausa_topic

MONTH_MAP = {
    "January": "Janairu", "February": "Fabrairu", "March": "Maris", "April": "Afrilu",
    "May": "Mayu", "June": "Yuni", "July": "Yuli", "August": "Agusta",
    "September": "Satumba", "October": "Oktoba", "November": "Nuwamba", "December": "Disamba"
}

def translate_to_hausa_text(text):
    """Translate month names and common season/unit phrases in an English fact string to Hausa."""
    for en, ha in MONTH_MAP.items():
        text = text.replace(en, ha)
    text = text.replace("first season", "kakar farko")
    text = text.replace("second season", "lokaci na biyu")
    text = text.replace("main season", "babbar kaka")
    text = text.replace("minor season", "kaka karama")
    text = text.replace("dry season", "lokacin rani")
    text = text.replace("rainy season", "damina")
    text = text.replace("harvest season", "lokacin girbi")
    text = text.replace("cold season", "lokacin hunturu")
    text = text.replace("months", "watanni")
    text = text.replace("month", "wata")
    text = text.replace("days", "kwanaki")
    text = text.replace("day", "rana")
    return text

HAUSA_CROP_MAP = {
    'masara': 'maize', 'rogo': 'cassava', 'tumatir': 'tomato', 'shinkafa': 'rice',
    'doya': 'yam', 'gyada': 'groundnut', 'wake': 'cowpea', 'barkono': 'pepper',
    'albasa': 'onion', 'citta': 'ginger', 'ridi': 'sesame', 'kaka': 'cocoa',
    'kwakwa': 'coconut', 'ayaba': 'banana', 'mangwaro': 'mango', 'dawa': 'sorghum',
    'gero': 'millet', 'waken soya': 'soybean'
}

def normalize_hausa_query(q):
    for ha_word, en_word in HAUSA_CROP_MAP.items():
        if ha_word in q:
            q = q + ' ' + en_word
    return q

def extract_crop_facts(query_lower):
    """Pull structured facts for the matched crop from the crops chunk, for template filling."""
    matched = None
    for cw in CROP_WORDS:
        if cw in query_lower:
            matched = cw
            break
    if not matched:
        return None
    chunk = _find_by_heading([matched], [])
    if not chunk:
        return None
    facts = {"crop": matched.capitalize(), "season": "watannin damina", "soil": "kasa mai kyau", "maturity": "kwanaki da yawa", "varieties": "iri daban-daban", "diseases": "cututtuka daban-daban"}
    for line in chunk.split("\n"):
        l = line.strip()
        if l.lower().startswith("planting season:"):
            facts["season"] = l.split(":",1)[1].strip()
        elif l.lower().startswith("soil type:"):
            facts["soil"] = l.split(":",1)[1].strip()
        elif l.lower().startswith("maturity period:"):
            facts["maturity"] = l.split(":",1)[1].strip()
        elif l.lower().startswith("recommended varieties:"):
            facts["varieties"] = l.split(":",1)[1].strip()
        elif l.lower().startswith("common diseases:"):
            facts["diseases"] = l.split(":",1)[1].strip()
    return facts

def ask(query, lang='en'):
    q = query.lower()

    if lang == 'ha' or any(w in q for w in HAUSA):
        q_clean = normalize_hausa_query(q.replace('nigeria', ''))
        has_crop = any(cw in q_clean for cw in CROP_WORDS)
        has_soil = any(t in q_clean for t in ['soil', 'ph', 'acid', 'kasa'])
        has_weather = any(t in q_clean for t in ['rain', 'weather', 'season', 'damina', 'fari'])
        has_market = any(t in q_clean for t in ['price', 'market', 'sell', 'farashi', 'kasuwa'])
        has_investment = any(t in q_clean for t in ['invest', 'roi', 'return', 'profit'])

        key = classify_hausa_topic(q_clean, has_crop, has_soil, has_weather, has_market, has_investment)
        template = HAUSA_TEMPLATES[key]

        fill = {
            "crop": "amfanin gona", "season": "watannin damina", "soil": "kasa mai kyau",
            "maturity": "kwanaki da yawa", "varieties": "iri daban-daban", "diseases": "cututtuka daban-daban",
            "market": "kusa da kai", "north_start": "Mayu zuwa Yuni", "south_start": "Maris zuwa Afrilu"
        }
        if has_crop:
            crop_facts = extract_crop_facts(q_clean)
            if crop_facts:
                for k in ("season", "maturity"):
                    if k in crop_facts:
                        crop_facts[k] = translate_to_hausa_text(crop_facts[k])
                fill.update(crop_facts)
                en_to_ha_crop = {v: k for k, v in HAUSA_CROP_MAP.items()}
                en_name = fill["crop"].lower()
                if en_name in en_to_ha_crop:
                    fill["crop"] = en_to_ha_crop[en_name].capitalize()

        try:
            return template.format(**fill)
        except Exception:
            return HAUSA_TEMPLATES["default"]

    ctx = "\n\n".join([c[:700] for c in retrieve(query, n=3)])
    prompt = "<|im_start|>system\nYou are VerdeBuddy, agricultural AI for Nigerian farmers and investors. Use facts from Context below. Never invent variety names, numbers, or facts not in Context. If part of the answer is missing from Context, answer what IS known and note what is not specified. Keep answer under 180 words.<|im_end|>\n<|im_start|>user\nContext:\n" + ctx + "\n\nQuestion: " + query + "<|im_end|>\n<|im_start|>assistant\n"
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
