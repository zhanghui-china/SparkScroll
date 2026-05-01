VLLM_USE_MODELSCOPE=true vllm serve \
  /home1/zhanghui/models/Qwen/Qwen3___5-9B \
  --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 131072 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --gpu-memory-utilization 0.32 \
  --served-model-name  DGX-Qwen3.5-9B 

