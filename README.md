# Qwen3-TTS VoiceDesign Playground

A local, professional web playground to experiment with **text-to-speech**
in Spanish, Portuguese and English, with three tabs backed by three different
Qwen3-TTS models:

- **Voice Design** — [`Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign):
  configurable accent, gender, age, personality, emotion, speed, style and
  free-text instructions, evaluated against a banking-assistant use case.
- **Voice Clone** — [`Qwen/Qwen3-TTS-12Hz-0.6B-Base`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base):
  clone a voice from a short reference audio clip (+ optional reference
  text) instead of describing it with words.
- **Custom Voice** — [`Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice):
  generate speech with one of 9 predefined premium speakers.

```text
Voice Design tab:
Language → Accent → Gender → Age → Personality → Emotion → Speed
    → VoiceDesign Prompt → Text → Generate → Qwen3-TTS-1.7B-VoiceDesign → Audio Player

Voice Clone tab:
Language → Reference Audio (+ Reference Text) → Text → Generate
    → Qwen3-TTS-0.6B-Base → Audio Player

Custom Voice tab:
Language → Speaker → Text → Generate → Qwen3-TTS-0.6B-CustomVoice → Audio Player
```

---

## 1. Requirements

- **Python 3.12**
- **[`uv`](https://docs.astral.sh/uv/)** — all dependency management goes through `uv`. This
  project does **not** use pip, poetry, pipenv, or `requirements.txt`.
- A **Linux** machine (primary target). An **NVIDIA GPU with CUDA** is strongly
  recommended; the app also runs on CPU (slow) if no GPU is available.

## 2. Installing PyTorch for CUDA

`qwen-tts` depends on `torch`/`torchaudio`. `uv` resolves a CUDA-enabled
wheel from PyPI automatically on most Linux + NVIDIA setups. If you need a
specific CUDA build (e.g. to match your driver), pin an extra index instead
of using pip — add this to `pyproject.toml` and re-run `uv sync`:

```toml
[[tool.uv.index]]
name = "pytorch-cu121"
url = "https://download.pytorch.org/whl/cu121"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu121" }
torchaudio = { index = "pytorch-cu121" }
```

Adjust `cu121` to match your CUDA runtime (e.g. `cu124`, `cu128`). This keeps
dependency management entirely inside `uv` — no `pip install` calls.

## 3. Project setup

```bash
uv sync
```

This creates `.venv/`, resolves `uv.lock`, and installs every dependency
declared in `pyproject.toml` (`qwen-tts`, `gradio`, `soundfile`, `pydantic`,
`pydantic-settings`, `huggingface-hub`, plus dev tools `pytest`,
`pytest-mock`, `ruff`).

## 4. Getting the models

This app uses three separate Qwen3-TTS checkpoints, one per tab.

### Option A — download them locally (recommended for repeated use)

```bash
uv run hf download \
  Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
  --local-dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign

uv run hf download \
  Qwen/Qwen3-TTS-12Hz-0.6B-Base \
  --local-dir ./models/Qwen3-TTS-12Hz-0.6B-Base

uv run hf download \
  Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice \
  --local-dir ./models/Qwen3-TTS-12Hz-0.6B-CustomVoice
```

Then point the app at them via `.env`:

```env
QWEN_TTS_MODEL_PATH=./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
QWEN_TTS_VOICE_CLONE_MODEL_PATH=./models/Qwen3-TTS-12Hz-0.6B-Base
QWEN_TTS_CUSTOM_VOICE_MODEL_PATH=./models/Qwen3-TTS-12Hz-0.6B-CustomVoice
```

### Option B — stream from the Hugging Face Hub

If a path does not exist (or is empty), the app falls back to the matching
Hub repo id (`Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`,
`Qwen/Qwen3-TTS-12Hz-0.6B-Base`, or `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`)
directly, letting `from_pretrained` download and cache it under
`~/.cache/huggingface`.

### Loading behavior

All three models are currently loaded **lazily**: nothing is loaded at
process startup, and each model loads (once) on the first "Generate..."
click in its tab, then stays cached in memory for the rest of the session
(never reloaded per-request).

This is deliberate: many GPUs (e.g. a 4-6GB laptop GPU) cannot even fit the
1.7B VoiceDesign model on its own, let alone all three models at once, so
eager loading at startup would crash the whole app before it serves a
single page. See §12 for VRAM numbers observed in practice (in short: the
two 0.6B models fit comfortably on a 4GB GPU; the 1.7B one does not).

If your hardware can comfortably fit the VoiceDesign model, you can restore
eager loading (load-once-at-startup, fail-fast instead of failing on first
click) by uncommenting the `service.load()` call in `main()`
(`src/qwen_tts_playground/playground.py`).

## 5. Configuration

Copy `.env.example` to `.env` and adjust as needed:

```env
QWEN_TTS_MODEL_PATH=./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
QWEN_TTS_VOICE_CLONE_MODEL_PATH=./models/Qwen3-TTS-12Hz-0.6B-Base
QWEN_TTS_CUSTOM_VOICE_MODEL_PATH=./models/Qwen3-TTS-12Hz-0.6B-CustomVoice
PLAYGROUND_HOST=127.0.0.1
PLAYGROUND_PORT=7860
OUTPUT_DIR=outputs
```

## 6. Running the playground

```bash
uv sync
uv run python -m qwen_tts_playground.playground
```

Open <http://127.0.0.1:7860>.

On startup the app logs:

```text
Model loaded | device=cuda:0 | dtype=torch.bfloat16 | model_path=... | GPU=...
```

## 7. Supported languages

`Spanish`, `Portuguese`, `English` — these exact strings are sent literally
to the model as `language=` in `generate_voice_design(...)`.

## 8. Language vs. accent

- **Language** (`language=`) is a hard parameter validated by the model
  itself (`model.get_supported_languages()`).
- **Accent** is *not* a model parameter. It is a *requested style*, expressed
  through the natural-language `instruct` text (VoiceDesign's whole point).
  Accent presets in this app (Peruvian, Mexican, Colombian, Argentinian,
  Spain, Brazilian, São Paulo, Rio de Janeiro, Portugal, American, British,
  Australian, Indian, Latin American English…) are **requests**, not
  guarantees. **Always evaluate the generated audio by ear** — VoiceDesign
  may approximate, blend, or miss a requested regional accent depending on
  the prompt and sampling.

## 9. Using VoiceDesign

1. Pick a **Language**.
2. Pick an **Accent** (style request).
3. Pick **Gender**, **Age**, **Personality** (one or more), **Emotion**,
   **Speaking Pace**.
4. The **Voice Design Instruction** textarea is rebuilt automatically from
   these controls (via `VoicePromptBuilder`). You can edit it manually —
   click **Reset Voice Prompt** to regenerate it from the selectors.
5. Optionally add **Additional Voice Instruction** free text.
6. Optionally load a ready-made **Voice Preset** (overrides the instruction).
7. Write or pick a **Banking Preset** for the **Text to synthesize**.
8. Click **Generate Audio**.

## 10. Voice Clone tab

Unlike Voice Design, cloning does not use `instruct` text — it uses a
reference recording of a real voice:

1. Pick a **Language**.
2. Upload or record a **Reference Audio** clip (3+ seconds recommended).
3. Choose a **Cloning Mode**:
   - **In-Context Learning** (default): the model continues from the
     reference speech + reference text, which must match what is actually
     said in the clip. Generally higher quality.
   - **Speaker Embedding Only (x-vector)**: only the speaker's voice
     characteristics are extracted; no reference text is needed, but
     quality/naturalness is usually a bit lower.
4. Write the **Text to synthesize** and click **Generate Cloned Audio**.

This tab's model (`Qwen3-TTS-12Hz-0.6B-Base`) loads on the first click, not
at startup — see §4.

## 11. Custom Voice tab

Pick one of 9 predefined premium speakers and generate speech directly, no
accent/age/personality/emotion/speed axes needed — the speaker's voice
already carries its own character:

1. Pick a **Language**. Every speaker works with any of the three
   supported languages, but each one has a **native language** (shown next
   to its name) where quality is typically best.
2. Pick a **Speaker**: `Vivian`, `Serena`, `Uncle_Fu`, `Dylan`, `Eric`,
   `Ryan`, `Aiden`, `Ono_Anna`, `Sohee` — descriptions are shown in the tab.
3. Write the **Text to synthesize** and click **Generate Audio**.

An optional **Style Instruction** field is also shown (e.g. "Speak in a
very happy tone") — this maps to the model's `instruct` parameter, which
the underlying architecture supports. However, **the currently installed
`qwen-tts` package (0.1.1) silently forces `instruct=None` for the 0.6B
CustomVoice checkpoint** regardless of what you type, even though that
model's own card shows an instruct example. This app forwards whatever you
type anyway (in case a future `qwen-tts` release changes this), but don't
expect it to have any audible effect right now — verified against the
installed package's source (`qwen3_tts_model.py`):
`if self.model.tts_model_size in "0b6": instruct = None`.

This tab's model (`Qwen3-TTS-12Hz-0.6B-CustomVoice`) loads on the first
click, not at startup — see §4.

## 12. GPU usage & performance metrics

- Each model loads once as `cuda:0` + `torch.bfloat16` when a CUDA GPU is
  available (`float32` on CPU).
- `attn_implementation="flash_attention_2"` is used automatically **only**
  if the `flash-attn` package is importable; otherwise the default
  (SDPA/eager) attention implementation is used, and you'll see:
  `Warning: flash-attn is not installed. Will only run the manual PyTorch
  version.` FlashAttention is never a hard requirement — this warning is
  safe to ignore.

  Note: `flash-attn` does not publish prebuilt wheels to PyPI, only to its
  GitHub releases, and its newest prebuilt wheels lag behind the newest
  PyTorch/CUDA releases (e.g. as of writing, the latest wheels target up to
  `torch2.9+cu13`/`torch2.8+cu12`). If `uv sync` resolves a newer `torch`
  than that (common, since `qwen-tts` doesn't pin a `torch` version), there
  is no matching prebuilt wheel, and installing `flash-attn` would either
  fail an ABI check against a mismatched wheel or require building from
  source with the full CUDA Toolkit (`nvcc`, not just the driver) — a slow
  build with a limited payoff here, since flash-attn mainly saves memory on
  long attention sequences, and TTS prompts here are short; the real VRAM
  pressure comes from model weight size, which flash-attn doesn't change.
  If you want it anyway, either pin `torch`/`torchaudio` to a version with a
  matching prebuilt wheel (see §2 for pinning a specific CUDA index) or
  install the CUDA Toolkit and build from source.
- Every generation reports:
  - **Generation time** (`time.perf_counter()`)
  - **Audio duration** (`len(wav) / sample_rate`)
  - **RTF** = `generation_time / audio_duration` (lower is better; `< 1.0`
    means faster than real time)
  - **Sample rate**, **GPU name**, **VRAM allocated/reserved**
    (`torch.cuda.memory_allocated()` / `memory_reserved()`)

Numbers observed on a 4GB laptop GPU (NVIDIA RTX 500 Ada, 3.65 GiB usable):
the 1.7B VoiceDesign model does **not** fit (`CudaOutOfMemoryError` while
loading), while both 0.6B models fit comfortably one at a time:

| Model | VRAM allocated | RTF observed |
| --- | --- | --- |
| 0.6B Base (Voice Clone, ICL mode) | ~2.06 GiB | ≈ 1.31 |
| 0.6B CustomVoice | ~2.02 GiB | ≈ 2.15 |
| 1.7B VoiceDesign | OOM at load | N/A (falls back to CPU) |

Your mileage will vary with driver/CUDA version and other processes holding
VRAM — see §14 for the VoiceDesign fallback.

## 13. Thread safety

GPU inference is serialized behind a lock in `QwenTTSService`. Concurrent
clicks in the UI queue instead of racing on the same model instance, which
avoids state corruption and reduces OOM risk from overlapping generations.
Each tab's model has its own `QwenTTSService` instance/lock, so generations
in different tabs could in principle run concurrently — but on a single GPU
with limited VRAM, running two or three tabs at once is likely to OOM;
prefer using one tab at a time on constrained hardware.

## 14. Troubleshooting CUDA OOM

All three models need VRAM (much more for the 1.7B VoiceDesign model than
for either 0.6B model) plus activation memory that scales with text
length. If you hit
`CudaOutOfMemoryError`, whether while loading a model or during generation:

- Shorten the input text or split it into shorter segments.
- Close other GPU-using processes (check with `nvidia-smi`).
- Lower `max_new_tokens` via **Advanced Settings** if exposed, or reduce
  `Top K`/`Top P` sampling breadth.
- Try one of the smaller 0.6B models (Voice Clone or Custom Voice) instead
  of VoiceDesign (1.7B) if your GPU can't fit the larger one — see the VRAM
  numbers in §12.
- If you are on a GPU with very limited VRAM (e.g. 4-6 GB laptop GPUs), fall
  back to CPU by unsetting CUDA (`CUDA_VISIBLE_DEVICES=""`) — generation will
  be much slower but still functional for evaluation purposes.
- The app calls `torch.cuda.empty_cache()` after an OOM (whether at load
  time or generation time) to help recovery for the next attempt without
  restarting the process.

## 15. Project structure

```text
qwen-tts-playground/
├── pyproject.toml
├── uv.lock
├── README.md
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── models/                      # local model snapshots (gitignored)
├── outputs/                     # generated WAV files (gitignored)
├── tests/
│   ├── test_profiles.py
│   ├── test_prompt_builder.py
│   └── test_tts_service.py
└── src/qwen_tts_playground/
    ├── __init__.py
    ├── config.py                # pydantic-settings env config (3 model paths)
    ├── models.py                 # enums + pydantic result models
    ├── profiles.py                # accents, ages, speeds, presets, speakers (data)
    ├── prompt_builder.py          # VoicePromptBuilder -> single instruct
    ├── tts_service.py             # QwenTTSService: load once, synthesize/clone/custom-voice
    └── playground.py              # Gradio UI: Voice Design + Voice Clone + Custom Voice tabs
```

Architecture:

```text
Playground (Gradio UI, 3 tabs)
    │
    ├── Voice Design tab
    │       │
    │       ▼
    │   VoicePromptBuilder  (language, accent, gender, age, personality, emotion, speed, custom → instruct)
    │       │
    │       ▼
    │   QwenTTSService[VoiceDesign].synthesize(text, language, instruct)
    │       │
    │       ▼
    │   Qwen3TTSModel.generate_voice_design(...)  (loaded lazily, on first use)
    │
    ├── Voice Clone tab
    │       │
    │       ▼
    │   QwenTTSService[Base].synthesize_voice_clone(text, language, ref_audio, ref_text)
    │       │
    │       ▼
    │   Qwen3TTSModel.generate_voice_clone(...)  (loaded lazily, on first use)
    │
    └── Custom Voice tab
            │
            ▼
        QwenTTSService[CustomVoice].synthesize_custom_voice(text, language, speaker, instruct)
            │
            ▼
        Qwen3TTSModel.generate_custom_voice(...)  (loaded lazily, on first use)

    All three paths write → WAV file under outputs/
```

## 16. Tests & linting

Tests fully mock the model — **they never load real Qwen3-TTS weights**:

```bash
uv run pytest
```

Lint / format:

```bash
uv run ruff check .
uv run ruff format .
```

## 17. Output files

Generated audio is written to `OUTPUT_DIR` (default `outputs/`) as WAV,
never overwriting existing files:

```text
{language}_{accent}_{gender}_{timestamp}.wav
# Voice Design, e.g.:  spanish_peruvian_female_20260923_001530.wav
# Voice Clone, e.g.:   english_clone_voice_20260923_020846.wav
# Custom Voice, e.g.:  english_ryan_voice_20260923_141543.wav
```

## 18. Session history

The UI keeps an in-memory table (timestamp, mode, language, accent, gender,
voice style, generation time, audio duration, RTF, filename) shared across
all three tabs, for the current browser session only — no database is used.

## 19. Running with Docker

A `Dockerfile` is provided. It uses a plain `python:3.12-slim` base — **no
CUDA Toolkit inside the image** — because PyTorch's pip wheel already
bundles the CUDA *runtime* libraries it needs (cuBLAS, cuDNN, NCCL, ...).
GPU access at `docker run` time comes entirely from the **host's** NVIDIA
driver + container runtime; only `libcuda.so` (the driver API) is injected
into the container.

### Build

```bash
docker build -t qwen-tts-playground .
```

The image is ~6.7 GB and takes a while the first time; `uv sync` layers are
cached separately from source code changes, so rebuilding after editing
`src/` is fast.

**Why it's this big / what's already trimmed:** ~75% of the image is the
CUDA + PyTorch + Triton stack itself — `nvidia/*` wheels (cuBLAS, cuDNN,
cuFFT, NCCL, cuSPARSELt, NVSHMEM: ~3.2 GB), `torch` (~1.2 GB), `triton`
(~0.9 GB after trimming, see below). This is not really reducible without
dropping GPU support: NCCL, cuSPARSELt and NVSHMEM are hard-linked into
`torch._C` at import time in this wheel even though a single-GPU app never
uses them — deleting any of them breaks `import torch` outright (verified).
What *was* safe to remove (and already is, in the `Dockerfile`): Triton's
bundled CUPTI profiler static libs and torch's C++ headers (`torch/include`,
only needed to build custom extensions) — together ~340 MB, confirmed
unused by re-running a real Triton JIT kernel compile and
`scaled_dot_product_attention` after deleting them. One gotcha if you touch
this: the `rm -rf` for these has to live in the *same* `RUN` as the `uv
sync` that installs them — overlayfs layers are additive, so deleting files
in a later layer only hides them (0 bytes saved on the image) while the
bytes still ship in the earlier layer.

### Run

Models are **not** baked into the image (multi-GB, and you likely already
have them locally per §4) — mount them, along with `outputs/`, as volumes:

```bash
docker run -d --name qwen-tts-playground \
  --gpus all \
  -p 7860:7860 \
  -v "$(pwd)/models:/app/models:ro" \
  -v "$(pwd)/outputs:/app/outputs" \
  qwen-tts-playground
```

Then open <http://127.0.0.1:7860>.

- `--gpus all` is the standard flag on most Docker + NVIDIA Container
  Toolkit setups. If it fails with an error mentioning `cdi`/`nvidia`
  runtime hooks, use `--runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all`
  instead (needed, and verified working, on the machine this was built on).
- Omit `--gpus all` / `--runtime=nvidia` entirely to run on CPU (much
  slower, but works — same CPU fallback as running outside Docker).
- The image sets `PLAYGROUND_HOST=0.0.0.0` by default (required for the
  server to be reachable from outside the container); override any setting
  from §5 with `-e VAR=value` or `--env-file .env`.
- All three models are still loaded lazily on first use of their tab (§4) —
  starting the container is fast regardless of which/how many models are
  configured.
- The container runs as a **non-root user** (`appuser`, UID/GID 1000 by
  default — the common single-user-Linux-desktop id) instead of root, so
  files it writes into `outputs/` come out owned by you on the host, not
  root. If your host user's UID/GID isn't 1000 (`id -u` / `id -g`), rebuild
  with `docker build --build-arg APP_UID=$(id -u) --build-arg
  APP_GID=$(id -g) .` so writes match your user exactly.
- **If `outputs/` already contains root-owned files** (e.g. left over from
  an older build of this image that ran as root), fix it once with
  `sudo chown -R "$USER":"$USER" outputs/` — otherwise the non-root
  container can't write into a directory it doesn't own, and generation
  fails with a `soundfile.LibsndfileError: ... System error` (a permission
  error that `libsndfile` doesn't report clearly). This applies whether
  you're generating from inside Docker or from `uv run` directly on the
  host afterward.

### Run with Docker Compose

A `docker-compose.yml` is also provided, wrapping the same build/run/volumes
behavior above:

```bash
docker compose up --build     # build the image and start the app
docker compose up -d          # start in the background (image already built)
docker compose down           # stop and remove the container
```

- It uses `runtime: nvidia` (the form confirmed working on this host — see
  the `--gpus all` note above). If you have no NVIDIA GPU, delete the
  `runtime: nvidia` line and the two `NVIDIA_*` environment variables from
  `docker-compose.yml` to run on CPU.
- Copy `.env.example` to `.env` to override any setting from §5 (e.g.
  `PLAYGROUND_PORT`) — `docker-compose.yml` loads it automatically
  (`env_file`, optional) and it is *not* baked into the image.
- `./models` and `./outputs` are bind-mounted the same way as the manual
  `docker run` command, so models placed there per §4 are picked up as-is.

### Verified

This exact `Dockerfile` was built and run on the machine this project was
developed on (GPU: RTX 500 Ada, 4GB VRAM): the container started, found the
mounted model snapshots, generated real audio on GPU inside the container,
and wrote the WAV back out through the `outputs/` volume mount. One
non-obvious fix was required and is already baked into the Dockerfile:
`build-essential` — without a C compiler, PyTorch/Triton's runtime kernel
JIT-compilation fails with `Failed to find C compiler` on first generation,
even though the image builds and the UI serves pages just fine without it.
