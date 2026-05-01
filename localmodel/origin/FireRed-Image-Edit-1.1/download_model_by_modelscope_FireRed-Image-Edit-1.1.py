from modelscope import snapshot_download
import os

model_dir = snapshot_download('FireRedTeam/FireRed-Image-Edit-1.1', cache_dir='/home1/zhanghui/models', revision='master')
