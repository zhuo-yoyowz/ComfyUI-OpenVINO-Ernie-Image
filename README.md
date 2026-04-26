# ComfyUI OpenVINO ERNIE-Image

> ERNIE-Image Base INT8 and Turbo INT4 in ComfyUI, accelerated by OpenVINO on Intel AI PCs.

[![OpenVINO](https://img.shields.io/badge/OpenVINO-2026.1-7B61FF)](https://github.com/openvinotoolkit/openvino)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-custom_node-black)](https://github.com/comfyanonymous/ComfyUI)
[![Intel AI PC](https://img.shields.io/badge/Intel-AI_PC-0071C5)](https://www.intel.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Run **ERNIE-Image Base INT8** and **ERNIE-Image Turbo INT4** inside **ComfyUI** on **Intel integrated GPUs,
Intel Arc GPUs, and Intel AI PCs**. No CUDA required.

![Sample generated with ERNIE-Image Turbo INT4 and OpenVINO](assets/ComfyUI_00017_.png)

## Highlights

- **ComfyUI node for two OpenVINO ERNIE-Image models**: Base INT8 and Turbo INT4
- **OpenVINO backend** with `GPU`, `CPU`, and `AUTO` device selection
- **ERNIE-Image Base INT8 and Turbo INT4** support through the standard Optimum export layout
- **Prompt Enhancer support** when the exported model contains `pe` and `pe_tokenizer`
- **CUDA-free ComfyUI launchers** for Intel AI PCs
- **API smoke test and environment checker** for repeatable validation

## Model Downloads

This repository currently supports two pre-converted OpenVINO models on ModelScope:

- **ERNIE-Image Base INT8**
  `https://www.modelscope.cn/models/yoyowz/ERNIE-Image-ov-int8/`
- **ERNIE-Image Turbo INT4**
  `https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4`

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

Download one or both pre-converted OpenVINO models from ModelScope:

```text
https://www.modelscope.cn/models/yoyowz/ERNIE-Image-ov-int8/
https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4
```

Put the downloaded model directories somewhere local, for example:

```text
C:\models\ERNIE-Image-ov-int8
C:\models\ERNIE-Image-Turbo-ov-int4
```

Optional CLI download:

```powershell
python -m pip install modelscope
modelscope download --model yoyowz/ERNIE-Image-ov-int8 --local_dir C:\models\ERNIE-Image-ov-int8
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

## Docker Deployment

Yes, this project now includes a Docker deployment path.

Note: Docker deployment has been verified locally on Windows with CPU execution.
If you want Intel GPU passthrough inside the container, use a Linux host with the
optional `docker-compose.intel-gpu.yml` override.

Included files:

- `docker/Dockerfile`
- `docker/entrypoint.sh`
- `docker-compose.yml`
- `docker-compose.intel-gpu.yml`

The default Docker base image is `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm`.
This avoids Docker Hub connectivity or rate-limit issues on some networks. If needed, you can
override it with the `BASE_IMAGE` build argument.

Recommended host layout:

```text
your-workspace/
  ComfyUI-OpenVINO-Ernie-Image/
  models/
    ERNIE-Image-ov-int8/
    ERNIE-Image-Turbo-ov-int4/
```

Build and start the container:

```powershell
cd C:\path\to\ComfyUI-OpenVINO-Ernie-Image
docker compose up --build
```

This starts ComfyUI on:

```text
http://127.0.0.1:8188
```

By default, the compose file mounts:

- `./models` to `/models`
- `./docker-data/output` to `/opt/ComfyUI/output`
- `./docker-data/input` to `/opt/ComfyUI/input`
- `./docker-data/user` to `/opt/ComfyUI/user`

Default model inside the container:

```text
/models/ERNIE-Image-ov-int8
```

If you want to change the default model path, set:

```powershell
$env:ERNIE_IMAGE_OV_MODEL_DIR="/models/ERNIE-Image-Turbo-ov-int4"
docker compose up --build
```

### Intel GPU in Docker

For Intel GPU acceleration on Linux, start with the extra compose file:

```bash
docker compose -f docker-compose.yml -f docker-compose.intel-gpu.yml up --build
```

This mounts:

```text
/dev/dri
```

Notes:

- Docker GPU passthrough is primarily intended for Linux hosts with Intel GPU access through `/dev/dri`.
- CPU-only Docker deployment should still work without the Intel GPU compose override.
- On Windows Docker Desktop, Intel GPU passthrough behavior depends on the host/container stack and may require additional setup outside this repository.

## Choosing a Model in ComfyUI

The same node supports both model variants. You choose which model to run by
changing the `model_dir` field.

Device recommendation:

- Use `GPU.0` by default. This is the recommended default because most users
  have Intel integrated graphics but may not have an Intel discrete GPU.
- If your system also has an Intel discrete GPU exposed by OpenVINO as
  `GPU.1`, you can switch `device`, `text_encoder_device`,
  `transformer_device`, and `vae_decoder_device` to `GPU.1`.
- If you do not have a discrete GPU, keep `GPU.0`.

For **ERNIE-Image Base INT8**:

```text
model_dir: C:\models\ERNIE-Image-ov-int8
```

For **ERNIE-Image Turbo INT4**:

```text
model_dir: C:\models\ERNIE-Image-Turbo-ov-int4
```

Recommended workflow in ComfyUI:

1. Add `OpenVINO ERNIE-Image Text to Image`.
2. Set `model_dir` to the local folder of the model you want to run.
3. Use the matching parameter profile for Base or Turbo.
4. Run the workflow.

Recommended profiles:

- **Base INT8**: `steps=20`, `guidance_scale=4.0`, `use_pe=false`
- **Turbo INT4**: `steps=8`, `guidance_scale=1.0`, `use_pe=true`

If you want to compare them side by side, duplicate the node and point each
node to a different `model_dir`.

Inside Docker, example `model_dir` values are:

```text
/models/ERNIE-Image-ov-int8
/models/ERNIE-Image-Turbo-ov-int4
```

## Recommended Settings

Turbo INT4:

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

Base INT8:

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

For strict composition, keep `load_pe=true` and set `use_pe=false`.

If you import the example workflows in this repo, the main thing you need to
change is the `model_dir` field:

- [workflows/ernie_image_base_int8_comfyui.json](workflows/ernie_image_base_int8_comfyui.json)
- [workflows/ernie_image_turbo_int4_comfyui.json](workflows/ernie_image_turbo_int4_comfyui.json)

The workflow defaults use `GPU.0`. If your machine has an Intel discrete GPU,
you can manually change those fields to `GPU.1`.

## Check Your Environment

Before opening ComfyUI, run:

```powershell
python .\scripts\check_env.py --model-dir C:\models\ERNIE-Image-Turbo-ov-int4
```

It checks:

- Python package availability
- OpenVINO available devices
- whether `GPU` is visible
- expected ERNIE-Image model layout
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

Base INT8 verification:

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

## Example Workflows

- [workflows/ernie_image_turbo_int4_comfyui.json](workflows/ernie_image_turbo_int4_comfyui.json): import into ComfyUI
- [workflows/ernie_image_turbo_int4_api.json](workflows/ernie_image_turbo_int4_api.json): minimal API payload
- [workflows/ernie_image_base_int8_comfyui.json](workflows/ernie_image_base_int8_comfyui.json): Base INT8 workflow
- [workflows/ernie_image_base_int8_api.json](workflows/ernie_image_base_int8_api.json): Base INT8 API payload

After loading a workflow, update `model_dir` to your local model path.

## Model Layout

This node supports the standard Optimum OpenVINO layout:

```text
ERNIE-Image-ov-int8/ or ERNIE-Image-Turbo-ov-int4/
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
