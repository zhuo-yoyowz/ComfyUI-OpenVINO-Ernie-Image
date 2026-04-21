# Troubleshooting

## Torch not compiled with CUDA enabled

Symptom:

```text
AssertionError: Torch not compiled with CUDA enabled
```

Start ComfyUI with `--cpu`:

```powershell
python main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch --cpu
```

This flag only affects ComfyUI's PyTorch device detection. ERNIE-Image still
runs through OpenVINO, and the node's `device=GPU` still targets the Intel GPU.

You can also use:

```powershell
python .\scripts\start_comfyui_openvino.py --port 8188
```

## Expected model_index.json in model_dir

The node supports only Optimum-exported OpenVINO model directories.

Check that `model_dir` points to the directory containing:

```text
model_index.json
transformer/
text_encoder/
vae_decoder/
scheduler/
tokenizer/
```

Do not point `model_dir` at the parent folder unless the parent itself contains
`model_index.json`.

## Prompt Enhancer changes my composition

Prompt Enhancer can rewrite prompts creatively. For exact object placement,
use:

```text
load_pe: true
use_pe: false
```

That keeps the PE model available but sends the original prompt directly to the
diffusion pipeline.

## comfy-aimdo failed to load

You may see:

```text
comfy-aimdo failed to load
NOTE: comfy-aimdo is currently only support for Nvidia GPUs
```

This warning is unrelated to this OpenVINO node. Use the `--cpu` launch mode to
avoid CUDA initialization issues in ComfyUI.

## GPU is not listed

Check OpenVINO device discovery:

```powershell
python -c "import openvino as ov; print(ov.Core().available_devices)"
```

If `GPU` is missing, install or update the Intel GPU driver and OpenVINO runtime.

## The first run is slow

The first run compiles OpenVINO models. Subsequent generations in the same
ComfyUI session reuse the cached pipeline.
