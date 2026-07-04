# VerdeBuddy: ADTC 2026 Technical Report

## 1. Problem

Nigeria has over 36 million smallholder farmers who make daily decisions about planting, soil management, pest control, and market timing without access to reliable advisory services. Agricultural extension officers are scarce, with the national ratio sitting at approximately one officer per 3,000 farmers. In much of the Sudan Savanna and Guinea Savanna belts, where the majority of food production takes place, internet connectivity is intermittent at best and entirely absent at worst.

Existing agricultural apps assume a stable cloud connection and are rarely available in local languages. When connectivity fails, so does the tool. VerdeBuddy was built to eliminate that dependency entirely. It runs a complete agricultural AI advisor offline on a standard laptop, requiring no internet connection during inference. Farmers can ask questions in English, Hausa, Yoruba, or Igbo and receive practical, grounded advice on crops, soil health, weather patterns, and market prices at any time, from any location.

The primary target users are smallholder farmers across Nigeria's six geopolitical zones, with particular focus on growers of maize, cassava, sorghum, yam, groundnut, cowpea, tomato, rice, pepper, and onion in northern and central Nigeria.


## 2. Design Decisions

### Model: Qwen2.5-1.5B-Instruct (Q4_K_M GGUF, approximately 1 GB)

Qwen2.5-1.5B-Instruct was selected after evaluating several small open-source models against four criteria: instruction-following quality, multilingual capability, RAM footprint, and CPU inference speed.

| Model | Parameters | RAM at Q4_K_M | Instruction Quality | Selected |
|---|---|---|---|---|
| Qwen2.5-1.5B-Instruct | 1.5B | ~1.0 GB | Strong | Yes |
| Gemma-2-2B | 2B | ~1.5 GB | Moderate | No |
| Phi-3-mini-4k | 3.8B | ~2.4 GB | Strong | No (too slow on CPU) |
| Qwen2.5-3B | 3B | ~2.0 GB | Strong | No (RAM concern) |

Qwen2.5-1.5B offered the best overall balance. It delivers strong instruction-following at roughly 1 GB RAM, leaving comfortable headroom for the operating system and application overhead within the 8 GB hardware target.

The Q4_K_M quantization level was chosen because it preserves most of the model's reasoning quality while reducing RAM usage by approximately 75% compared to full float32. Q2_K produced noticeably degraded agricultural reasoning in early tests, and Q5_K_M exceeded the RAM budget on the target hardware profile.

### Runtime: llama.cpp via llama-cpp-python

llama.cpp provides the fastest available CPU inference for GGUF models, using hand-optimized SIMD kernels. No GPU is required or assumed. Key inference parameters tuned for the 8 GB hardware target: n_ctx=512, n_batch=128, n_threads=4, n_gpu_layers=0, max_tokens=150, repeat_penalty=1.3.

### Subprocess Worker Architecture

The inference engine runs as a separate subprocess rather than inline with the HTTP server. This means a C-level crash or segfault in llama.cpp does not bring down the web server. The main process communicates with the worker over stdin/stdout using newline-delimited JSON, with a threading lock ensuring requests are serialized safely.

### RAG Pipeline: Keyword-Based Retrieval

Every model response is grounded in a curated local knowledge base through retrieval-augmented generation. At query time, the most relevant passages are retrieved by keyword scoring and injected into the prompt context, substantially reducing hallucination on domain-specific agricultural questions.

The knowledge base consists of four domain files totalling approximately 1,200 lines of curated agricultural content, covering ten major Nigerian crops with state-specific planting calendars, disease guides, fertilizer schedules, and yield targets; weather patterns across Nigeria's six agro-ecological zones; five soil types with pH management and amendment guidance; and commodity market pricing, seasonal trends, and post-harvest advice across major Nigerian markets including Dawanau, Mile 12, and Makurdi.

A keyword-based retrieval approach was chosen over sentence-transformers after discovering that the embedding model caused indefinite startup hangs in offline environments due to background network checks. Pure Python keyword scoring is instant, reliable, and requires no additional dependencies.

### Multilingual Support

Language detection operates on two levels. First, the user can explicitly select their language via a toggle (EN, HA, YO, IG) in the interface. Second, keyword matching provides automatic fallback detection. When a language is selected or detected, the system prompt instructs the model to respond entirely in that language, accompanied by a few-shot example in the target language to guide output quality. This approach requires no translation API and works entirely offline.

### User Interface

VerdeBuddy serves a single-page chat application through Python's built-in http.server module. The interface includes a chat history sidebar with search and navigation; copy, refresh, and edit buttons on every message; suggested follow-up questions after each response; a language toggle for English, Hausa, Yoruba, and Igbo; voice input via the Web Speech API; an export chat function; suggested prompt chips in all four languages; and a clean agriculture-themed design. All assets are local with zero external resource dependencies.

### Progressive Web App

VerdeBuddy ships with a Web App Manifest and service worker, allowing it to be installed directly from the browser on any device. Once installed it launches in fullscreen like a native app, and the service worker caches all static assets for instant loading.


## 3. Constraints

The 8 GB RAM ceiling was the primary hardware constraint shaping every decision. The 1.5B model at Q4_K_M occupies approximately 1 GB, leaving well over 6 GB of headroom for the operating system and application overhead.

The requirement for zero internet access during inference meant that all assets, model weights, the knowledge base, and UI resources had to be local. No GPU could be assumed, so inference runs entirely on CPU through llama.cpp. African language support was achieved through explicit language selection combined with keyword-based detection and few-shot prompt engineering rather than a separate translation model. The server runs on Python's standard library HTTP server, avoiding any dependency on Flask, FastAPI, or other web frameworks.


## 4. Benchmarks

Measured on development machine: Intel Core i7-6500U, 4 CPU cores, 5.8 GB usable RAM, WSL2 Ubuntu, no GPU.

| Metric | Observed Value |
|---|---|
| Model load time (cold start) | 18 to 25 seconds |
| RAG retrieval latency | less than 0.1 seconds |
| Inference speed | 7.65 tokens per second |
| First token latency | approximately 44 seconds |
| Peak RAM usage | 1.78 GB |
| Steady state RAM | 1.71 GB |
| Context window | 512 tokens |
| Maximum response length | 150 tokens |

### Profiler Results (adtc-profiler v0.1.0, participant mode)

| Metric | Value | Score |
|---|---|---|
| Tokens per second | 8.0 | 53.3/100 |
| Peak RAM | 1.78 GB | 74.6/100 |
| Combined (perf + efficiency) | | 30.9/50 |


## 5. Offline Compliance

VerdeBuddy makes zero network requests during normal operation. Model weights are stored locally and downloaded once via the provided idempotent script. The knowledge base is a set of plain text files. All UI assets are either inlined or served from the local /static/ directory. There is no CDN usage, no analytics, and no telemetry. The system has been tested with the network interface fully disabled and behaves identically to connected mode.


*VerdeBuddy. Verde means Green. Built for Nigerian farmers, runs anywhere.*
