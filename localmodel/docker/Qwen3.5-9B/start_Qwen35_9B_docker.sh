docker run -d --gpus all --rm \
       -v /home/zhanghui/models/Qwen/Qwen3___5-9B:/mnt/ \
       -p 0.0.0.0:8000:8000/tcp \
       --name qwen35_9b vllm/vllm-openai:cu130-nightly /mnt/Qwen3.5-9B 
       --served-model-name DGX-Qwen3.5-9B 
       --config /mnt/model_qwen35_p8000.yaml 
       --speculative-config '{"method": "mtp", "num_speculative_tokens": 1}'
