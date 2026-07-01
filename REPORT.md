# VerdeBuddy: ADTC 2026 Technical Report

## 1. Problem

Nigeria has over 36 million smallholder farmers who make daily decisions about planting, soil management, pest control, and market timing without reliable access to advisory services. Agricultural extension officers are scarce, with the national ratio sitting at approximately one officer per 3,000 farmers. In much of the Sudan Savanna and Guinea Savanna belts, where the majority of food production takes place, internet connectivity is intermittent at best and entirely absent at worst.

Existing agricultural apps assume a stable cloud connection and are rarely available in local languages. When connectivity fails, so does the tool. VerdeBuddy was built to eliminate that dependency entirely. It runs a complete agricultural AI advisor offline on a standard laptop, requiring no internet connection during inference. Farmers can ask questions in English, Hausa, Yoruba, or Igbo and receive practical, grounded advice on crops, soil health, weather patterns, and market prices at any time, from any location.

The primary target users are smallholder farmers across Nigeria's six geopolitical zones, with particular focus on growers of maize, cassava, sorghum, yam, groundnut, cowpea, tomato, rice, pepper, and onion in northern and central Nigeria.


## 2. Design Decisions

### Model Selection: Qwen2.5-1.5B-Instruct (Q4_K_M GGUF, approximately 1 GB)

Qwen2.5-1.5B-Instruct was selected after evaluating several small open-source models against four criteria: instruction-following quality, multilingual capability, RAM footprint, and CPU inference speed.

| Model | Parameters | RAM at Q4_K_M | Instruction Quality | Selected |
|---|---|---|---|---|
| Qwen2.5-1.5B-Instruct | 1.5B | ~1.0 GB | Strong | Yes |
| Gemma-2-2B | 2B | ~1.5 GB | Moderate | No |
| Phi-3-mini-4k | 3.8B | ~2.4 GB | Strong | No (too slow on CPU) |
| Qwen2.5-3B | 3B | ~2.0 GB | Strong | No (RAM concern) |

Qwen2.5-1.5B offered the best overall balance. It delivers strong instruction-following at roughly 1 GB RAM, leaving comfortable headroom for the operating system, RAG pipeline, and embedding model within the 8 GB hardware target. Its multilingual pretraining also gives it reasonable handling of Hausa, Yoruba, and Igbo vocabulary without any fine-tuning.

The Q4_K_M quantization level was chosen because it preserves most of the model's reasoning quality while reducing RAM usage by approximately 75% compared to full float32. Q2_K produced noticeably degraded agricultural reasoning in early tests, and Q5_K_M exceeded the RAM budget on the target hardware profile.

### Runtime: llama.cpp via llama-cpp-python

llama.cpp provides the fastest available CPU inference for GGUF models, using hand-optimized SIMD kernels. No GPU is required or assumed. The key inference parameters were tuned specifically for the 8 GB hardware target: n_ctx=512, n_batch=256, n_threads=4, n_gpu_layers=0, and max_tokens=80.

### RAG Pipeline: ChromaDB and sentence-transformers

Every model response is grounded in a curated local knowledge base through retrieval-augmented generation. At query time, the three most relevant passages are retrieved and injected into the prompt context, substantially reducing hallucination on domain-specific agricultural questions.

The embedding model is all-MiniLM-L6-v2, which weighs approximately 80 MB and runs entirely offline. The vector store is ChromaDB, configured for local persistent storage with no external server required. The knowledge base consists of four domain files totalling approximately 1,200 lines of curated agricultural content, covering ten major Nigerian crops with state-specific planting calendars, disease guides, fertilizer schedules, and yield targets; weather patterns across Nigeria's six agro-ecological zones; five soil types with pH management and amendment guidance; and commodity market pricing, seasonal trends, and post-harvest advice across major Nigerian markets.

### Multilingual Support

Language detection uses keyword matching across four languages. When a Hausa, Yoruba, or Igbo query is detected, the system prompt instructs the model to respond in that language. This approach requires no additional models or translation APIs and works entirely offline.

### User Interface

VerdeBuddy serves a single-page chat interface through Python's built-in http.server module. The interface includes a chat history sidebar with search, New Chat, and Back/Forward navigation; suggested prompt chips in all four supported languages on the landing screen; properly word-wrapped responses; and a background image served from base64 so there are no external asset requests. The entire UI operates offline with zero CDN or third-party resource dependencies.


## 3. Constraints

The 8 GB RAM ceiling was the primary hardware constraint shaping every decision. The 1.5B model at Q4_K_M occupies approximately 1 GB, and the MiniLM embedding model adds another 80 MB, leaving well over 6 GB of headroom for the operating system and application overhead.

The requirement for zero internet access during inference meant that all assets, model weights, the vector database, and UI resources had to be local. No GPU could be assumed, so inference runs entirely on CPU through llama.cpp. African language support was achieved through keyword-based detection paired with a multilingual system prompt rather than a separate translation model. The server runs on Python's standard library HTTP server, avoiding any dependency on Flask, FastAPI, or other web frameworks. Model weights are downloaded once via an idempotent download_model.sh script that checks for the file before downloading.


## 4. Benchmarks

The following measurements were taken on the development machine: an Intel Core i5 with 4 CPU cores, 5.8 GB usable RAM, running WSL2 Ubuntu 24 with no GPU.

| Metric | Observed Value |
|---|---|
| Model load time (cold start) | 18 to 25 seconds |
| RAG retrieval latency | 0.3 to 0.8 seconds |
| Inference speed | 4 to 7 tokens per second |
| Time to first response | 15 to 25 seconds |
| Peak RAM usage (model and RAG) | approximately 1.4 GB |
| Idle RAM after load | approximately 1.1 GB |
| Context window | 512 tokens |
| Maximum response length | 80 tokens |

Response time is primarily constrained by CPU inference speed. On more capable hardware such as a modern 8-core CPU, inference speed would improve to roughly 12 to 18 tokens per second, bringing time-to-response down to between 5 and 10 seconds.


## 5. Offline Compliance

VerdeBuddy makes zero network requests during normal operation. Model weights are stored at model/qwen2.5-1.5b-instruct-q4_k_m.gguf and downloaded once via the provided script. The sentence-transformers embedding model is cached locally. ChromaDB persists its vector index to a local directory. All UI assets are either inlined or served from the local /static/ directory. There is no CDN usage, no analytics, and no telemetry of any kind. The system has been tested with the network interface fully disabled and behaves identically to connected mode.


*VerdeBuddy. Verde means Green. Built for Nigerian farmers, runs anywhere.*