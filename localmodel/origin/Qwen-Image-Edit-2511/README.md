# Qwen-Image-Edit-2511 模型部署指南

## 背景
Qwen-Image-Edit-2511 是一个性能优秀的开源图像编辑模型，在开源文生图模型中排名第3位（第一名是腾讯的混元）。本文档提供了完整的部署和使用指南。

## 模型准备

### 1. 下载模型
创建 `download_model_by_modelscope_Qwen-Image-Edit-2511.py` 文件：
```python
from modelscope import snapshot_download
import os

model_dir = snapshot_download('Qwen/Qwen-Image-Edit-2511', cache_dir='/home1/zhanghui/models', revision='master')
```

执行下载：
```bash
python download_model_by_modelscope_Qwen-Image-Edit-2511.py
```

检查下载结果（模型大小约52G）：
```bash
cd /home1/zhanghui/models/Qwen/Qwen-Image-Edit-2511
du -h
```

## 使用官方范例运行模型推理

### 1. 准备conda环境
```bash
conda create -n qwenimage python=3.13 -y 
conda activate qwenimage
```

### 2. 安装依赖包
```bash
# 安装diffusers
pip install git+https://github.com/huggingface/diffusers

# 安装CUDA13对应的Pytorch
pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu130

# 验证CUDA支持
python -c "import torch; print(torch.cuda.is_available())"

# 安装transformers
pip install transformers

# 安装加速库
pip install accelerate
```

### 3. 准备推理脚本
创建 `test_Qwen-Image-Edit-2511.py` 文件：
```python
import os
import torch
import time
from PIL import Image
from diffusers import QwenImageEditPlusPipeline

pipeline = QwenImageEditPlusPipeline.from_pretrained("/home1/zhanghui/models/Qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16)
print("pipeline loaded")

pipeline.to('cuda')
pipeline.set_progress_bar_config(disable=None)
image1 = Image.open("image1.png")
prompt = "生成圣诞节主题，一位纯欲气质的美少女，图中人脸不变。松散的双麻花辫松散低扎(麻花辫上有布艺彩球装饰)少女气质，无辜眼神，头戴圣诞树造型发饰，小型锥形圣诞树整齐地固定在头顶，顶部是金色五角星，树身装饰着彩色灯串、金色铃铛、蝴蝶结、红蓝金小球，布置精致饱满;冷白皮，白嫩嫩的皮肤如琼玉般嫩滑，纯欲朦胧滤镜，红棕系眼影自然晕染，双手拿着圣诞老人玩偶，圣诞氛围拉满，庆祝感眼神和表情，轻轻歪头，俏皮又好看的动作，可爱与性感并存，反差;蓬松微乱发丝与头顶圣诞树自然融合;穿毛绒红色上衣，质感柔软蓬松;暖白背景、棚拍柔光、低对比度、低饱和度、细腻胶片颗粒轻微色散光晕、胶片柔光感、温暖治愈氛围、独特视角，非常规构图，70mm胶片人像风格绿色涂鸦描边人物轮廓描边周围空白处还有各种圣诞节元素的可爱涂鸦，充满童趣和圣诞氛围的手绘拼贴感。人物轮廓荧光红绿金色虚线波点包裹，写满了“MERRYCHRISMAS”可爱字体，中景"

inputs = {
    "image": [image1],
    "prompt": prompt,
    "generator": torch.manual_seed(0),
    "true_cfg_scale": 4.0,
    "negative_prompt": " ",
    "num_inference_steps": 40,
    "guidance_scale": 1.0,
    "num_images_per_prompt": 1,
}

with torch.inference_mode():
    # 记录推理开始时间
    start_time = time.time()

    output = pipeline(**inputs)

    # 记录推理结束时间
    end_time = time.time()

    output_image = output.images[0]
    output_image.save("output_image_edit_2511.png")
    print("image saved at", os.path.abspath("output_image_edit_2511.png"))

    # 计算并打印推理所花费的时间
    inference_time = end_time - start_time
    print(f"真正推理部分花了 {inference_time:.2f} 秒")
```

### 4. 准备测试图片
将测试图片保存为 `image1.png`

### 5. 执行模型推理
```bash
python test_Qwen-Image-Edit-2511.py
```

**运行情况**：
- 统一内存：约68.64G
- GPU利用率：基本满负荷

### 6. 将模型推理包装成HTTP服务
创建 `test_Qwen-Image-Edit-2511_service.py` 文件：
```python
import os
import torch
import time
from PIL import Image
from flask import Flask, request, jsonify
from diffusers import QwenImageEditPlusPipeline
from werkzeug.utils import secure_filename


app = Flask(__name__)

# 配置上传文件夹、输出文件夹和允许的文件扩展名
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 初始化模型
pipeline = QwenImageEditPlusPipeline.from_pretrained("/home1/zhanghui/models/Qwen/Qwen-Image-Edit-2511", torch_dtype=torch.bfloat16)
pipeline.to('cuda')
pipeline.set_progress_bar_config(disable=None)

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 图像编辑API
@app.route('/edit', methods=['POST'])
def edit_image():
    # 检查请求中是否有文件部分
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 检查文件类型是否允许
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # 获取提示文本
    prompt = request.form.get('prompt', '')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # 保存上传的文件
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # 加载图片
        image = Image.open(filepath)
        
        # 准备输入
        inputs = {
            "image": [image],
            "prompt": prompt,
            "generator": torch.manual_seed(0),
            "true_cfg_scale": 4.0,
            "negative_prompt": " ",
            "num_inference_steps": 40,
            "guidance_scale": 1.0,
            "num_images_per_prompt": 1,
        }
        
        # 执行推理
        start_time = time.time()
        with torch.inference_mode():
            output = pipeline(**inputs)
        end_time = time.time()
        
        # 保存输出图片
        output_filename = f"output_{int(time.time())}.png"
        output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        output_image = output.images[0]
        output_image.save(output_filepath)
        
        # 返回结果
        return jsonify({
            'success': True,
            'output_image': output_filename,
            'inference_time': f"{end_time - start_time:.2f}秒"
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 7. 使用curl验证服务
启动服务：
```bash
python test_Qwen-Image-Edit-2511_service.py
```

使用curl发送请求：
```bash
curl -X POST http://localhost:5000/edit \
  -F "image=@image1.png" \
  -F "prompt=生成圣诞节主题，一位纯欲气质的美少女，图中人脸不变"
```

## 性能参考
- **模型大小**：约52G
- **内存需求**：约68.64G统一内存
- **GPU利用率**：基本满负荷

## 注意事项
1. 确保服务器有足够的内存和GPU资源
2. 推理时间较长，建议在后台运行
3. 模型下载需要较大的存储空间
4. 依赖包版本需要严格按照文档要求安装

## 在本项目部署Qwen-Image-Edit-2511本地模型

### 部署步骤
1. **进入conda环境**：
   ```bash
   conda activate qwenimage
   ```

2. **启动服务**：
   ```bash
   python image_edit_service.py
   ```

服务启动后，即可通过配置的端口访问本地模型。