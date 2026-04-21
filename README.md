# ComfyUI OpenVINO ERNIE-Image

> ERNIE-Image Turbo INT4 in ComfyUI, accelerated by OpenVINO on Intel AI PCs.

[![OpenVINO](https://img.shields.io/badge/OpenVINO-2026.1-7B61FF)](https://github.com/openvinotoolkit/openvino)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-custom_node-black)](https://github.com/comfyanonymous/ComfyUI)
[![Intel AI PC](https://img.shields.io/badge/Intel-AI_PC-0071C5)](https://www.intel.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Run **ERNIE-Image Turbo INT4** inside **ComfyUI** on **Intel integrated GPUs,
Intel Arc GPUs, and Intel AI PCs**. No CUDA required.

![Sample generated with ERNIE-Image Turbo INT4 and OpenVINO](assets/sample_ernie_turbo_openvino.png)

## Highlights

- **ComfyUI node for ERNIE-Image Turbo** using the OpenVINO backend
- **OpenVINO backend** with `GPU`, `CPU`, and `AUTO` device selection
- **ERNIE-Image Turbo INT4** support through the standard Optimum export layout
- **Prompt Enhancer support** when the exported model contains `pe` and `pe_tokenizer`
- **CUDA-free ComfyUI launchers** for Intel AI PCs
- **API smoke test and environment checker** for repeatable validation

## 60-Second Setup

Clone into ComfyUI's `custom_nodes` directory:

```powershell
cd C:\path\to\ComfyUI\custom_nodes
git clone https://github.com/zhuo-yoyowz/ComfyUI-OpenVINO-Ernie-Image.git
```

Install dependencies into the same Python environment used by ComfyUI:

```powershell
cd C:\path\to\ComfyUI
python -m pip install -r .\custom_nodes\ComfyUI-OpenVINO-Ernie-Image\requirements.txt
```

Download the pre-converted Turbo INT4 OpenVINO model from ModelScope:

```text
https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4
```

Put the downloaded model directory somewhere local, for example:

```text
C:\models\ERNIE-Image-Turbo-ov-int4
```

Optional CLI download:

```powershell
python -m pip install modelscope
modelscope download --model snake7gun/ERNIE-Image-Turbo-ov-int4 --local_dir C:\models\ERNIE-Image-Turbo-ov-int4
```

Start ComfyUI with the Intel AI PC launcher:

```powershell
cd C:\path\to\ComfyUI\custom_nodes\ComfyUI-OpenVINO-Ernie-Image
python .\scripts\start_comfyui_openvino.py --port 8188
```

Open:

```text
http://127.0.0.1:8188
```

Add the node:

```text
OpenVINO/ERNIE-Image/OpenVINO ERNIE-Image Text to Image
```

Connect `image` to `SaveImage.images`.

## Recommended Settings

```text
model_dir: C:\models\ERNIE-Image-Turbo-ov-int4
prompt: a centered whole red apple on a wooden table, studio lighting, sharp focus, high quality
negative_prompt:
device: GPU
load_pe: true
use_pe: true
pe_max_new_tokens: 256
text_encoder_device:
transformer_device:
vae_decoder_device:
width: 512
height: 512
steps: 8
guidance_scale: 1.0
seed: 42
```

For strict composition, keep `load_pe=true` and set `use_pe=false`.

## Check Your Environment

Before opening ComfyUI, run:

```powershell
python .\scripts\check_env.py --model-dir C:\models\ERNIE-Image-Turbo-ov-int4
```

It checks:

- Python package availability
- OpenVINO available devices
- whether `GPU` is visible
- expected ERNIE-Image Turbo model layout
- optional Prompt Enhancer files

## Why `--cpu` Is Used To Start ComfyUI

On Intel AI PCs, ComfyUI may try to initialize CUDA during startup. With a CPU
PyTorch build this can fail with:

```text
AssertionError: Torch not compiled with CUDA enabled
```

Start ComfyUI with `--cpu`:

```powershell
python main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch --cpu
```

This does **not** force ERNIE-Image inference to CPU. It only keeps ComfyUI's
PyTorch device discovery away from CUDA. The ERNIE-Image node still runs through
OpenVINO, and `device=GPU` uses the Intel GPU backend.

The included launchers add `--cpu` automatically:

```powershell
python .\scripts\start_comfyui_openvino.py --port 8188
.\scripts\start_comfyui_openvino.ps1 -Port 8188
```

## API Verification

Use the API smoke test to verify a local model without clicking through the UI:

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

The output image is saved in ComfyUI's `output` directory.

## Example Workflows

- [workflows/ernie_image_turbo_int4_comfyui.json](workflows/ernie_image_turbo_int4_comfyui.json): import into ComfyUI
- [workflows/ernie_image_turbo_int4_api.json](workflows/ernie_image_turbo_int4_api.json): minimal API payload

After loading a workflow, update `model_dir` to your local model path.

## Model Layout

This node supports the standard Optimum OpenVINO layout:

```text
ERNIE-Image-Turbo-ov-int4/
  model_index.json
  openvino_config.json
  scheduler/
  text_encoder/
  tokenizer/
  transformer/
  vae_decoder/
  vae_encoder/
  pe/            # optional
  pe_tokenizer/  # optional
```

Older hand-exported ERNIE-Image folders with `ov_ernie_image_config.json` are
not supported. See [docs/MODELS.md](docs/MODELS.md).

## Project Docs

- [Model export and layout](docs/MODELS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Performance notes](docs/PERFORMANCE.md)
- [Release playbook](docs/RELEASE_PLAYBOOK.md)
- [GitHub launch notes](docs/GITHUB_LAUNCH.md)

## Roadmap

- ComfyUI Manager packaging
- Linux launch notes
- Hardware performance table for Intel Core Ultra and Intel Arc GPUs
- More ready-to-load workflows
- Export helper once upstream Optimum support is fully released

## Acknowledgements

Built around:

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [OpenVINO](https://github.com/openvinotoolkit/openvino)
- [Optimum Intel](https://github.com/huggingface/optimum-intel)
- [ERNIE-Image Turbo](https://huggingface.co/baidu/ERNIE-Image-Turbo)

## License

MIT. Model weights and third-party projects are governed by their own licenses.
