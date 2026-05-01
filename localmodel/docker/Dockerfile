FROM vllm/vllm-openai:v0.19.0-aarch64-cu130

#ENV PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/"
COPY ./vllm-omni /workspace/vllm-omni

RUN apt update && apt install -y git
RUN pip install -U pip setuptools setuptools-scm

WORKDIR /workspace/vllm-omni 
RUN pip install . --no-build-isolation
RUN pip install orjson

EXPOSE 9000

WORKDIR /mnt/
ENTRYPOINT ["vllm", "serve"]
