# VerdeBuddy — ADTC 2026 Technical Report

## Problem

Nigerian smallholder farmers — over 36 million of them — make critical decisions
about planting, soil management, and selling without access to timely, reliable
advisory services. Extension officers are scarce, internet connectivity is
unreliable in rural areas, and existing agricultural apps require cloud access.

VerdeBuddy solves this by running a full agricultural AI advisor entirely offline
on a standard 8 GB laptop. Farmers can ask questions in English, Hausa, Yoruba,
or Igbo and receive practical advice on crops, soil health, weather patterns,
and market prices — with zero internet dependency during inference.

## Target User

Smallholder farmers across Nigeria's six geopolitical zones, particularly in
the Sudan Savanna and Guinea Savanna belts where maize, sorghum, cassava, yam,
groundnut, and cowpea are the primary crops.

## Design Decisions

**Model choice — Phi-3-mini-4k-instruct (Q4_K_M GGUF, 3.8B parameters)**
Microsoft's Phi-3-mini was chosen for its exceptional instruction-following
quality at small parameter counts. The Q4_K_M quantization reduces the model
to approximately 2.4 GB RAM while preserving strong reasoning quality.
Alternatives evaluated: Gemma-2-2B (less instruction-following), Qwen2.5-3B
(stronger multilingual but slower on CPU).

**Runtime — llama.cpp via llama-cpp-python**
llama.cpp provides the fastest CPU inference available for GGUF models.
n_threads=4, n_ctx=2048, n_batch=512 were tuned for the 8 GB RAM target
hardware profile.

**RAG pipeline — ChromaDB + sentence-transformers (all-MiniLM-L6-v2)**
A local retrieval-augmented generation pipeline grounds every model response
in a curated agricultural knowledge base covering 10 major Nigerian crops,
6 agro-ecological weather zones, 5 soil types, and commodity market pricing
across major Nigerian markets. The embedding model (80 MB) runs fully offline.

**Knowledge base**
Four domain files covering:
- Crop advisory (10 crops: maize, tomato, cassava, rice, sorghum, cowpea,
  groundnut, yam, pepper, onion) with state-specific planting calendars,
  disease guides, fertilizer recommendations, and yield data
- Weather patterns across Nigeria's 6 agro-ecological zones with monthly
  farming calendars
- Soil health covering 5 soil types, pH management, fertilizer guide,
  and conservation practices
- Market prices, seasonal trends, value addition, and post-harvest advice
  for all major commodities

**Multilingual support (African Alpha Bonus)**
VerdeBuddy supports English, Hausa, Yoruba, and Igbo through system prompt
language-detection instructions combined with Hausa, Yoruba, and Igbo
agricultural vocabulary embedded in the knowledge base. No additional
translation models are required.

**User interface**
Custom HTML/CSS/JavaScript chat interface served locally via Python's built-in
HTTPServer. Features a wet-leaf wallpaper, animated falling water droplets,
agricultural green theme, welcome screen with quick-start prompts, and a
centered chat layout. No external UI frameworks required.

## Constraints

- Hardware: 4 vCPU, 8 GB RAM, no GPU, no internet during inference
- Model must load and respond within available RAM after OS overhead (~2 GB)
- All knowledge base data pre-downloaded and stored as local text files
- No external API calls, no cloud services, no authentication required

## Benchmarks

Development machine: Standard laptop, 4-core CPU, 8 GB RAM

| Metric | Value |
|---|---|
| Model load time | ~45 seconds |
| Knowledge base load time | ~8 seconds |
| RAM usage (model + RAG + UI) | ~4.2 GB |
| Tokens per second | 8-12 tok/s |
| Average response time | 30-60 seconds |
| Response length | 100-150 tokens |
| Offline verified | ✅ Zero network calls during inference |

## Cross-Disciplinary Integration

VerdeBuddy integrates four distinct knowledge domains in every response:

1. **Crop science** — variety selection, planting schedules, pest and disease management
2. **Soil science** — pH management, nutrient recommendations, soil type identification
3. **Meteorology** — seasonal rainfall patterns, agro-ecological zone advisories
4. **Agricultural economics** — commodity pricing, market timing, value addition strategies

A single farmer query such as "I want to plant cassava in Oyo state next month"
triggers retrieval from all four domains simultaneously, producing a unified
advisory that no single-domain system could provide.

## African Language Support

Supported languages: English, Hausa (ha), Yoruba (yo), Igbo (ig)
Coverage: Crop terms, farming questions, and advisory responses in all four languages.
Implementation: System prompt language detection + multilingual knowledge base

