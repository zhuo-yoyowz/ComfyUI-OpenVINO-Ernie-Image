# ComfyUI OpenVINO ERNIE-Image

> 在 ComfyUI 中使用 OpenVINO 后端运行 ERNIE-Image Base INT8 和 ERNIE-Image Turbo INT4，面向 Intel AI PC / Intel GPU 平台优化。

[English README](README.md)

![Sample generated with ERNIE-Image Turbo INT4 and OpenVINO](assets/ComfyUI_00017_.png)

## 项目简介

这个仓库提供一个 ComfyUI 自定义节点，用于在 OpenVINO 后端上运行两个 ERNIE-Image 模型：

- **ERNIE-Image Base INT8**
- **ERNIE-Image Turbo INT4**

支持平台包括：

- Intel 集成显卡
- Intel Arc 独立显卡
- Intel AI PC
- Intel CPU

不依赖 CUDA。

## 主要特性

- 通过同一个 ComfyUI 节点支持 **Base INT8** 和 **Turbo INT4**
- 支持 OpenVINO `GPU`、`GPU.0`、`GPU.1`、`CPU`、`AUTO`
- 支持标准 Optimum OpenVINO Diffusers 模型目录布局
- 支持 Prompt Enhancer：`pe/` + `pe_tokenizer/`
- 提供 ComfyUI 启动脚本、环境检查脚本和 API 验证脚本

## 模型下载

当前仓库支持两个已经转换好的 ModelScope 模型：

- **ERNIE-Image Base INT8**
  `https://www.modelscope.cn/models/yoyowz/ERNIE-Image-ov-int8/`
- **ERNIE-Image Turbo INT4**
  `https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4`

建议下载后的本地目录示例：

```text
C:\models\ERNIE-Image-ov-int8
C:\models\ERNIE-Image-Turbo-ov-int4
```

## 快速开始

### 1. 克隆到 ComfyUI 的 `custom_nodes`

```powershell
cd C:\path\to\ComfyUI\custom_nodes
git clone https://github.com/zhuo-yoyowz/ComfyUI-OpenVINO-Ernie-Image.git
```

### 2. 安装依赖

请在 ComfyUI 使用的同一个 Python 环境中安装依赖：

```powershell
cd C:\path\to\ComfyUI
python -m pip install -r .\custom_nodes\ComfyUI-OpenVINO-Ernie-Image\requirements.txt
```

### 3. 下载模型

可以从 ModelScope 下载一个或两个模型：

```text
https://www.modelscope.cn/models/yoyowz/ERNIE-Image-ov-int8/
https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4
```

或者使用 CLI：

```powershell
python -m pip install modelscope
modelscope download --model yoyowz/ERNIE-Image-ov-int8 --local_dir C:\models\ERNIE-Image-ov-int8
modelscope download --model snake7gun/ERNIE-Image-Turbo-ov-int4 --local_dir C:\models\ERNIE-Image-Turbo-ov-int4
```

### 4. 启动 ComfyUI

```powershell
cd C:\path\to\ComfyUI\custom_nodes\ComfyUI-OpenVINO-Ernie-Image
python .\scripts\start_comfyui_openvino.py --port 8188
```

浏览器打开：

```text
http://127.0.0.1:8188
```

### 5. 添加节点

在 ComfyUI 中添加：

```text
OpenVINO/ERNIE-Image/OpenVINO ERNIE-Image Text to Image
```

然后把节点输出 `image` 连接到 `SaveImage.images`。

## Docker 部署

现在仓库已经支持 Docker 部署。

说明：这条 Docker 部署路径已经在 Windows 本机完成了 CPU 模式验证。
如果你希望在容器中使用 Intel GPU，建议在 Linux 主机上配合可选的
`docker-compose.intel-gpu.yml` override 使用。

已包含的文件：

- `docker/Dockerfile`
- `docker/entrypoint.sh`
- `docker-compose.yml`
- `docker-compose.intel-gpu.yml`

Docker 默认基础镜像使用 `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm`。
这样可以避开部分网络环境下访问 Docker Hub 的连接或限流问题；如果你有自己的
基础镜像，也可以通过 `BASE_IMAGE` build argument 覆盖。

建议宿主机目录结构：

