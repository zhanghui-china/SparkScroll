from modelscope import snapshot_download
import os

model_dir = snapshot_download('Qwen/Qwen3.5-9B', cache_dir='/home1/zhanghui/models', revision='master')
