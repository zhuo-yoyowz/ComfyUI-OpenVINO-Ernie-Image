# GitHub Launch Notes

Use this page when creating the public GitHub repository.

## Repository Name

Recommended:

```text
ComfyUI-OpenVINO-Ernie-Image
```

## Short Description

Use this as the GitHub repo description:

```text
Run ERNIE-Image Turbo INT4 in ComfyUI on Intel AI PCs with OpenVINO. No CUDA required.
```

## Website

Use the ModelScope model page or leave empty:

```text
https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4
```

## Topics

Add these GitHub topics:

```text
comfyui
openvino
intel-ai-pc
intel-gpu
ernie-image
text-to-image
diffusion
optimum-intel
modelscope
```

## First Post

Suggested launch post:

```text
I open-sourced a ComfyUI custom node for running ERNIE-Image Turbo INT4 on Intel AI PCs with OpenVINO.

- No CUDA required
- OpenVINO GPU / CPU / AUTO device selection
- Pre-converted Turbo INT4 model on ModelScope
- Prompt Enhancer support
- API smoke test and environment checker included

Repo: https://github.com/zhuo-yoyowz/ComfyUI-OpenVINO-Ernie-Image
Model: https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4
```

## Before Publishing

- Update `LICENSE` copyright owner.
- Confirm the sample image can be used publicly.
- Run `scripts/check_env.py` on the target Intel AI PC.
- Push `main`, then create a `v0.1.0` release.
