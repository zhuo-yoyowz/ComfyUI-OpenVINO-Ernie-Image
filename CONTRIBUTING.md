# Contributing

Thanks for helping improve the ComfyUI OpenVINO ERNIE-Image node.

## Good First Contributions

- Add verified Intel hardware results
- Improve the sample workflows
- Tighten installation docs for different ComfyUI setups
- Add Linux/macOS launch notes
- Report model export compatibility issues

## Development Checks

Run the lightweight syntax check:

```powershell
python -m py_compile nodes.py scripts\check_env.py scripts\verify_comfyui_api.py scripts\start_comfyui_openvino.py
```

Run an API smoke test against a local ComfyUI checkout:

```powershell
python .\scripts\verify_comfyui_api.py `
  --comfyui-dir C:\path\to\ComfyUI `
  --model-dir C:\models\ERNIE-Image-Turbo-ov-int4 `
  --device GPU `
  --width 256 `
  --height 256 `
  --steps 1 `
  --timeout 900
```

Run the environment checker:

```powershell
python .\scripts\check_env.py --model-dir C:\models\ERNIE-Image-Turbo-ov-int4
```

## Pull Requests

Please keep changes focused. If a PR changes runtime behavior, include:

- The model directory layout used for testing
- OpenVINO, Optimum Intel, Diffusers, and ComfyUI versions
- Device used: `CPU`, `GPU`, or `AUTO`
- A short note about visual quality or failure mode
