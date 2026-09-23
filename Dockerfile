# syntax=docker/dockerfile:1

# Qwen3-TTS Playground image.
#
# GPU inference relies on the NVIDIA driver + container runtime on the HOST
# (via `nvidia-container-toolkit`); this image does NOT need the CUDA
# Toolkit or nvcc, since PyTorch's pip wheel bundles the CUDA *runtime*
# libraries it needs (cuBLAS, cuDNN, NCCL, ...). Only the driver-side
# libcuda.so is injected from the host at `docker run` time.
FROM python:3.12-slim

# System packages:
#   - build-essential: torch/triton JIT-compile some GPU kernels at runtime
#     and need a working `cc`; without it, generation fails with
#     "Failed to find C compiler" the first time a kernel needs compiling.
#   - libsndfile1: required by `soundfile`/`librosa` to read/write audio.
#   - sox: silences a benign warning `qwen-tts` prints at import time if the
#     `sox` CLI is missing (never a hard requirement).
#   - ca-certificates: HTTPS access to the Hugging Face Hub when a model is
#     not present locally under /app/models.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libsndfile1 \
        sox \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Non-root user the app actually runs as (see USER below). Defaults to
# 1000:1000, the common single-user-Linux-desktop UID/GID, so files this
# process writes into bind-mounted volumes (outputs/, models/) come out
# owned by *you* on the host instead of root. If your host user has a
# different id, override at build time:
#   docker build --build-arg APP_UID=$(id -u) --build-arg APP_GID=$(id -g) .
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd -g "${APP_GID}" appuser \
    && useradd -m -u "${APP_UID}" -g "${APP_GID}" -s /bin/bash appuser

# Official uv static binary (no pip bootstrap needed).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies first, from the lockfile only, so that source-code
# changes below don't invalidate (and re-download) this expensive layer.
COPY pyproject.toml uv.lock ./
# The rm -rf below MUST be in this same RUN command (not a later layer):
# overlayfs layers are additive, so deleting files in a *later* layer only
# hides them with a whiteout marker — the bytes still ship inside this
# layer and the image doesn't shrink. Removed here: CUPTI static libs
# (Nsight/profiler-only, not needed to run Triton kernels) and torch's C++
# headers (only needed to build custom C++/CUDA extensions against
# libtorch, not to run pretrained models) — verified safe: a real Triton
# JIT kernel compile+run and torch.nn.functional.scaled_dot_product_
# attention both still work after removing these. Saves ~340MB.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev \
    && rm -rf \
        .venv/lib/python3.12/site-packages/triton/backends/nvidia/lib/cupti \
        .venv/lib/python3.12/site-packages/triton/backends/nvidia/lib/cupti-blackwell \
        .venv/lib/python3.12/site-packages/torch/include

# Now bring in the project itself (README.md is required: pyproject.toml
# declares it as `readme`) and install it into the same environment.
COPY README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Mount points for model snapshots and generated audio (see README §4).
# Bind-mount host directories here at `docker run` time; models are large
# (multi-GB) and are intentionally not baked into the image. chown so the
# non-root user below can write into them (and anything else under /app,
# e.g. __pycache__ for the src/ tree).
RUN mkdir -p models outputs && chown -R appuser:appuser /app

ENV PATH="/app/.venv/bin:${PATH}" \
    HOME=/home/appuser \
    PLAYGROUND_HOST=0.0.0.0 \
    PLAYGROUND_PORT=7860 \
    QWEN_TTS_MODEL_PATH=/app/models/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
    QWEN_TTS_VOICE_CLONE_MODEL_PATH=/app/models/Qwen3-TTS-12Hz-0.6B-Base \
    QWEN_TTS_CUSTOM_VOICE_MODEL_PATH=/app/models/Qwen3-TTS-12Hz-0.6B-CustomVoice \
    OUTPUT_DIR=/app/outputs

# Run as non-root: writes to bind-mounted outputs/models stay owned by the
# host user (see APP_UID/APP_GID above), and HF Hub cache / Triton's JIT
# kernel cache land under this user's $HOME instead of /root.
USER appuser

EXPOSE 7860

CMD ["python", "-m", "qwen_tts_playground.playground"]
