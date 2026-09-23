# Qwen3-TTS VoiceDesign Playground

A local, professional web playground to experiment with **text-to-speech**
in Spanish, Portuguese and English, with two tabs backed by two different
Qwen3-TTS models:

- **Voice Design** — [`Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign):
  configurable accent, gender, age, personality, emotion, speed, style and
  free-text instructions, evaluated against a banking-assistant use case.
- **Voice Clone** — [`Qwen/Qwen3-TTS-12Hz-0.6B-Base`](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base):
  clone a voice from a short reference audio clip (+ optional reference
  text) instead of describing it with words.

```text
Voice Design tab:
Language → Accent → Gender → Age → Personality → Emotion → Speed
    → VoiceDesign Prompt → Text → Generate → Qwen3-TTS-1.7B-VoiceDesign → Audio Player

Voice Clone tab:
Language → Reference Audio (+ Reference Text) → Text → Generate
    → Qwen3-TTS-0.6B-Base → Audio Player
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

This app uses two separate Qwen3-TTS checkpoints, one per tab.

### Option A — download them locally (recommended for repeated use)

```bash
uv run hf download \
  Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
  --local-dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign

uv run hf download \
  Qwen/Qwen3-TTS-12Hz-0.6B-Base \
  --local-dir ./models/Qwen3-TTS-12Hz-0.6B-Base
```

Then point the app at them via `.env`:

```env
QWEN_TTS_MODEL_PATH=./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
QWEN_TTS_VOICE_CLONE_MODEL_PATH=./models/Qwen3-TTS-12Hz-0.6B-Base
```

### Option B — stream from the Hugging Face Hub

If either path does not exist (or is empty), the app falls back to the
matching Hub repo id (`Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` or
`Qwen/Qwen3-TTS-12Hz-0.6B-Base`) directly, letting `from_pretrained` download
and cache it under `~/.cache/huggingface`.

### Loading behavior

Both models are currently loaded **lazily**: nothing is loaded at process
startup, and each model loads (once) on the first "Generate..." click in its
tab, then stays cached in memory for the rest of the session (never reloaded
per-request).

This is deliberate: many GPUs (e.g. a 4-6GB laptop GPU) cannot even fit the
1.7B VoiceDesign model on its own, let alone both models at once, so eager
loading at startup would crash the whole app before it serves a single
page. See §12 for VRAM numbers observed in practice.

If your hardware can comfortably fit the VoiceDesign model, you can restore
eager loading (load-once-at-startup, fail-fast instead of failing on first
click) by uncommenting the `service.load()` call in `main()`
(`src/qwen_tts_playground/playground.py`).

## 5. Configuration

Copy `.env.example` to `.env` and adjust as needed:

```env
QWEN_TTS_MODEL_PATH=./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign
QWEN_TTS_VOICE_CLONE_MODEL_PATH=./models/Qwen3-TTS-12Hz-0.6B-Base
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

## 12. GPU usage & performance metrics

- Each model loads once as `cuda:0` + `torch.bfloat16` when a CUDA GPU is
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

Numbers observed on a 4GB laptop GPU (NVIDIA RTX 500 Ada, 3.65 GiB usable):
the 1.7B VoiceDesign model does **not** fit (`CudaOutOfMemoryError` while
loading), while the 0.6B Base voice-clone model **does** fit comfortably
(~2.1 GiB allocated, 1.4 GiB still free) and produced audio with RTF ≈ 1.3.
Your mileage will vary with driver/CUDA version and other processes holding
VRAM — see §13 for the VoiceDesign fallback.

## 13. Thread safety

GPU inference is serialized behind a lock in `QwenTTSService`. Concurrent
clicks in the UI queue instead of racing on the same model instance, which
avoids state corruption and reduces OOM risk from overlapping generations.
Each tab's model has its own `QwenTTSService` instance/lock, so a Voice
Design generation and a Voice Clone generation could in principle run
concurrently — but on a single GPU with limited VRAM, running both tabs at
once is likely to OOM; prefer using one tab at a time on constrained
hardware.

## 14. Troubleshooting CUDA OOM

Both models need a few GB of VRAM (more for the 1.7B VoiceDesign model)
plus activation memory that scales with text length. If you hit
`CudaOutOfMemoryError`, whether while loading a model or during generation:

- Shorten the input text or split it into shorter segments.
- Close other GPU-using processes (check with `nvidia-smi`).
- Lower `max_new_tokens` via **Advanced Settings** if exposed, or reduce
  `Top K`/`Top P` sampling breadth.
- Try the smaller Voice Clone (0.6B) model instead of VoiceDesign (1.7B) if
  your GPU can't fit the larger one — see the VRAM numbers in §12.
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
├── models/                      # local model snapshots (gitignored)
├── outputs/                     # generated WAV files (gitignored)
├── tests/
│   ├── test_profiles.py
│   ├── test_prompt_builder.py
│   └── test_tts_service.py
└── src/qwen_tts_playground/
    ├── __init__.py
    ├── config.py                # pydantic-settings env config (2 model paths)
    ├── models.py                 # enums + pydantic result models
    ├── profiles.py                # accents, ages, speeds, presets (data)
    ├── prompt_builder.py          # VoicePromptBuilder -> single instruct
    ├── tts_service.py             # QwenTTSService: load once, synthesize (+ clone)
    └── playground.py              # Gradio UI: Voice Design tab + Voice Clone tab
```

Architecture:

```text
Playground (Gradio UI, 2 tabs)
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
    └── Voice Clone tab
            │
            ▼
        QwenTTSService[Base].synthesize_voice_clone(text, language, ref_audio, ref_text)
            │
            ▼
        Qwen3TTSModel.generate_voice_clone(...)  (loaded lazily, on first use)

    Both paths write → WAV file under outputs/
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
# Voice Design, e.g.: spanish_peruvian_female_20260923_001530.wav
# Voice Clone, e.g.:  english_clone_voice_20260923_020846.wav
```

## 18. Session history

The UI keeps an in-memory table (timestamp, mode, language, accent, gender,
voice style, generation time, audio duration, RTF, filename) shared across
both tabs, for the current browser session only — no database is used.
