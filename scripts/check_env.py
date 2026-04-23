from __future__ import annotations

import argparse
import importlib.metadata
import sys
from pathlib import Path


REQUIRED_MODEL_ITEMS = [
    "model_index.json",
    "scheduler",
    "text_encoder",
    "tokenizer",
    "transformer",
    "vae_decoder",
]

PACKAGES = [
    "openvino",
    "openvino-tokenizers",
    "optimum",
    "optimum-intel",
    "diffusers",
    "transformers",
    "torch",
]


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def mark(ok: bool) -> str:
    return "OK" if ok else "MISSING"


def check_packages() -> bool:
    print("Packages")
    all_ok = True
    for package in PACKAGES:
        version = package_version(package)
        ok = version is not None
        all_ok = all_ok and ok
        print(f"  [{mark(ok)}] {package}: {version or '-'}")
    print()
    return all_ok


def check_openvino() -> bool:
    print("OpenVINO devices")
    try:
        import openvino as ov

        devices = ov.Core().available_devices
        print(f"  available_devices: {devices}")
        has_gpu = "GPU" in devices
        print(f"  [{mark(has_gpu)}] Intel GPU visible to OpenVINO")
        print()
        return has_gpu
    except Exception as exc:
        print(f"  [MISSING] Could not initialize OpenVINO: {exc}")
        print()
        return False


def check_model(model_dir: str | None) -> bool:
    print("Model layout")
    if not model_dir:
        print("  [MISSING] Pass --model-dir or set the node model_dir field in ComfyUI.")
        print()
        return False

    model_path = Path(model_dir).expanduser().resolve()
    print(f"  path: {model_path}")
    ok = True
    for item in REQUIRED_MODEL_ITEMS:
        exists = (model_path / item).exists()
        ok = ok and exists
        print(f"  [{mark(exists)}] {item}")

    pe_exists = (model_path / "pe" / "openvino_model.xml").exists()
    pe_tokenizer_exists = (model_path / "pe_tokenizer").is_dir()
    print(f"  [{'OK' if pe_exists else 'OPTIONAL'}] pe/openvino_model.xml")
    print(f"  [{'OK' if pe_tokenizer_exists else 'OPTIONAL'}] pe_tokenizer")
    if pe_exists and not pe_tokenizer_exists:
        print("  [INFO] PE model exists without pe_tokenizer; the ComfyUI node will run with PE disabled by default.")
    print()
    return ok


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check the local environment for ComfyUI OpenVINO ERNIE-Image.")
    parser.add_argument("--model-dir", help="Path to the Optimum-exported ERNIE-Image OpenVINO model.")
    return parser


def main() -> int:
    args = build_argparser().parse_args()
    print("ComfyUI OpenVINO ERNIE-Image environment check")
    print(f"Python: {sys.version.split()[0]}")
    print()

    packages_ok = check_packages()
    openvino_gpu_ok = check_openvino()
    model_ok = check_model(args.model_dir)

    if packages_ok and model_ok:
        if openvino_gpu_ok:
            print("Result: ready for OpenVINO GPU validation.")
        else:
            print("Result: packages and model look usable, but OpenVINO GPU is not visible.")
        return 0

    print("Result: environment needs attention before validation.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
