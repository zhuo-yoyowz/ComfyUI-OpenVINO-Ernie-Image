# Model Layout

This custom node supports ERNIE-Image Base INT8 and ERNIE-Image Turbo INT4
models exported with Optimum Intel to the standard OpenVINO Diffusers layout.

## Expected Directory

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
    load_pe=False,
)
```

The node loads the main pipeline first and then attaches the OpenVINO Prompt
Enhancer itself when `load_pe=true`. This keeps Base INT8 and Turbo INT4 on the
same tokenizer compatibility path.

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

For ERNIE-Image Base INT8, use an Optimum/OpenVINO exported directory such as:

```text
C:\models\ERNIE-Image-ov-int8
```

## Export Command

When ERNIE-Image support is available in your Optimum Intel build, the intended
Turbo INT4 export flow is:

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

A Base INT8 export uses the same directory layout, but with INT8 weights:

```powershell
optimum-cli export openvino `
  --model baidu/ERNIE-Image `
  --task text-to-image `
  --weight-format int8 `
  C:\models\ERNIE-Image-ov-int8
```

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

`pe_tokenizer` is a tokenizer asset directory. It normally contains files such
as `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, and
`chat_template.jinja`; it does not need OpenVINO tokenizer IR files for this
node.

Use `use_pe=false` when you want strict control over the original prompt. This
is useful for product-like prompts, exact centering, and composition tests.
