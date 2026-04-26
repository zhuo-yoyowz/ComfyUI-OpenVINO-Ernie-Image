#!/usr/bin/env bash
set -euo pipefail

cd /opt/ComfyUI

echo "Starting ComfyUI with OpenVINO ERNIE-Image custom node"
echo "ComfyUI directory: /opt/ComfyUI"
echo "Model directory hint: ${ERNIE_IMAGE_OV_MODEL_DIR:-<not set>}"
echo

if [[ -n "${ERNIE_IMAGE_OV_MODEL_DIR:-}" && ! -e "${ERNIE_IMAGE_OV_MODEL_DIR}" ]]; then
  echo "Warning: ERNIE_IMAGE_OV_MODEL_DIR does not exist inside the container:"
  echo "  ${ERNIE_IMAGE_OV_MODEL_DIR}"
  echo "Make sure your model volume is mounted correctly."
  echo
fi

extra_args=()
if [[ -n "${COMFYUI_ARGS:-}" ]]; then
  # shellcheck disable=SC2206
  extra_args=(${COMFYUI_ARGS})
fi

exec python main.py \
  --listen 0.0.0.0 \
  --port "${COMFYUI_PORT:-8188}" \
  --cpu \
  "${extra_args[@]}"
