docker run -ti --gpus all --rm \
	-v /home/zhanghui/models/FireRedTeam/FireRed-Image-Edit-1___1:/mnt/ \
	-p 0.0.0.0:9000:9000/tcp \
	--name firered-edit vllm-omni . \
	--served-model-name DGX-FireRed-Image-Edit \
       	--omni \
	--port 9000 \
	--api-key 'sk-caa**0b8'
