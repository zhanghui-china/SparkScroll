from modelscope import snapshot_download
import os

model_dir = snapshot_download('nv-community/NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4', cache_dir='/home/zhanghui/models', revision='master')
