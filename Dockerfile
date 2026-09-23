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

# Official uv static binary (no pip bootstrap needed).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies first, from the lockfile only, so that source-code
# changes below don't invalidate (and re-download) this expensive layer.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Now bring in the project itself (README.md is required: pyproject.toml
# declares it as `readme`) and install it into the same environment.
COPY README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Mount points for model snapshots and generated audio (see README §4).
# Bind-mount host directories here at `docker run` time; models are large
# (multi-GB) and are intentionally not baked into the image.
RUN mkdir -p models outputs

ENV PATH="/app/.venv/bin:${PATH}" \
    PLAYGROUND_HOST=0.0.0.0 \
    PLAYGROUND_PORT=7860 \
    QWEN_TTS_MODEL_PATH=/app/models/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
    QWEN_TTS_VOICE_CLONE_MODEL_PATH=/app/models/Qwen3-TTS-12Hz-0.6B-Base \
    QWEN_TTS_CUSTOM_VOICE_MODEL_PATH=/app/models/Qwen3-TTS-12Hz-0.6B-CustomVoice \
    OUTPUT_DIR=/app/outputs

EXPOSE 7860

CMD ["python", "-m", "qwen_tts_playground.playground"]
