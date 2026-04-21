# Release Playbook

Use this checklist before publishing or tagging a release.

## Before Push

- Set the MIT license copyright owner.
- Confirm the sample image is acceptable for public use.
- Confirm `requirements.txt` points to the intended Optimum Intel support branch.
- Run syntax checks:

```powershell
python -m py_compile nodes.py scripts\check_env.py scripts\verify_comfyui_api.py scripts\start_comfyui_openvino.py
```

- Validate workflow JSON:

```powershell
python -m json.tool workflows\ernie_image_turbo_int4_api.json
python -m json.tool workflows\ernie_image_turbo_int4_comfyui.json
```

## First GitHub Release

Suggested release title:

```text
v0.1.0 - ERNIE-Image Turbo INT4 on Intel AI PCs
```

Suggested release notes:

```text
Initial release:
- ComfyUI text-to-image node for ERNIE-Image Turbo INT4
- OpenVINO GPU/CPU/AUTO device selection
- Prompt Enhancer support
- Intel AI PC launch scripts that avoid CUDA initialization
- API smoke test and environment checker
- Example ComfyUI and API workflows
```

## GitHub Topics

Recommended topics:

```text
comfyui
openvino
intel-ai-pc
intel-gpu
text-to-image
diffusion
ernie-image
optimum-intel
modelscope
```

## Social Preview

Use `assets/sample_ernie_turbo_openvino.png` or create a 1280x640 preview image
from the same sample.

## GitHub Launch

See [GITHUB_LAUNCH.md](GITHUB_LAUNCH.md) for the repository description, topics,
and a short launch post template.
