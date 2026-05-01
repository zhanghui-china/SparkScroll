docker run --rm -it --ipc=host \
	--ulimit memlock=-1 --ulimit stack=67108864 \
	--gpus=all \
	-v /home/zhanghui/models:/mnt \
	-p 0.0.0.0:8000:8000/tcp nvcr.io/nvidia/tensorrt-llm/release:1.3.0rc10 
