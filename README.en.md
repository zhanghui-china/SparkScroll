# SparkScroll

![zongguanxian](zongguanxian.png)



## 📖 Project Introduction

**Project Naming:**

SparkScroll - Intelligent Multi-Modal Content Generation and Editing Platform, Chinese name is "星火绘卷" (Xing Huo Hui Juan). "Spark" directly pays tribute to the NVIDIA DGX Spark platform, and "Scroll" represents comics and picture scrolls. The Chinese name "星火绘卷" combines both a sense of technology and classical literary charm.

**Project Content:**

SparkScroll is a multi-modal creation project for classical literary content generation, building a complete closed loop around "long text understanding -> plot breakdown -> comic strip storyboarding -> page generation -> frontend display".

**Project Highlights:**

This repository contains three core capabilities: `gateway` multi-Agent orchestration service, `client` Streamlit frontend, and local model deployment scripts and instructions in `localmodel`.

- Multi-Agent workflow: covering Director, Writer, CharacterDesigner, Drafting, Editor, Assembler and other stages.
- Dual-end collaboration: `gateway` provides FastAPI and task orchestration, `client` provides project creation, progress tracking, and result browsing.
- Local/remote hybrid models: The repository retains local deployment assets for Qwen3.5-9B, Qwen-Image-Edit-2511, and FireRed-Image-Edit-1.1, and has integrated DashScope and OpenAI-style vLLM image editing providers.
- Complete deliverables: including project report, release wheel packages, and pipeline configuration, facilitating demonstration, testing, and delivery.

## 📆 Update Notes and Team Dynamics

[2026.4.10] **Zhang Xiaobai** published "Deploying NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4 Model on Nvidia DGX Spark using TensorRT-LLM": https://zhuanlan.zhihu.com/p/2025685426493506830

[2026.4.9] **Zhang Xiaobai** published "Deploying FireRed-Image-Edit Image Editing Model Service on Nvidia DGX Spark using Docker": https://zhuanlan.zhihu.com/p/2025459284385743751, **Hanchen** published "TensorRT-LLM Model Deployment NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4 Record": https://gitee.com/zhanghui_china/SparkScroll/tree/master/localmodel/TensorRT-LLM/NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4, **Feige** submitted "Journey to the West Comic Version with Storyline": https://gitee.com/zhanghui_china/SparkScroll/commit/906deb509f4b2f5726c159dd8b9b271df2e5dbed, **Zhang Xiaobai** published project introduction video (updated version): https://www.bilibili.com/video/BV1JJDxBAETr/

[2026.4.8] **Zhang Xiaobai** published "SparkScroll Project Operation Guide": https://zhuanlan.zhihu.com/p/2024950757548401621, **Feige** published "NVIDIA First DGX Spark Full-Stack AI Hackathon Results Showcase" video: https://www.bilibili.com/video/BV1CVDjBLE7C, **Zhang Xiaobai** and **Feige** submitted competition certificates: https://gitee.com/zhanghui_china/SparkScroll/blob/master/certificate/certificate.md

[2026.4.7] **Zhang Xiaobai** published project introduction video (first draft): https://www.bilibili.com/video/BV1tnDiBGEDo/

[2026.4.6] **Hanchen** released sparkscroll_gateway version 2.3.0, upgraded vLLM image model API support. **Zhang Xiaobai** wrote competition submission documents. **Feige** further conducted frontend integration and testing.

[2026.4.5] **Hanchen** released sparkscroll_gateway versions 2.2.2-2.2.7. **Zhang Xiaobai** optimized frontend UI docking test code, and found the problem of "abnormal display of Chinese on images" in local models during integration. **Zhang Xiaobai** deployed FireRed-Image-Edit-1.1 model to replace Qwen-Image-Edit-2511 local model for verification, and dual local model testing was successful.

[2026.4.4] **Hanchen** released sparkscroll_gateway versions 2.1.8-2.2.0. **Zhang Xiaobai** deployed Qwen3.5 9B model on Spark, used Little Red Riding Hood for local text and remote image generation hybrid model testing, and solved the model call timeout BUG. **Feige** issued project description and technology stack description documents, and began to organize frontend call details documents. **Zhang Xiaobai** used "The Little Match Girl" for Gateway Spark local deployment and dual local model integration, solved 400 error, and added MTP parameter to vLLM startup.

