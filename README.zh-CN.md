# ComfyUI OpenVINO ERNIE-Image

> 在 Intel AI PC 上，用 OpenVINO backend 在 ComfyUI 里运行 ERNIE-Image Base INT8 和 Turbo INT4。

[English README](README.md)

![Sample generated with ERNIE-Image Turbo INT4 and OpenVINO](assets/sample_ernie_turbo_openvino.png)

## 这个项目解决什么问题

这个 custom node 把 ERNIE-Image Base INT8、ERNIE-Image Turbo INT4、OpenVINO 和 ComfyUI 串成一个干净的本地文生图工作流：

- 面向 Intel AI PC 和 Intel GPU 的 ERNIE-Image ComfyUI 节点
- 不需要 CUDA
- 支持 OpenVINO `GPU`、`CPU`、`AUTO`
- 支持 Optimum/OpenVINO 标准导出目录
- 支持 Prompt Enhancer，也可以关闭 PE 改写以获得更稳定构图
- 提供启动脚本，避免 ComfyUI 初始化 CUDA 报错
- 提供 API 验证脚本和环境检查脚本

## 快速开始

把仓库 clone 到 ComfyUI 的 `custom_nodes` 目录：

```powershell
cd C:\path\to\ComfyUI\custom_nodes
git clone https://github.com/zhuo-yoyowz/ComfyUI-OpenVINO-Ernie-Image.git
```

安装依赖：

```powershell
cd C:\path\to\ComfyUI
python -m pip install -r .\custom_nodes\ComfyUI-OpenVINO-Ernie-Image\requirements.txt
```

从 ModelScope 下载已经转换好的 Turbo INT4 OpenVINO 模型：

```text
https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4
```

把下载后的模型目录放到本地路径，例如：

```text
C:\models\ERNIE-Image-Turbo-ov-int4
```

如果使用 ERNIE-Image Base INT8，请准备 Optimum/OpenVINO 标准目录，例如：

```text
C:\models\ERNIE-Image-ov-int8
```

也可以使用 ModelScope CLI 下载：

```powershell
python -m pip install modelscope
modelscope download --model snake7gun/ERNIE-Image-Turbo-ov-int4 --local_dir C:\models\ERNIE-Image-Turbo-ov-int4
```

启动 ComfyUI：

```powershell
cd C:\path\to\ComfyUI\custom_nodes\ComfyUI-OpenVINO-Ernie-Image
python .\scripts\start_comfyui_openvino.py --port 8188
```

打开：

```text
http://127.0.0.1:8188
```

添加节点：

```text
OpenVINO/ERNIE-Image/OpenVINO ERNIE-Image Text to Image
```

把该节点的 `image` 输出连接到 `SaveImage` 的 `images` 输入。

## 推荐参数

Turbo INT4：

```text
model_dir: C:\models\ERNIE-Image-Turbo-ov-int4
device: GPU
load_pe: true
use_pe: true
width: 512
height: 512
steps: 8
guidance_scale: 1.0
seed: 42
```

Base INT8：

```text
model_dir: C:\models\ERNIE-Image-ov-int8
device: GPU
load_pe: true
use_pe: false
width: 512
height: 512
steps: 20
guidance_scale: 4.0
seed: 42
```

如果需要严格控制构图，建议：

```text
load_pe: true
use_pe: false
```

## 环境检查

在启动 ComfyUI 前，可以先运行：

```powershell
python .\scripts\check_env.py --model-dir C:\models\ERNIE-Image-Turbo-ov-int4
```

它会检查 Python 包、OpenVINO 可用设备、`GPU` 是否可见、模型目录是否符合 Optimum 标准布局，以及是否包含 PE 模型。

## 为什么启动时要加 --cpu

Intel AI PC 场景下，ComfyUI 启动时建议加 `--cpu`：

```powershell
python main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch --cpu
```

这里的 `--cpu` 只是避免 ComfyUI/PyTorch 尝试初始化 CUDA，不会让 ERNIE-Image 改成 CPU 推理。节点里的 `device=GPU` 仍然会通过 OpenVINO 使用 Intel GPU。

本项目提供的启动脚本会自动加 `--cpu`：

```powershell
python .\scripts\start_comfyui_openvino.py --port 8188
.\scripts\start_comfyui_openvino.ps1 -Port 8188
```

## API 验证

```powershell
python .\scripts\verify_comfyui_api.py `
  --comfyui-dir C:\path\to\ComfyUI `
  --model-dir C:\models\ERNIE-Image-Turbo-ov-int4 `
  --device GPU `
  --width 512 `
  --height 512 `
  --steps 8 `
  --guidance-scale 1.0 `
  --timeout 1800
```

验证 Base INT8：

```powershell
python .\scripts\verify_comfyui_api.py `
  --comfyui-dir C:\path\to\ComfyUI `
  --model-profile base `
  --model-dir C:\models\ERNIE-Image-ov-int8 `
  --device GPU `
  --width 512 `
  --height 512 `
  --no-use-pe `
  --timeout 1800
```

更多说明见英文 README 和 `docs/` 目录。
