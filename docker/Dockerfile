ARG BASE_IMAGE=mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
FROM ${BASE_IMAGE}

ARG COMFYUI_REPO=https://github.com/comfyanonymous/ComfyUI.git
ARG COMFYUI_REF=master

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    COMFYUI_DIR=/opt/ComfyUI

RUN rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    git \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN git clone --depth 1 --branch "${COMFYUI_REF}" "${COMFYUI_REPO}" "${COMFYUI_DIR}"

WORKDIR ${COMFYUI_DIR}

RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

COPY . ${COMFYUI_DIR}/custom_nodes/ComfyUI-OpenVINO-Ernie-Image

RUN python -m pip install -r ${COMFYUI_DIR}/custom_nodes/ComfyUI-OpenVINO-Ernie-Image/docker/requirements.docker.txt && \
    python -m pip install --no-deps git+https://github.com/openvino-dev-samples/optimum-intel.git@e70cae7d0cd91087c087418e96179bd4a8479004

RUN chmod +x ${COMFYUI_DIR}/custom_nodes/ComfyUI-OpenVINO-Ernie-Image/docker/entrypoint.sh

EXPOSE 8188

ENTRYPOINT ["/opt/ComfyUI/custom_nodes/ComfyUI-OpenVINO-Ernie-Image/docker/entrypoint.sh"]