cat > ~/verdebuddy-adtc-2026/REPORT.md << 'EOF'
# VerdeBuddy — ADTC 2026 Technical Report

## Problem

Nigerian smallholder farmers — over 36 million of them — make critical decisions
about planting, soil management, and selling without access to timely, reliable
advisory services. Extension officers are scarce, internet connectivity is
unreliable in rural areas, and existing agricultural apps require cloud access.

VerdeBuddy solves this by running a full agricultural AI advisor entirely offline
on a standard 8 GB laptop. Farmers can ask questions in English, Hausa, Yoruba,
or Igbo and receive practical advice on crops, soil health, weather patterns,
and market prices — with zero internet dependency during inference.

## Target User

Smallholder farmers across Nigeria's six geopolitical zones, particularly in
the Sudan Savanna and Guinea Savanna belts where maize, sorghum, cassava, yam,
groundnut, and cowpea are the primary crops.

## Design Decisions

**Model choice — Phi-3-mini-4k-instruct (Q4_K_M GGUF, 3.8B parameters)**
Microsoft's Phi-3-mini was chosen for its exceptional instruction-following
quality at small parameter counts. The Q4_K_M quantization reduces the model
to approximately 2.4 GB RAM while preserving strong reasoning quality.
Alternatives evaluated: Gemma-2-2B (less instruction-following), Qwen2.5-3B
(stronger multilingual but slower on CPU).

**Runtime — llama.cpp via llama-cpp-python**
llama.cpp provides the fastest CPU inference available for GGUF models.
n_threads=4, n_ctx=2048, n_batch=512 were tuned for the 8 GB RAM target
hardware profile.

**RAG pipeline — ChromaDB + sentence-transformers (all-MiniLM-L6-v2)**
A local retrieval-augmented generation pipeline grounds every model response
in a curated agricultural knowledge base covering 10 major Nigerian crops,
6 agro-ecological weather zones, 5 soil types, and commodity market pricing
across major Nigerian markets. The embedding model (80 MB) runs fully offline.

**Knowledge base**
Four domain files covering:
- Crop advisory (10 crops: maize, tomato, cassava, rice, sorghum, cowpea,
  groundnut, yam, pepper, onion) with state-specific planting calendars,
  disease guides, fertilizer recommendations, and yield data
- Weather patterns across Nigeria's 6 agro-ecological zones with monthly
  farming calendars
- Soil health covering 5 soil types, pH management, fertilizer guide,
  and conservation practices
- Market prices, seasonal trends, value addition, and post-harvest advice
  for all major commodities

**Multilingual support (African Alpha Bonus)**
VerdeBuddy supports English, Hausa, Yoruba, and Igbo through system prompt
language-detection instructions combined with Hausa, Yoruba, and Igbo
agricultural vocabulary embedded in the knowledge base. No additional
translation models are required.

**User interface**
Custom HTML/CSS/JavaScript chat interface served locally via Python's built-in
HTTPServer. Features a wet-leaf wallpaper, animated falling water droplets,
agricultural green theme, welcome screen with quick-start prompts, and a
centered chat layout. No external UI frameworks required.

## Constraints

- Hardware: 4 vCPU, 8 GB RAM, no GPU, no internet during inference
- Model must load and respond within available RAM after OS overhead (~2 GB)
- All knowledge base data pre-downloaded and stored as local text files
- No external API calls, no cloud services, no authentication required

## Benchmarks

Development machine: Standard laptop, 4-core CPU, 8 GB RAM

| Metric | Value |
|---|---|
| Model load time | ~45 seconds |
| Knowledge base load time | ~8 seconds |
| RAM usage (model + RAG + UI) | ~4.2 GB |
| Tokens per second | 8-12 tok/s |
| Average response time | 30-60 seconds |
| Response length | 100-150 tokens |
| Offline verified | ✅ Zero network calls during inference |

## Cross-Disciplinary Integration

VerdeBuddy integrates four distinct knowledge domains in every response:

1. **Crop science** — variety selection, planting schedules, pest and disease management
2. **Soil science** — pH management, nutrient recommendations, soil type identification
3. **Meteorology** — seasonal rainfall patterns, agro-ecological zone advisories
4. **Agricultural economics** — commodity pricing, market timing, value addition strategies

A single farmer query such as "I want to plant cassava in Oyo state next month"
triggers retrieval from all four domains simultaneously, producing a unified
advisory that no single-domain system could provide.

## African Language Support

Supported languages: English, Hausa (ha), Yoruba (yo), Igbo (ig)
Coverage: Crop terms, farming questions, and advisory responses in all four languages.
Implementation: System prompt language detection + multilingual knowledge base




cat > ~/verdebuddy-adtc-2026/REPORT.md << 'EOF'
# VerdeBuddy — ADTC 2026 Technical Report

## Problem

Nigerian smallholder farmers — over 36 million of them — make critical decisions
about planting, soil management, and selling without access to timely, reliable
advisory services. Extension officers are scarce, internet connectivity is
unreliable in rural areas, and existing agricultural apps require cloud access.

VerdeBuddy solves this by running a full agricultural AI advisor entirely offline
on a standard 8 GB laptop. Farmers can ask questions in English, Hausa, Yoruba,
or Igbo and receive practical advice on crops, soil health, weather patterns,
and market prices — with zero internet dependency during inference.

## Target User

Smallholder farmers across Nigeria's six geopolitical zones, particularly in
the Sudan Savanna and Guinea Savanna belts where maize, sorghum, cassava, yam,
groundnut, and cowpea are the primary crops.

## Design Decisions

**Model choice — Phi-3-mini-4k-instruct (Q4_K_M GGUF, 3.8B parameters)**
Microsoft's Phi-3-mini was chosen for its exceptional instruction-following
quality at small parameter counts. The Q4_K_M quantization reduces the model
to approximately 2.4 GB RAM while preserving strong reasoning quality.
Alternatives evaluated: Gemma-2-2B (less instruction-following), Qwen2.5-3B
(stronger multilingual but slower on CPU).

**Runtime — llama.cpp via llama-cpp-python**
llama.cpp provides the fastest CPU inference available for GGUF models.
n_threads=4, n_ctx=2048, n_batch=512 were tuned for the 8 GB RAM target
hardware profile.

**RAG pipeline — ChromaDB + sentence-transformers (all-MiniLM-L6-v2)**
A local retrieval-augmented generation pipeline grounds every model response
in a curated agricultural knowledge base covering 10 major Nigerian crops,
6 agro-ecological weather zones, 5 soil types, and commodity market pricing
across major Nigerian markets. The embedding model (80 MB) runs fully offline.

**Knowledge base**
Four domain files covering:
- Crop advisory (10 crops: maize, tomato, cassava, rice, sorghum, cowpea,
  groundnut, yam, pepper, onion) with state-specific planting calendars,
  disease guides, fertilizer recommendations, and yield data
- Weather patterns across Nigeria's 6 agro-ecological zones with monthly
  farming calendars
- Soil health covering 5 soil types, pH management, fertilizer guide,
  and conservation practices
- Market prices, seasonal trends, value addition, and post-harvest advice
  for all major commodities

**Multilingual support (African Alpha Bonus)**
VerdeBuddy supports English, Hausa, Yoruba, and Igbo through system prompt
language-detection instructions combined with Hausa, Yoruba, and Igbo
agricultural vocabulary embedded in the knowledge base. No additional
translation models are required.

**User interface**
Custom HTML/CSS/JavaScript chat interface served locally via Python's built-in
HTTPServer. Features a wet-leaf wallpaper, animated falling water droplets,
agricultural green theme, welcome screen with quick-start prompts, and a
centered chat layout. No external UI frameworks required.

## Constraints

- Hardware: 4 vCPU, 8 GB RAM, no GPU, no internet during inference
- Model must load and respond within available RAM after OS overhead (~2 GB)
- All knowledge base data pre-downloaded and stored as local text files
- No external API calls, no cloud services, no authentication required

## Benchmarks

Development machine: Standard laptop, 4-core CPU, 8 GB RAM

| Metric | Value |
|---|---|
| Model load time | ~45 seconds |
| Knowledge base load time | ~8 seconds |
| RAM usage (model + RAG + UI) | ~4.2 GB |
| Tokens per second | 8-12 tok/s |
| Average response time | 30-60 seconds |
| Response length | 100-150 tokens |
| Offline verified | ✅ Zero network calls during inference |

## Cross-Disciplinary Integration

VerdeBuddy integrates four distinct knowledge domains in every response:

1. **Crop science** — variety selection, planting schedules, pest and disease management
2. **Soil science** — pH management, nutrient recommendations, soil type identification
3. **Meteorology** — seasonal rainfall patterns, agro-ecological zone advisories
4. **Agricultural economics** — commodity pricing, market timing, value addition strategies

A single farmer query such as "I want to plant cassava in Oyo state next month"
triggers retrieval from all four domains simultaneously, producing a unified
advisory that no single-domain system could provide.

## African Language Support

Supported languages: English, Hausa (ha), Yoruba (yo), Igbo (ig)
Coverage: Crop terms, farming questions, and advisory responses in all four languages.
Implementation: System prompt language detection + multilingual knowledge base

