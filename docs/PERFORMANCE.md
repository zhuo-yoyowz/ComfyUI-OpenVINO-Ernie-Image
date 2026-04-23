# Performance Notes

This page is intentionally data-driven. If you test a device, please open a PR
with the table filled in.

## Suggested Benchmark Settings

Use a stable prompt and fixed seed:

```text
prompt: a centered whole red apple on a wooden table, studio lighting, sharp focus, high quality
width: 512
height: 512
steps: 8
guidance_scale: 1.0
seed: 42
load_pe: true
use_pe: false
```

For Base INT8 comparisons, use:

```text
width: 512
height: 512
steps: 20
guidance_scale: 4.0
load_pe: true
use_pe: false
```

Use the API verifier:

```powershell
python .\scripts\verify_comfyui_api.py `
  --comfyui-dir C:\path\to\ComfyUI `
  --model-dir C:\models\ERNIE-Image-Turbo-ov-int4 `
  --device GPU `
  --width 512 `
  --height 512 `
  --steps 8 `
  --guidance-scale 1.0 `
  --no-use-pe `
  --timeout 1800
```

For Base INT8, add `--model-profile base` and point `--model-dir` to the Base
INT8 export:

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

## Results Template

| Hardware | OpenVINO device | Resolution | Steps | First run | Warm run | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Intel Core Ultra | GPU | 512x512 | 8 | TBD | TBD | Add driver and OpenVINO version |
| Intel Arc | GPU | 512x512 | 8 | TBD | TBD | Add driver and OpenVINO version |
| Intel Core Ultra | GPU | 512x512 | 20 | TBD | TBD | Base INT8 profile |

## Measurement Notes

- First run includes OpenVINO model compilation.
- Warm run should be measured in the same ComfyUI session.
- Prompt Enhancer can add latency when `use_pe=true`.
- Report OpenVINO, Optimum Intel, Diffusers, and ComfyUI versions.
