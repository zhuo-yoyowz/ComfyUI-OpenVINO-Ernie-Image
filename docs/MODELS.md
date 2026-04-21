# Model Layout

This custom node supports ERNIE-Image Turbo models exported with Optimum Intel
to the standard OpenVINO Diffusers layout.

## Expected Directory

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
  vae_bn_stats.npz
  pe/            # optional
  pe_tokenizer/  # optional
```

The node checks for `model_index.json` and then loads the model with:

```python
from optimum.intel import OVErnieImagePipeline

pipe = OVErnieImagePipeline.from_pretrained(
    model_dir,
    export=False,
    local_files_only=True,
    device="GPU",
    load_pe=True,
)
```

## Recommended Download

The easiest path is to download the pre-converted Turbo INT4 OpenVINO model from
ModelScope:

```text
https://www.modelscope.cn/models/snake7gun/ERNIE-Image-Turbo-ov-int4
```

Put the downloaded directory somewhere local, for example:

```text
C:\models\ERNIE-Image-Turbo-ov-int4
```

Optional ModelScope CLI download:

```powershell
python -m pip install modelscope
modelscope download --model snake7gun/ERNIE-Image-Turbo-ov-int4 --local_dir C:\models\ERNIE-Image-Turbo-ov-int4
```

Then use that directory as the ComfyUI node's `model_dir`.

## Export Command

When ERNIE-Image Turbo support is available in your Optimum Intel build, the
intended export flow is:

```powershell
optimum-cli export openvino `
  --model baidu/ERNIE-Image-Turbo `
  --task text-to-image `
  --weight-format int4 `
  --ratio 0.8 `
  C:\models\ERNIE-Image-Turbo-ov-int4
```

If you already have an exported model directory, no export is needed. Point the
ComfyUI node's `model_dir` directly at that directory.

## Unsupported Legacy Layout

This repository does not support older hand-exported ERNIE-Image folders such
as:

```text
ov_ernie_image_int8_dynamic/
  scheduler/
  text_encoder/
  tokenizer/
  transformer/
  vae_decoder/
  ov_ernie_image_config.json
```

Those exports use different component interfaces and would require a separate
inference implementation. Keeping only the Optimum layout makes the ComfyUI
node smaller, easier to maintain, and easier to reason about.

## Prompt Enhancer

If your export includes:

```text
pe/
pe_tokenizer/
```

the node can load the OpenVINO Prompt Enhancer when `load_pe=true`.

Use `use_pe=false` when you want strict control over the original prompt. This
is useful for product-like prompts, exact centering, and composition tests.
