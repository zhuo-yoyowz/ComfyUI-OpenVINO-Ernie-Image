from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import torch


def _find_parent_path(name: str, required_child: str | None = None) -> Path | None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / name
        if not candidate.exists():
            continue
        if required_child is None or (candidate / required_child).exists():
            return candidate
    return None


def _default_model_dir() -> Path | None:
    env_keys = [
        "ERNIE_IMAGE_OV_MODEL_DIR",
        "ERNIE_IMAGE_BASE_OV_DIR",
        "ERNIE_IMAGE_TURBO_OV_DIR",
    ]
    for key in env_keys:
        env_value = os.environ.get(key, "").strip()
        if not env_value:
            continue
        candidate = Path(env_value).expanduser()
        if (candidate / "model_index.json").exists():
            return candidate

    current = Path(__file__).resolve()
    candidates = []
    for parent in current.parents:
        candidates.extend(
            [
                parent / "ERNIE-Image-ov-int8",
                parent / "ernie_image_int8",
                parent / "ernie_image_int8_fixed3",
                parent / "Base" / "INT8",
                parent / "models" / "ERNIE-Image-ov-int8",
                parent / "models" / "ernie_image_int8",
                parent / "ERNIE-Image-Turbo-ov-int4",
                parent / "models" / "ERNIE-Image-Turbo-ov-int4",
                parent / "Turbo" / "INT4",
            ]
        )
    for candidate in candidates:
        if (candidate / "model_index.json").exists():
            return candidate
    return None


DEFAULT_MODEL_DIR = _default_model_dir()


_PIPELINE_CACHE = {}


def _available_device_choices() -> list[str]:
    choices = ["GPU", "GPU.0", "GPU.1", "CPU", "AUTO"]
    try:
        import openvino as ov

        detected = list(ov.Core().available_devices)
    except Exception:
        detected = []

    ordered = []
    for device in detected + choices:
        if device not in ordered:
            ordered.append(device)
    return ordered


def _normalize_optional_device(value: str) -> str | None:
    value = value.strip()
    return value or None


def _load_pe_tokenizer(pe_tokenizer_path: Path):
    import json

    from transformers import PreTrainedTokenizerFast

    tok_config_path = pe_tokenizer_path / "tokenizer_config.json"
    tokenizer_path = pe_tokenizer_path / "tokenizer.json"
    if tok_config_path.exists():
        tok_config = json.loads(tok_config_path.read_text(encoding="utf-8"))
        if isinstance(tok_config.get("extra_special_tokens"), list):
            tok_config["extra_special_tokens"] = {tok: tok for tok in tok_config["extra_special_tokens"]}
            chat_template_path = pe_tokenizer_path / "chat_template.jinja"
            if chat_template_path.exists():
                tok_config["chat_template"] = chat_template_path.read_text(encoding="utf-8")
            return PreTrainedTokenizerFast(tokenizer_file=str(tokenizer_path), **tok_config)
    return PreTrainedTokenizerFast.from_pretrained(str(pe_tokenizer_path))


class _NoTokenTypeIdsTokenizer:
    def __init__(self, tokenizer, model_max_length: int | None = None):
        self._tokenizer = tokenizer
        self.model_max_length = int(model_max_length) if model_max_length and int(model_max_length) > 0 else tokenizer.model_max_length

    def __call__(self, *args, **kwargs):
        encoded = self._tokenizer(*args, **kwargs)
        encoded.pop("token_type_ids", None)
        return encoded

    def __getattr__(self, name):
        return getattr(self._tokenizer, name)


def _attach_optimum_pe_if_available(pipeline, model_path: Path, device: str, load_pe: bool, pe_max_new_tokens: int):
    if not load_pe or getattr(pipeline, "pe", None) is not None:
        return pipeline

    pe_path = model_path / "pe"
    pe_tokenizer_path = model_path / "pe_tokenizer"
    if pe_path.is_dir() and (pe_path / "openvino_model.xml").exists():
        from optimum.intel.openvino.modeling_decoder import OVModelForCausalLM

        pipeline.pe = OVModelForCausalLM.from_pretrained(
            str(pe_path),
            device=device,
            compile=True,
            local_files_only=True,
        )
    if pe_tokenizer_path.is_dir():
        pipeline.pe_tokenizer = _NoTokenTypeIdsTokenizer(_load_pe_tokenizer(pe_tokenizer_path), pe_max_new_tokens)
    return pipeline


def _has_complete_openvino_pe(model_path: Path) -> bool:
    return (model_path / "pe" / "openvino_model.xml").exists() and (model_path / "pe_tokenizer").is_dir()