```text
your-workspace/
  ComfyUI-OpenVINO-Ernie-Image/
  models/
    ERNIE-Image-ov-int8/
    ERNIE-Image-Turbo-ov-int4/
```

构建并启动容器：

```powershell
cd C:\path\to\ComfyUI-OpenVINO-Ernie-Image
docker compose up --build
```

启动后访问：

```text
http://127.0.0.1:8188
```

默认挂载关系：

- `./models` -> `/models`
- `./docker-data/output` -> `/opt/ComfyUI/output`
- `./docker-data/input` -> `/opt/ComfyUI/input`
- `./docker-data/user` -> `/opt/ComfyUI/user`

容器内默认模型目录：

```text
/models/ERNIE-Image-ov-int8
```

如果你希望默认指向 Turbo 模型，可以设置：

```powershell
$env:ERNIE_IMAGE_OV_MODEL_DIR="/models/ERNIE-Image-Turbo-ov-int4"
docker compose up --build
```

### Docker 中启用 Intel GPU

在 Linux 主机上，如果要把 Intel GPU 透传给容器，请使用：

```bash
docker compose -f docker-compose.yml -f docker-compose.intel-gpu.yml up --build
```

它会额外挂载：

```text
/dev/dri
```

说明：

- Intel GPU Docker 透传主要面向 Linux 主机
- 如果不加 `docker-compose.intel-gpu.yml`，也可以先用 CPU 方式启动
- 在 Windows Docker Desktop 上，Intel GPU 透传是否可用取决于宿主机和容器运行环境，可能需要额外配置

## 如何在 ComfyUI 中选择不同模型

这个节点同时支持 Base 和 Turbo，切换模型的方式就是修改 `model_dir`。

设备选择建议：

- **默认使用 `GPU.0`**。这是更适合大多数用户的默认值，因为大多数机器只有 Intel 集成显卡，不一定有 Intel 独立显卡。
- 如果你的机器还有被 OpenVINO 识别为 `GPU.1` 的 Intel 独立显卡，可以把 `device`、`text_encoder_device`、`transformer_device`、`vae_decoder_device` 都切换成 `GPU.1`。
- 如果没有独立显卡，就保持 `GPU.0` 即可。

### 运行 ERNIE-Image Base INT8

```text
model_dir: C:\models\ERNIE-Image-ov-int8
```

### 运行 ERNIE-Image Turbo INT4

```text
model_dir: C:\models\ERNIE-Image-Turbo-ov-int4
```

在 ComfyUI 中推荐这样操作：

1. 添加 `OpenVINO ERNIE-Image Text to Image` 节点
2. 把 `model_dir` 改成你想运行的模型本地目录
3. 使用对应模型的推荐参数
4. 点击运行

如果你想做对比测试，可以复制两个节点：

- 一个指向 Base INT8
- 一个指向 Turbo INT4

这样可以在同一个 workflow 里快速比较两个模型。

在 Docker 容器中，对应的 `model_dir` 通常写成：

```text
/models/ERNIE-Image-ov-int8
/models/ERNIE-Image-Turbo-ov-int4
```

## 推荐参数

### Turbo INT4

```text
model_dir: C:\models\ERNIE-Image-Turbo-ov-int4
prompt: a centered whole red apple on a wooden table, studio lighting, sharp focus, high quality
negative_prompt:
device: GPU.0
load_pe: true
use_pe: true
pe_max_new_tokens: 256
text_encoder_device: GPU.0
transformer_device: GPU.0
vae_decoder_device: GPU.0
width: 512
height: 512
steps: 8
guidance_scale: 1.0
seed: 42
```

### Base INT8

```text
model_dir: C:\models\ERNIE-Image-ov-int8
prompt: a centered whole red apple on a wooden table, studio lighting, sharp focus, high quality
negative_prompt:
device: GPU.0
load_pe: true
use_pe: false
pe_max_new_tokens: 256
text_encoder_device: GPU.0
transformer_device: GPU.0
vae_decoder_device: GPU.0
width: 512
height: 512
steps: 20
guidance_scale: 4.0
seed: 42
```

如果你希望严格保持原始 prompt 构图，建议：

```text
load_pe: true
use_pe: false
```

## Workflow 使用说明

仓库中已经提供了两套 workflow：