[2026.4.3] **Hanchen** asked codex to solve the BUG of "sketch Agent shutdown" due to sensitive words failing review, solved the BUG of "image output shutdown", and increased the robustness of Director Agent. **Zhang Xiaobai** conducted generation tests using the first and second chapters of "Journey to the West".

[2026.4.2] The project team discussed frontend calling process. Held the second Tencent meeting. **Feige** began frontend vibe coding. **Zhang Hui** conducted UI docking vibe coding and cloud integration based on the Gateway version provided by Hanchen using Trae. **Hanchen** asked codex to solve the "Editing Agent shutdown" BUG.

[2026.4.1] **Hanchen** conducted Gateway code debugging.

[2026.3.31] **Hanchen** issued project module design document and started codex programming.

[2026.3.30] **Zhang Xiaobai** established gitee code repository: https://gitee.com/zhanghui_china/SparkScroll. Team members conducted directory planning and submitted code.

[2026.3.30] **Hanchen** successfully deployed Qwen3.5 9B local model: https://zhuanlan.zhihu.com/p/2023695422703575616. **Zhang Xiaobai** successfully deployed Qwen-Image-Edit-2511 local model: https://zhuanlan.zhihu.com/p/2022011775193718931

[2026.3.29] All members of the **Zongguanxian Team** participated in the Hackathon opening event.

[2026.3.27] **Zhang Xiaobai** provided dynamic secondary domain name ssh channel and http channel access to Nvidia DGX Spark device for team sharing, and provided Spark device physical expansion method: https://zhuanlan.zhihu.com/p/2020920979497428602

[2026.3.26] **Hanchen** issued project technical white paper and provided cloud testing environment, determined to use codex for vibe coding, initially decided that the coding process does not rely on local computing power, and first used cloud large models for debugging.

[2026.3.24] **Hanchen** suggested the project name as SparkScroll (Chinese name: 星火绘卷), which was widely accepted~~

[2026.3.22] **Zhang Xiaobai** completed the configuration of OpenClaw multi-Agent, established a Feishu group with 3 real people + 9 AI robots for the Zongguanxian Team: https://zhuanlan.zhihu.com/p/2018745391802261631. Further improved the project concept, generated project evaluation report and MVP prototype diagram.

[2026.3.20] The **Zongguanxian Team** put forward the initial idea - inputting world classic novel texts, OpenClaw calls skills for article abbreviation, and calls local text-to-image large models to generate comic strips. Consider using comic strip data for fine-tuning to adjust model style. The specific scenario can be popularizing world famous works for children, or advocating the "easy reading of famous works" scenario for working people who don't read books.

[2026.3.16] The **Zongguanxian Team** held the first video conference for brainstorming.

[2026.3.13] The **Zongguanxian Team** was established, consisting of **Zhang Xiaobai** (**Zhang Hui**, from Nanjing), **Hanchen** (from Beijing), and **Qin Feixiong** (**Feige**, from Guangzhou). **Zhang Xiaobai** published "Nvidia DGX Spark Initial Experience": https://zhuanlan.zhihu.com/p/2013726822618116929

[2026.3.12] **Zhang Xiaobai** published "Docker Deployment of OpenClaw on Nvidia DGX Spark": https://zhuanlan.zhihu.com/p/2014441844394705834

## 🗂️ Document Navigation

| Path | Description |
| :--- | :--- |
| [README.md](https://gitee.com/zhanghui_china/SparkScroll/blob/9cc60bfd73417e460908e4a753321a2799e44c63/README.md) | Chinese Overview |
| [README.en.md](https://gitee.com/zhanghui_china/SparkScroll/blob/9cc60bfd73417e460908e4a753321a2799e44c63/README.en.md) | English Overview |
| [gateway/README.md](https://gitee.com/zhanghui_china/SparkScroll/blob/9cc60bfd73417e460908e4a753321a2799e44c63/gateway/README.md) | Gateway Service Instructions, Interfaces and Deployment |
| [client/README.md](https://gitee.com/zhanghui_china/SparkScroll/blob/9cc60bfd73417e460908e4a753321a2799e44c63/client/README.md) | Streamlit Frontend Instructions |
| [localmodel/Qwen3.5-9B/README.md](https://gitee.com/zhanghui_china/SparkScroll/blob/9cc60bfd73417e460908e4a753321a2799e44c63/localmodel/Qwen3.5-9B/README.md) | Qwen3.5-9B Local Deployment Instructions |
| [localmodel/Qwen-Image-Edit-2511/README.md](https://gitee.com/zhanghui_china/SparkScroll/blob/9cc60bfd73417e460908e4a753321a2799e44c63/localmodel/Qwen-Image-Edit-2511/README.md) | Qwen Image Editing Model Deployment Instructions |
| [report/project_report.md](https://gitee.com/zhanghui_china/SparkScroll/blob/9cc60bfd73417e460908e4a753321a2799e44c63/report/project_report.md) | Project Report and Competition Materials |

## 🗺️ Technical Architecture

This project is specifically tailored for **NVIDIA DGX Spark (GB10 128G shared memory)**. To completely widen the gap with ordinary consumer-grade graphics cards (such as RTX 4090 24G), SparkScroll adopts a **"Memory-Resident Multi-Model" architecture**:

| Module | Selection | Memory Resident Budget | Absolute Necessity of DGX Spark |
| :--- | :--- | :--- | :--- |
| **Text and Logic Brain** | Qwen3.5-9B (actual 128K context, driven by vLLM v0.19.0) | **~40GB** | 128K context is sufficient to cover most novel full-text understanding, stably supporting plot compression, cross-episode planning and structured storyboard generation. |
| **Visual Rendering Core** | Qwen-Image-Edit-2511 / FireRed-Image-Edit-1.1 (local dual models) | **50~60GB** | Balancing high-fidelity character consistency editing and Chinese subtitle rendering capabilities, need to reserve enough memory for local image editing models. Forced quantization will cause loss of typesetting geometric reasoning ability. |
| **Framework and Concurrency Buffer** | vLLM v0.19.0, FastAPI, Diffusers, vLLM-Omni adaptation layer, OS | **~15GB** | Supports API flow, self-developed scheduling, model services and image editing calls, need to reserve safe redundancy for cache, scheduling and system operation. |
| **Total** | -- | **110~115GB / 128G** | **Ordinary single-card systems cannot run this concurrent pipeline at all.** Only DGX Spark can achieve "zero Swap" ultimate second-level response, supporting multi-Agent rapid switching and streaming presentation. |

## ✨ Project Report

[Project Report] https://gitee.com/zhanghui_china/SparkScroll/blob/master/report/project_report.md

[Competition Certificate] https://gitee.com/zhanghui_china/SparkScroll/blob/master/certificate/certificate.md

## 📋 Project Code Structure

```
The following structure is organized according to the 2026-04-09 repository snapshot, omitting environment and cache directories such as .git, .venv, __pycache__.

SparkScroll/
├── certificate/                        # Competition certificate
├── client/                             # Streamlit frontend (Zhang Xiaobai)
│   ├── app_streamlit.py                # Frontend entry
│   ├── static/                         # Static page resources
│   ├── generated/                      # Download image output directory
│   ├── *.db                            # Local SQLite data
│   ├── 操作手册.md                      # Frontend operation manual
│   └── README.md                       # Frontend instructions
├── client_vue/                         # Vue frontend (Feige)  
│   ├── spark-client/                    
│   │   ├── src/                        # Core source code
├── .workflow/                          # Branch, trunk, PR pipeline configuration
├── gateway/                            # Multi-Agent Gateway service (Hanchen)
│   ├── config.yaml                     # Service configuration
│   ├── docs/                           # Deployment and supplementary documentation
│   ├── examples/                       # Example configurations and call samples
│   ├── presets/                        # Preset fonts, layouts, project templates
│   ├── resource/                       # Three-view and page template images
│   ├── scripts/                        # Auxiliary scripts
│   ├── src/sparkscroll_gateway/        # Core source code
│   │   ├── agents/                     # Agent definitions and runtime
│   │   ├── api/                        # FastAPI application and interface schema
│   │   ├── application/                # Application layer DTO
│   │   ├── config/                     # Configuration models and loaders
│   │   ├── domain/                     # Domain models and state machines
│   │   ├── model_gateway/              # Text/image model adaptation layer
│   │   ├── repositories/               # File system and Redis storage
│   │   ├── services/                   # Project, workflow and execution services
│   │   ├── utils/                      # Resource layout, serialization and other tools
│   │   ├── workflows/                  # Workflow coordinator
│   │   └── cli.py                      # CLI entry
│   ├── tests/                          # Unit, contract, integration tests
│   ├── data/                           # Runtime cache, logs, project products
│   │   ├── cache/
│   │   ├── logs/
│   │   ├── projects/
│   │   └── system_presets/
│   ├── build/                          # Build intermediate products
│   ├── dist/                           # Build output directory
│   ├── pyproject.toml                  # Python packaging configuration
│   └── README.md                       # Gateway instructions
├── localmodel/                         # Local model deployment scripts and instructions
│   ├── origin/                         # Native deployment
│   │   ├── Qwen-Image-Edit-2511/       # Image editing model native deployment: Qwen
│   │   ├── FireRed-Image-Edit-1.1/     # Image editing model native deployment: Xiaohongshu
│   ├── vllm                            # conda VLLM deployment
│   │   ├── Qwen3.5-9B/                 # Text model vllm deployment: Qwen
│   ├── docker/                         # Docker deployment
│   │   ├── Qwen3.5-9B/                 # Text model Docker deployment: Qwen
│   │   ├── FireRed-Image-Edit-1.1/     # Image editing model Docker deployment: Xiaohongshu
│   ├── TensorRT-LLM/                   # TensorRT-LLM docker deployment
│   │   ├── NVIDIA-Nemotron-3-Nano-30B-A3B-NVFP4/     # Text model: NVIDIA-Nemotron-3-Nano
├── release/                            # Built sparkscroll_gateway wheel packages
├── report/                             # Project report
├── ppt/                                # Project presentation        
├── nvidia-logo.png                     # Acknowledgment resources
├── gpus-logo.png                       # Acknowledgment resources
├── zanqi-logo.png                      # Acknowledgment resources
├── README.md                           # Chinese documentation
├── README.en.md                        # English documentation
└── LICENSE                             # Apache License 2.0
```

## 🚀 Quick Start

### 1. Start Gateway

```
cd gateway
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .[dev]
export SPARKSCROLL_API_KEY=...
export SPARKSCROLL_TEXT_API_KEY=...
export SPARKSCROLL_IMAGE_API_KEY=...
python3 -m sparkscroll_gateway --config ./config.yaml --reload
```

### 2. Start Frontend

```
cd client
python3 -m pip install streamlit requests
streamlit run app_streamlit.py
```

Before starting, please confirm that `GATEWAY_BASE_URL` and `API_KEY` are configured correctly in `client/app_streamlit.py`; if you need to deploy local text/image models, please refer to the deployment scripts and instructions under `localmodel/` first.

## ☕ Project Team - Zongguanxian

The team is named "Zongguanxian" (纵贯线), which comes from the fact that team members are from Beijing-Nanjing-Guangzhou, like a line running through the country.

BTW: The Zongguanxian (Super Band) from Taiwan, China is composed of [Luo Dayou](https://baike.baidu.com/item/罗大佑/236869?fromModule=lemma_inlink), [Li Zongsheng](https://baike.baidu.com/item/李宗盛/438185?fromModule=lemma_inlink), [Zhou Huajian](https://baike.baidu.com/item/周华健/6700?fromModule=lemma_inlink), and [Zhang Zhenyue](https://baike.baidu.com/item/张震岳/440264?fromModule=lemma_inlink).

| Member | Responsibility | Contribution |
| ------ | ------------- | ------------ |
| Zhang Xiaobai | Team Leader, Project Planning | Project scenario planning, project management and team communication, local deployment and service of Qwen3.5-9B and Qwen-Image-Edit-2511 models, frontend UI development and debugging |
| Hanchen | Team Member, Architecture Design, Code Responsibility | Design system overall architecture, develop technical roadmap, coordinate module development, Gateway development leader |
| Qin Feixiong | Team Member, Testing and Documentation | Frontend UI development and debugging, system testing, technical documentation, competition materials preparation, etc. |
| Codex | Gateway Server Development | Design and implement backend API services |
| Trae | Frontend UI Development | Design user-friendly frontend interface, provide intuitive model operation entry |

## 💖 Special Thanks

Thank you to Nvidia for hosting this Hackathon event

![1372c345249308e6df60e9bc13346ab8](nvidia-logo.png)

Thank you to GPUS developers for providing competition support

![d36155b90cab1c9d1dc347ad822fea9e](gpus-logo.png)

Thank you to Zanqi Technology for providing competition equipment support

![78a608fc18d7f23073836da07417fe68](zanqi-logo.png)

## Open Source License

This project adopts the [Apache License 2.0 open source license](https://github.com/SmartFlowAI/TheGodOfCookery/blob/main/LICENSE).
