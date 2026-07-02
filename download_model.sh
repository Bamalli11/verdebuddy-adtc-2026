#!/bin/bash

MODEL_PATH="model/qwen2.5-1.5b-instruct-q4_k_m.gguf"

mkdir -p model

if [ -f "$MODEL_PATH" ]; then
    echo "Model already exists, skipping download."
    exit 0
fi

echo "Downloading Qwen 2.5 model (~1GB)..."

wget -O "$MODEL_PATH" \
  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf

echo "Download complete."