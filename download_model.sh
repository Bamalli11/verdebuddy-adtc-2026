#!/bin/bash
mkdir -p model
if [ -f "model/qwen2.5-1.5b-instruct-q4_k_m.gguf" ]; then
    echo "Model already exists, skipping download."
    exit 0
fi
wget -O model/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf
