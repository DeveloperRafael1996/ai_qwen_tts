"""Runtime detection: GPU, dtype and FlashAttention availability."""

from __future__ import annotations

import logging
import platform
import subprocess
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from importlib.util import find_spec
from typing import Literal

import torch

logger = logging.getLogger(__name__)

AttentionPreference = Literal["auto", "flash", "default"]
FLASH_IMPL = "flash_attention_2"
DEFAULT_ATTENTION_LABEL = "PyTorch SDPA/Eager"


@dataclass(frozen=True)
class FlashAttentionStatus:
    installed: bool
    usable: bool
    version: str | None = None
    reason: str = ""


@dataclass(frozen=True)
class AttentionChoice:
    """`implementation` is the value for `attn_implementation` (None = library default)."""

    implementation: str | None
    flash: FlashAttentionStatus
    reason: str = ""

    @property
    def label(self) -> str:
        return "FlashAttention 2" if self.implementation == FLASH_IMPL else DEFAULT_ATTENTION_LABEL


def _pkg_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def select_dtype(use_cuda: bool) -> torch.dtype:
    """bfloat16 if the GPU supports it, else float16; float32 on CPU."""
    if not use_cuda:
        return torch.float32
    return torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16


def check_flash_attention(use_cuda: bool, dtype: torch.dtype) -> FlashAttentionStatus:
    """Report whether flash-attn is installed AND actually runs on this GPU.

    Installed is not enough: a wheel built for another torch/CUDA ABI imports
    fine or fails at import, so a tiny real kernel call is the honest test.
    """
    if find_spec("flash_attn") is None:
        return FlashAttentionStatus(False, False, None, "flash-attn package not installed")
    pkg_version = _pkg_version("flash-attn")
    if not use_cuda:
        return FlashAttentionStatus(True, False, pkg_version, "no CUDA device")
    if dtype not in (torch.float16, torch.bfloat16):
        return FlashAttentionStatus(True, False, pkg_version, f"unsupported dtype {dtype}")
    major, minor = torch.cuda.get_device_capability()
    if major < 8:
        return FlashAttentionStatus(
            True, False, pkg_version, f"compute capability {major}.{minor} < 8.0"
        )
    try:
        from flash_attn import flash_attn_func

        q = torch.zeros(1, 8, 2, 64, device="cuda", dtype=dtype)
        flash_attn_func(q, q, q)
        torch.cuda.synchronize()
    except Exception as exc:
        return FlashAttentionStatus(True, False, pkg_version, f"kernel check failed: {exc}")
    return FlashAttentionStatus(True, True, pkg_version)


def resolve_attention(
    preference: AttentionPreference, use_cuda: bool, dtype: torch.dtype
) -> AttentionChoice:
    """Pick the attention implementation, falling back to PyTorch's default."""
    status = check_flash_attention(use_cuda, dtype)
    if preference == "default":
        return AttentionChoice(None, status, "forced by configuration")
    if status.usable:
        return AttentionChoice(FLASH_IMPL, status)
    if preference == "flash":
        logger.warning("FlashAttention requested but unavailable: %s", status.reason)
    return AttentionChoice(None, status, status.reason)


def gpu_name() -> str:
    if not torch.cuda.is_available():
        return "CPU"
    return torch.cuda.get_device_name(torch.cuda.current_device())


def vram_total_gib() -> float | None:
    if not torch.cuda.is_available():
        return None
    return torch.cuda.mem_get_info()[1] / 1024**3


def describe_runtime(
    model_name: str, device: str, dtype: torch.dtype, attention: AttentionChoice
) -> str:
    vram = vram_total_gib()
    lines = [
        "Qwen3-TTS Runtime",
        "-----------------",
        f"GPU: {gpu_name()}",
        f"VRAM: {vram:.0f} GB" if vram is not None else "VRAM: N/A",
        f"dtype: {str(dtype).removeprefix('torch.')}",
        f"Attention: {attention.label}",
    ]
    if attention.implementation != FLASH_IMPL:
        lines += [
            "FlashAttention: unavailable",
            f"Reason: {attention.reason or 'unknown'}",
        ]
    lines += [f"Device: {device}", f"Model: {model_name}"]
    return "\n".join(lines)


def _nvidia_driver_version() -> str:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        return out.stdout.strip().splitlines()[0]
    except (OSError, subprocess.SubprocessError, IndexError):
        return "unknown"


def diagnose_environment() -> str:
    """Multi-line environment report (GPU, driver, CUDA, versions, FlashAttention)."""
    import transformers

    use_cuda = torch.cuda.is_available()
    dtype = select_dtype(use_cuda)
    flash = check_flash_attention(use_cuda, dtype)
    lines = []
    if use_cuda:
        free, total = torch.cuda.mem_get_info()
        major, minor = torch.cuda.get_device_capability()
        lines += [
            f"GPU: {torch.cuda.get_device_name()}",
            f"VRAM: {total / 1024**3:.1f} GB total, {free / 1024**3:.1f} GB free",
            f"Compute Capability: {major}.{minor}",
            f"Driver: {_nvidia_driver_version()}",
            f"CUDA Runtime (PyTorch): {torch.version.cuda}",
            f"BF16 supported: {str(torch.cuda.is_bf16_supported()).lower()}",
        ]
    else:
        lines.append("GPU: none (CPU mode)")
    lines += [
        f"PyTorch: {torch.__version__}",
        f"Python: {platform.python_version()}",
        f"transformers: {transformers.__version__}",
        f"FlashAttention installed: {str(flash.installed).lower()}"
        + (f" ({flash.version})" if flash.version else ""),
        f"FlashAttention usable: {str(flash.usable).lower()}"
        + (f" ({flash.reason})" if flash.reason else ""),
    ]
    return "\n".join(lines)
