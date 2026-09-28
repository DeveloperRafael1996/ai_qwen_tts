.PHONY: help sync run test lint format check \
	models models-voicedesign models-clone models-customvoice \
	docker-build docker-run docker-up docker-down docker-logs \
	benchmark clean

help:
	@echo "Qwen3-TTS VoiceDesign Playground"
	@echo ""
	@echo "Setup:"
	@echo "  make sync                 uv sync (crea .venv e instala dependencias)"
	@echo "  make models               descarga los 3 modelos a ./models"
	@echo ""
	@echo "Desarrollo:"
	@echo "  make run                  levanta el playground (http://127.0.0.1:7860)"
	@echo "  make test                 uv run pytest"
	@echo "  make lint                 uv run ruff check ."
	@echo "  make format               uv run ruff format ."
	@echo "  make check                lint + test"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build         docker build -t qwen-tts-playground ."
	@echo "  make docker-run           docker run con --gpus all y volumenes"
	@echo "  make docker-up            docker compose up --build"
	@echo "  make docker-down          docker compose down"
	@echo "  make docker-logs          docker compose logs -f"
	@echo ""
	@echo "Otros:"
	@echo "  make benchmark            scripts/benchmark_tts.py --attention both"
	@echo "  make clean                borra caches de pytest/ruff"

sync:
	uv sync

run:
	uv run python -m qwen_tts_playground.playground

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

check: lint test

models: models-voicedesign models-clone models-customvoice

models-voicedesign:
	uv run hf download Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign \
		--local-dir ./models/Qwen3-TTS-12Hz-1.7B-VoiceDesign

models-clone:
	uv run hf download Qwen/Qwen3-TTS-12Hz-0.6B-Base \
		--local-dir ./models/Qwen3-TTS-12Hz-0.6B-Base

models-customvoice:
	uv run hf download Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice \
		--local-dir ./models/Qwen3-TTS-12Hz-0.6B-CustomVoice

docker-build:
	docker build -t qwen-tts-playground .

docker-run:
	docker run -d --name qwen-tts-playground \
		--gpus all \
		-p 7860:7860 \
		-v "$(CURDIR)/models:/app/models:ro" \
		-v "$(CURDIR)/outputs:/app/outputs" \
		qwen-tts-playground

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

benchmark:
	uv run python scripts/benchmark_tts.py --attention both

clean:
	rm -rf .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} +
