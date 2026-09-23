# Qwen3-TTS VoiceDesign Playground

A local, professional web playground to experiment with **text-to-speech**
using [`Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign):
Spanish, Portuguese and English, with configurable accent, gender, age,
personality, emotion, speed, style and free-text instructions — evaluated
against a banking-assistant use case.

```text
Language → Accent → Gender → Age → Personality → Emotion → Speed
    → VoiceDesign Prompt → Text → Generate → Qwen3-TTS → Audio Player
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

## 4. Getting the model

### Option A — download it locally (recommended for repeated use)

```bash
uv run hf download \
  Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
  --local-dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

Then point the app at it via `.env`:

```env
QWEN_TTS_MODEL_PATH=./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
```

### Option B — stream from the Hugging Face Hub

If `QWEN_TTS_MODEL_PATH` does not exist (or is empty), the app falls back to
the Hub repo id `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` directly, letting
`from_pretrained` download and cache it under `~/.cache/huggingface`.

In both cases **the model is loaded exactly once**, at process startup — never
per-request.

## 5. Configuration

Copy `.env.example` to `.env` and adjust as needed:

```env
QWEN_TTS_MODEL_PATH=./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
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

## 10. GPU usage & performance metrics

- The model loads once as `cuda:0` + `torch.bfloat16` when a CUDA GPU is
  available (`float32` on CPU).
- `attn_implementation="flash_attention_2"` is used automatically **only**
  if the `flash-attn` package is importable; otherwise the default
  (SDPA/eager) attention implementation is used. FlashAttention is never a
  hard requirement.
- Every generation reports:
  - **Generation time** (`time.perf_counter()`)
  - **Audio duration** (`len(wav) / sample_rate`)
  - **RTF** = `generation_time / audio_duration` (lower is better; `< 1.0`
    means faster than real time)
  - **Sample rate**, **GPU name**, **VRAM allocated/reserved**
    (`torch.cuda.memory_allocated()` / `memory_reserved()`)

## 11. Thread safety

GPU inference is serialized behind a lock in `QwenTTSService`. Concurrent
clicks in the UI queue instead of racing on the same model instance, which
avoids state corruption and reduces OOM risk from overlapping generations.

## 12. Troubleshooting CUDA OOM

The 1.7B model in `bfloat16` needs a few GB of VRAM plus activation memory
that scales with text length. If you hit `CudaOutOfMemoryError`:

- Shorten the input text or split it into shorter segments.
- Close other GPU-using processes (check with `nvidia-smi`).
- Lower `max_new_tokens` via **Advanced Settings** if exposed, or reduce
  `Top K`/`Top P` sampling breadth.
- If you are on a GPU with very limited VRAM (e.g. 4-6 GB laptop GPUs), fall
  back to CPU by unsetting CUDA (`CUDA_VISIBLE_DEVICES=""`) — generation will
  be much slower but still functional for evaluation purposes.
- The app calls `torch.cuda.empty_cache()` after an OOM to help recovery for
  the next attempt without restarting the process.

## 13. Project structure

```text
qwen-tts-playground/
├── pyproject.toml
├── uv.lock
├── README.md
├── .env.example
├── .gitignore
├── models/                      # local model snapshots (gitignored)
├── outputs/                     # generated WAV files (gitignored)
├── tests/
│   ├── test_profiles.py
│   ├── test_prompt_builder.py
│   └── test_tts_service.py
└── src/qwen_tts_playground/
    ├── __init__.py
    ├── config.py                # pydantic-settings env config
    ├── models.py                 # enums + pydantic result models
    ├── profiles.py                # accents, ages, speeds, presets (data)
    ├── prompt_builder.py          # VoicePromptBuilder -> single instruct
    ├── tts_service.py             # QwenTTSService: load once, synthesize
    └── playground.py              # Gradio UI (entry point)
```

Architecture:

```text
Playground (Gradio UI)
    │
    ▼
VoicePromptBuilder  (language, accent, gender, age, personality, emotion, speed, custom → instruct)
    │
    ▼
QwenTTSService.synthesize(text, language, instruct)
    │
    ▼
Qwen3TTSModel.generate_voice_design(...)  (loaded once at startup)
    │
    ▼
WAV file under outputs/
```

## 14. Tests & linting

Tests fully mock the model — **they never load real Qwen3-TTS weights**:

```bash
uv run pytest
```

Lint / format:

```bash
uv run ruff check .
uv run ruff format .
```

## 15. Output files

Generated audio is written to `OUTPUT_DIR` (default `outputs/`) as WAV,
never overwriting existing files:

```text
{language}_{accent}_{gender}_{timestamp}.wav
# e.g. spanish_peruvian_female_20260923_001530.wav
```

## 16. Session history

The UI keeps an in-memory table (timestamp, language, accent, gender, voice
style, generation time, audio duration, RTF, filename) for the current
browser session only — no database is used.
