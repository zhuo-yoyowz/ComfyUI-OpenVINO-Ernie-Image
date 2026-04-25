from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_comfyui_dir(explicit_dir: str | None = None) -> Path:
    env_dir = None if explicit_dir else os.environ.get("COMFYUI_DIR")
    requested_dir = explicit_dir or env_dir
    if requested_dir:
        comfyui_dir = Path(requested_dir).expanduser().resolve()
        if (comfyui_dir / "main.py").exists():
            return comfyui_dir
        raise FileNotFoundError(f"Could not find ComfyUI main.py in: {comfyui_dir}")

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "main.py").exists() and (parent / "custom_nodes").exists():
            return parent
        nested = parent / "ComfyUI"
        if (nested / "main.py").exists():
            return nested
    raise FileNotFoundError(
        "Could not locate ComfyUI. Pass --comfyui-dir explicitly or set COMFYUI_DIR. "
        "Example: python .\\scripts\\start_comfyui_openvino.py --comfyui-dir C:\\path\\to\\ComfyUI --port 8188"
    )


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Start ComfyUI for OpenVINO custom nodes on Intel AI PCs. "
            "This always passes --cpu to ComfyUI so PyTorch does not try to initialize CUDA."
        )
    )
    parser.add_argument("--comfyui-dir", default=None, help="Path to the ComfyUI directory.")
    parser.add_argument("--listen", default="127.0.0.1", help="ComfyUI listen address.")
    parser.add_argument("--port", default="8188", help="ComfyUI port.")
    parser.add_argument("--auto-launch", action="store_true", help="Let ComfyUI open the browser automatically.")
    parser.add_argument(
        "comfyui_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments passed to ComfyUI. Prefix them with --, for example: -- --verbose",
    )
    return parser


def main() -> int:
    args = build_argparser().parse_args()
    comfyui_dir = find_comfyui_dir(args.comfyui_dir)
    main_py = comfyui_dir / "main.py"

    if not main_py.exists():
        raise FileNotFoundError(f"Could not find ComfyUI main.py at: {main_py}")

    command = [
        sys.executable,
        "main.py",
        "--listen",
        str(args.listen),
        "--port",
        str(args.port),
        "--cpu",
    ]
    if not args.auto_launch:
        command.append("--disable-auto-launch")

    extra_args = list(args.comfyui_args)
    if extra_args[:1] == ["--"]:
        extra_args = extra_args[1:]
    command.extend(extra_args)

    print("Starting ComfyUI for Intel AI PC / OpenVINO:")
    print(" ".join(command))
    print()
    print("OpenVINO device selection is still controlled inside the ERNIE-Image node, for example device=GPU.")
    return subprocess.call(command, cwd=comfyui_dir)


if __name__ == "__main__":
    raise SystemExit(main())
