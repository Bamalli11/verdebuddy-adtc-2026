#!/bin/bash
set -e

MODEL_DIR="model"
MODEL_FILE="Phi-3-mini-4k-instruct-q4.gguf"
MODEL_URL="https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"

mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_DIR/$MODEL_FILE" ]; then
  echo "Model already downloaded."
  exit 0
fi

echo "Downloading Phi-3-mini (~2.4 GB)..."
curl -L --progress-bar -o "$MODEL_DIR/$MODEL_FILE" "$MODEL_URL"

echo "Done. Model saved to $MODEL_DIR/$MODEL_FILE"