- [workflows/ernie_image_base_int8_comfyui.json](workflows/ernie_image_base_int8_comfyui.json)
- [workflows/ernie_image_turbo_int4_comfyui.json](workflows/ernie_image_turbo_int4_comfyui.json)

导入后，通常你只需要改 `model_dir` 即可开始运行。

workflow 默认设备已经设置为 `GPU.0`。如果你的机器有 Intel 独立显卡，并且 OpenVINO 中显示为 `GPU.1`，可以再手动改成 `GPU.1`。

## 环境检查

在打开 ComfyUI 之前，建议先运行：

```powershell
python .\scripts\check_env.py --model-dir C:\models\ERNIE-Image-ov-int8
```

或者：

```powershell
python .\scripts\check_env.py --model-dir C:\models\ERNIE-Image-Turbo-ov-int4
```

它会检查：

- Python 包是否安装齐全
- OpenVINO 是否能识别 Intel GPU
- 模型目录结构是否完整
- Prompt Enhancer 文件是否存在

## 为什么启动 ComfyUI 时使用 `--cpu`

在 Intel AI PC 环境里，ComfyUI 启动时可能尝试初始化 CUDA。  
如果当前 PyTorch 是 CPU 版本，可能会报：

```text
AssertionError: Torch not compiled with CUDA enabled
```

因此建议用：

```powershell
python main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch --cpu
```

这里的 `--cpu` 只影响 ComfyUI 自身的 PyTorch 启动行为，**不会强制 ERNIE-Image 节点走 CPU 推理**。  
节点内部仍然通过 OpenVINO 在 Intel GPU 上运行。

本仓库提供的启动脚本会自动加上 `--cpu`：

```powershell
python .\scripts\start_comfyui_openvino.py --port 8188
.\scripts\start_comfyui_openvino.ps1 -Port 8188
```

## API 验证

如果你不想在 UI 里手动点击，也可以直接用脚本做验证。

### Turbo INT4

```powershell
python .\scripts\verify_comfyui_api.py `
  --comfyui-dir C:\path\to\ComfyUI `
  --model-dir C:\models\ERNIE-Image-Turbo-ov-int4 `
  --device GPU `
  --width 512 `
  --height 512 `
  --steps 8 `
  --guidance-scale 1.0 `
  --filename-prefix ov_ernie_turbo_int4_gpu `
  --timeout 1800
```

### Base INT8

```powershell
python .\scripts\verify_comfyui_api.py `
  --comfyui-dir C:\path\to\ComfyUI `
  --model-profile base `
  --model-dir C:\models\ERNIE-Image-ov-int8 `
  --device GPU `
  --width 512 `
  --height 512 `
  --no-use-pe `
  --filename-prefix ov_ernie_base_int8_gpu `
  --timeout 1800
```

生成图片会保存在 ComfyUI 的 `output` 目录。

## 模型目录结构

该节点支持标准 Optimum OpenVINO 模型布局：

```text
ERNIE-Image-ov-int8/ 或 ERNIE-Image-Turbo-ov-int4/
  model_index.json
  openvino_config.json
  scheduler/
  text_encoder/
  tokenizer/
  transformer/
  vae_decoder/
  vae_encoder/
  pe/            # 可选
  pe_tokenizer/  # 可选
```

不支持旧版手工导出的非 Optimum 目录布局。更多说明见：
[docs/MODELS.md](docs/MODELS.md)

## 文档

- [模型导出与目录布局](docs/MODELS.md)
- [常见问题](docs/TROUBLESHOOTING.md)
- [性能说明](docs/PERFORMANCE.md)
- [发布流程](docs/RELEASE_PLAYBOOK.md)
- [GitHub Launch Notes](docs/GITHUB_LAUNCH.md)

## 路线图

- ComfyUI Manager 打包支持
- Linux 启动说明
- Intel Core Ultra / Intel Arc 硬件性能表
- 更多现成 workflow
- 等待上游 Optimum 支持进一步完善后的导出辅助脚本

## 致谢

本项目基于以下项目完成：

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [OpenVINO](https://github.com/openvinotoolkit/openvino)
- [Optimum Intel](https://github.com/huggingface/optimum-intel)
- [ERNIE-Image Turbo](https://huggingface.co/baidu/ERNIE-Image-Turbo)
