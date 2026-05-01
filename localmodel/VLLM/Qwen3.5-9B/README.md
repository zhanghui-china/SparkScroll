# Qwen3.5-9B 模型部署指南

## 背景
Qwen3.5-9B 模型是一个受到好评的大语言模型，本文档提供了完整的部署步骤。

## 环境安装

### 1. 准备conda环境
```bash
conda create -n qwen35 python=3.13 -y
```

### 2. 安装vllm
```bash
conda activate qwen35
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu129
```

### 3. 验证vllm安装
```bash
vllm
```

## 下载模型

### 1. 创建下载脚本
创建 `download_model_by_modelscope_Qwen3.5-9B.py` 文件：
```python
from modelscope import snapshot_download
import os

model_dir = snapshot_download('Qwen/Qwen3.5-9B', cache_dir='/home1/zhanghui/models', revision='master')
```

### 2. 执行下载
```bash
python download_model_by_modelscope_Qwen3.5-9B.py
```

### 3. 查看下载结果
下载完毕后，模型会保存在以下目录：
```
/home1/zhanghui/models/Qwen/Qwen3___5-9B
```

## 启动服务

### 1. 基本启动命令
```bash
VLLM_USE_MODELSCOPE=true vllm serve /home1/zhanghui/models/Qwen/Qwen3___5-9B --port 8000 --tensor-parallel-size 1 --max-model-len 262144 --reasoning-parser qwen3 --enable-auto-tool-choice --tool-call-parser qwen3_coder
```

### 2. 调整内存使用率
创建 `start_qwen35.sh` 脚本：
```bash
VLLM_USE_MODELSCOPE=true vllm serve \
  /home1/zhanghui/models/Qwen/Qwen3___5-9B \
  --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 262144 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --gpu-memory-utilization 0.3  # 限制显存使用率为30%
```

### 3. 启动服务
```bash
chmod +x start_qwen35.sh
./start_qwen35.sh
```

## 配置Cherry Studio

### 1. 打开设置
点击左下角的“设置”，选择本地模型。

### 2. 输入API地址
```
http://192.168.199.107:8000
```
其中 `192.168.199.107` 是服务器的IP地址。

### 3. 添加模型
直接输入模型的全路径即可。

## 验证服务

### 1. 切换模型
切换到Cherry Studio的对话窗口，在上方选择本地对应的9B模型。

### 2. 测试对话
```
hello
你是什么模型？你能做什么？
```

### 3. 验证结果
如果服务正常，模型会返回相应的回答，说明服务可以正常使用。

## 内存使用情况

### 检查内存使用
启动服务后，可以通过系统工具检查内存使用情况。

### 调整内存限制
通过 `--gpu-memory-utilization` 参数可以调整显存使用率，例如设置为30%。

## 在本项目部署Qwen3.5-9B本地模型

### 部署步骤
1. **进入conda环境**：
   ```bash
   conda activate qwen35
   ```

2. **启动服务**：
   ```bash
   chmod +x start_qwen35.sh
   ./start_qwen35.sh
   ```

服务启动后，即可通过配置的端口访问本地模型。