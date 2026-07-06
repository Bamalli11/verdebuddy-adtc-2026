import sys, os, json, signal

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from llama_cpp import Llama

llm = Llama(
    model_path="/home/servi/VerdeBuddy/model/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    n_ctx=512, n_threads=4, n_gpu_layers=0, n_batch=128, verbose=False
)

sys.stdout.write("READY\n")
sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        data = json.loads(line)
        prompt = data["prompt"]
        r = llm(prompt, max_tokens=150, temperature=0.2, repeat_penalty=1.4,
                stop=["<|im_end|>", "Human:", "Question:", "User:"])
        ans = r["choices"][0]["text"].strip()
        if ans and not ans[-1] in '.?!':
            last = max(ans.rfind('.'), ans.rfind('?'), ans.rfind('!'))
            if last > 30:
                ans = ans[:last+1]
        if not ans:
            ans = "Sorry, I could not find information on that. Please try again."
    except Exception as e:
        ans = "Sorry, something went wrong. Please try again."
    try:
        sys.stdout.write(json.dumps({"answer": ans}) + "\n")
        sys.stdout.flush()
    except BrokenPipeError:
        break