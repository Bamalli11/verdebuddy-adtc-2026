import sys, os, json
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
from llama_cpp import Llama

llm = Llama(model_path="/home/servi/VerdeBuddy/model/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    n_ctx=512, n_threads=4, n_gpu_layers=0, n_batch=128, verbose=False)

print("READY", flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    data = json.loads(line)
    prompt = data["prompt"]
    try:
        r = llm(prompt, max_tokens=50, temperature=0.4, repeat_penalty=1.3, stop=["<|im_end|>", "Human:", "Question:"])
        ans = r["choices"][0]["text"].strip()
        if not ans:
             ans = "Babu bayani a yanzu. Don Allah sake gwadawa."
        words = ans.split()
        clean = []
        for i, w in enumerate(words):
            if i >= 3 and words[i-3:i].count(w) >= 2:
               break
            clean.append(w)
        ans = " ".join(clean)

       
    except Exception as e:
        ans = "Sorry, please try again."
    print(json.dumps({"answer": ans}), flush=True)