cat > ~/verdebuddy-adtc-2026/REPORT.md << 'EOF'
# VerdeBuddy — ADTC 2026 Technical Report

## Problem

Nigerian smallholder farmers — over 36 million of them — make critical decisions
about planting, soil management, and selling without access to timely, reliable
advisory services. Extension officers are scarce, internet connectivity is
unreliable in rural areas, and existing agricultural apps require cloud access.

VerdeBuddy solves this by running a full agricultural AI advisor entirely offline
on a standard 8 GB laptop. Farmers can ask questions in English, Hausa, Yoruba,
or Igbo and receive practical advice on crops, soil health, weather patterns,
and market prices — with zero internet dependency during inference.

## Target User

Smallholder farmers across Nigeria's six geopolitical zones, particularly in
the Sudan Savanna and Guinea Savanna belts where maize, sorghum, cassava, yam,
groundnut, and cowpea are the primary crops.

## Design Decisions

**Model choice — Phi-3-mini-4k-instruct (Q4_K_M GGUF, 3.8B parameters)**
Microsoft's Phi-3-mini was chosen for its exceptional instruction-following
quality at small parameter counts. The Q4_K_M quantization reduces the model
to approximately 2.4 GB RAM while preserving strong reasoning quality.
Alternatives evaluated: Gemma-2-2B (less instruction-following), Qwen2.5-3B
(stronger multilingual but slower on CPU).

**Runtime — llama.cpp via llama-cpp-python**
llama.cpp provides the fastest CPU inference available for GGUF models.
n_threads=4, n_ctx=2048, n_batch=512 were tuned for the 8 GB RAM target
hardware profile.

**RAG pipeline — ChromaDB + sentence-transformers (all-MiniLM-L6-v2)**
A local retrieval-augmented generation pipeline grounds every model response
in a curated agricultural knowledge base covering 10 major Nigerian crops,
6 agro-ecological weather zones, 5 soil types, and commodity market pricing
across major Nigerian markets. The embedding model (80 MB) runs fully offline.

**Knowledge base**
Four domain files covering:
- Crop advisory (10 crops: maize, tomato, cassava, rice, sorghum, cowpea,
  groundnut, yam, pepper, onion) with state-specific planting calendars,
  disease guides, fertilizer recommendations, and yield data
- Weather patterns across Nigeria's 6 agro-ecological zones with monthly
  farming calendars
- Soil health covering 5 soil types, pH management, fertilizer guide,
  and conservation practices
- Market prices, seasonal trends, value addition, and post-harvest advice
  for all major commodities

**Multilingual support (African Alpha Bonus)**
VerdeBuddy supports English, Hausa, Yoruba, and Igbo through system prompt
language-detection instructions combined with Hausa, Yoruba, and Igbo
agricultural vocabulary embedded in the knowledge base. No additional
translation models are required.

**User interface**
Custom HTML/CSS/JavaScript chat interface served locally via Python's built-in
HTTPServer. Features a wet-leaf wallpaper, animated falling water droplets,
agricultural green theme, welcome screen with quick-start prompts, and a
centered chat layout. No external UI frameworks required.

## Constraints

- Hardware: 4 vCPU, 8 GB RAM, no GPU, no internet during inference
- Model must load and respond within available RAM after OS overhead (~2 GB)
- All knowledge base data pre-downloaded and stored as local text files
- No external API calls, no cloud services, no authentication required

## Benchmarks

Development machine: Standard laptop, 4-core CPU, 8 GB RAM

| Metric | Value |
|---|---|
| Model load time | ~45 seconds |
| Knowledge base load time | ~8 seconds |
| RAM usage (model + RAG + UI) | ~4.2 GB |
| Tokens per second | 8-12 tok/s |
| Average response time | 30-60 seconds |
| Response length | 100-150 tokens |
| Offline verified | ✅ Zero network calls during inference |

## Cross-Disciplinary Integration

VerdeBuddy integrates four distinct knowledge domains in every response:

1. **Crop science** — variety selection, planting schedules, pest and disease management
2. **Soil science** — pH management, nutrient recommendations, soil type identification
3. **Meteorology** — seasonal rainfall patterns, agro-ecological zone advisories
4. **Agricultural economics** — commodity pricing, market timing, value addition strategies

A single farmer query such as "I want to plant cassava in Oyo state next month"
triggers retrieval from all four domains simultaneously, producing a unified
advisory that no single-domain system could provide.

## African Language Support

Supported languages: English, Hausa (ha), Yoruba (yo), Igbo (ig)
Coverage: Crop terms, farming questions, and advisory responses in all four languages.
Implementation: System prompt language detection + multilingual knowledge base




[200~EOF~