def _load_pipeline(
    model_dir: str,
    device: str,
    text_encoder_device: str,
    transformer_device: str,
    vae_decoder_device: str,
    load_pe: bool,
    pe_max_new_tokens: int,
):
    model_path = Path(model_dir).expanduser().resolve()
    if not (model_path / "model_index.json").exists():
        raise ValueError(
            "Only Optimum-exported ERNIE-Image model directories are supported. "
            "Expected model_index.json in model_dir."
        )

    cache_key = (
        str(model_path),
        device,
        text_encoder_device,
        transformer_device,
        vae_decoder_device,
        load_pe,
        pe_max_new_tokens,
    )

    pipeline = _PIPELINE_CACHE.get(cache_key)
    if pipeline is not None:
        return pipeline

    optimum_intel_path = _find_parent_path("optimum-intel", "optimum")
    if optimum_intel_path is not None and str(optimum_intel_path) not in sys.path:
        sys.path.insert(0, str(optimum_intel_path))

    from optimum.intel import OVErnieImagePipeline

    kwargs = {
        "device": device,
        "export": False,
        "local_files_only": True,
        # Load PE explicitly below so Base INT8 and Turbo INT4 share the same
        # tokenizer compatibility path.
        "load_pe": False,
    }
    text_device = _normalize_optional_device(text_encoder_device)
    transformer_device_value = _normalize_optional_device(transformer_device)
    vae_device = _normalize_optional_device(vae_decoder_device)
    if text_device:
        kwargs["text_encoder_device"] = text_device
    if transformer_device_value:
        kwargs["transformer_device"] = transformer_device_value
    if vae_device:
        kwargs["vae_decoder_device"] = vae_device

    pipeline = OVErnieImagePipeline.from_pretrained(model_path, **kwargs)
    pipeline = _attach_optimum_pe_if_available(
        pipeline,
        model_path,
        device,
        load_pe and _has_complete_openvino_pe(model_path),
        int(pe_max_new_tokens),
    )
    _PIPELINE_CACHE[cache_key] = pipeline
    return pipeline


def _pil_to_comfy_image(image):
    array = np.asarray(image.convert("RGB")).astype(np.float32) / 255.0
    return torch.from_numpy(array).unsqueeze(0)


class OVErnieImageTextToImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_dir": (
                    "STRING",
                    {
                        "default": str(DEFAULT_MODEL_DIR or ""),
                        "multiline": False,
                    },
                ),
                "prompt": (
                    "STRING",
                    {
                        "default": "a centered whole red apple on a wooden table, studio lighting, sharp focus, high quality",
                        "multiline": True,
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
                "device": (_available_device_choices(), {"default": "GPU.0"}),
                "load_pe": ("BOOLEAN", {"default": True}),
                "use_pe": ("BOOLEAN", {"default": True}),
                "pe_max_new_tokens": ("INT", {"default": 256, "min": 32, "max": 2048, "step": 32}),
                "text_encoder_device": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
                "transformer_device": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
                "vae_decoder_device": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                    },
                ),
                "width": ("INT", {"default": 512, "min": 128, "max": 2048, "step": 16}),
                "height": ("INT", {"default": 512, "min": 128, "max": 2048, "step": 16}),
                "steps": ("INT", {"default": 8, "min": 1, "max": 100, "step": 1}),
                "guidance_scale": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 20.0,
                        "step": 0.1,
                    },
                ),
                "seed": ("INT", {"default": 42, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "revised_prompt")
    FUNCTION = "generate"
    CATEGORY = "OpenVINO/ERNIE-Image"

    def generate(
        self,
        model_dir,
        prompt,
        negative_prompt,
        device,
        load_pe,
        use_pe,
        pe_max_new_tokens,
        text_encoder_device,
        transformer_device,
        vae_decoder_device,
        width,
        height,
        steps,
        guidance_scale,
        seed,
    ):
        pipeline = _load_pipeline(
            model_dir=model_dir,
            device=device,
            text_encoder_device=text_encoder_device,
            transformer_device=transformer_device,
            vae_decoder_device=vae_decoder_device,
            load_pe=bool(load_pe),
            pe_max_new_tokens=int(pe_max_new_tokens),
        )
        generator = torch.Generator(device="cpu").manual_seed(int(seed))
        can_use_pe = (
            bool(use_pe)
            and getattr(pipeline, "pe", None) is not None
            and getattr(pipeline, "pe_tokenizer", None) is not None
        )
        result = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            height=int(height),
            width=int(width),
            num_inference_steps=int(steps),
            guidance_scale=float(guidance_scale),
            generator=generator,
            use_pe=can_use_pe,
        )
        revised_prompt = ""
        if getattr(result, "revised_prompts", None):
            revised_prompt = result.revised_prompts[0] or ""
        return (_pil_to_comfy_image(result.images[0]), revised_prompt)


NODE_CLASS_MAPPINGS = {
    "OVErnieImageTextToImage": OVErnieImageTextToImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OVErnieImageTextToImage": "OpenVINO ERNIE-Image Text to Image",
}
