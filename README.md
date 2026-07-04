# VerdeBuddy 🌿
### Offline Agricultural AI for Nigerian Farmers
**ADTC 2026 Submission** | Built by Nana-Aisha Bamalli ([@Bamalli11](https://github.com/Bamalli11))

---

VerdeBuddy is a fully offline AI assistant that helps Nigerian smallholder farmers get practical advice on crops, soil health, weather patterns, and market prices — in English, Hausa, Yoruba, or Igbo — with no internet connection required.

![VerdeBuddy Screenshot](templates/screenshot.png)

---

## Features

- **Fully offline** — zero network requests during inference
- **4 languages** — English, Hausa, Yoruba, Igbo with explicit language toggle
- **Voice input** — speak your question via the microphone button
- **Chat history** — sidebar with search, New Chat, and Back/Forward navigation
- **Copy, Refresh, Edit** — action buttons on every message
- **Follow-up suggestions** — context-aware follow-up questions after each response
- **Export chat** — save conversations as a text file
- **PWA support** — installable on phone or desktop, works like a native app
- **8GB RAM compliant** — runs on CPU only, peak RAM ~1.78 GB

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Bamalli11/verdebuddy-adtc-2026.git
cd verdebuddy-adtc-2026

# 2. Download the model (~1GB)
bash download_model.sh

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start VerdeBuddy
python3 main.py

# 5. Open in browser
# http://localhost:7860
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language model | Qwen2.5-1.5B-Instruct Q4_K_M GGUF |
| Inference runtime | llama-cpp-python 0.2.56 |
| RAG pipeline | Keyword-based retrieval (pure Python) |
| Web server | Python built-in http.server |
| Frontend | HTML, CSS, Vanilla JS |
| PWA | Web App Manifest + Service Worker |

---

## Knowledge Base

The local knowledge base covers:
- **10 crops**: maize, cassava, tomato, rice, sorghum, cowpea, groundnut, yam, pepper, onion
- **6 agro-ecological zones** with monthly farming calendars
- **5 soil types** with pH management and amendment guides
- **Market prices** from Dawanau, Mile 12, Makurdi, and other major Nigerian markets

---

## Profiler Results

Measured with `adtc-profiler v0.1.0` on Intel Core i7-6500U, 5.8GB RAM, no GPU:

| Metric | Value |
|---|---|
| Tokens per second | 8.0 |
| Peak RAM | 1.78 GB |
| Performance score | 53.3/100 |
| Efficiency score | 74.6/100 |
| Combined score | 30.9/50 |

---

## Languages

| Language | Toggle | Auto-detection |
|---|---|---|
| English | EN | Default |
| Hausa | HA | Keyword-based |
| Yoruba | YO | Keyword-based |
| Igbo | IG | Keyword-based |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*Verde means Green. Built for the 36 million smallholder farmers across Nigeria.*
