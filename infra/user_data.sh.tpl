#!/bin/bash
# First-boot provisioning. Progress: /var/log/qwen-setup.log
exec > >(tee -a /var/log/qwen-setup.log) 2>&1
set -euxo pipefail

APP_DIR=/opt/qwen-tts
REPO_URL="${repo_url}"
TOKEN="${github_token}"

if [ -n "$TOKEN" ]; then
  REPO_URL="$${REPO_URL/https:\/\//https://x-access-token:$${TOKEN}@}"
fi

git clone --branch "${repo_branch}" --depth 1 "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"
mkdir -p models outputs
# The container runs as uid/gid 1000 (see Dockerfile APP_UID/APP_GID).
chown -R 1000:1000 models outputs

docker compose build

# Download the three models into ./models using the app image's `hf` CLI.
for m in Qwen3-TTS-12Hz-1.7B-VoiceDesign Qwen3-TTS-12Hz-0.6B-Base Qwen3-TTS-12Hz-0.6B-CustomVoice; do
  docker compose run --rm --no-deps --entrypoint hf qwen-tts-playground \
    download "Qwen/$m" --local-dir "/app/models/$m"
done

docker compose up -d
echo "Qwen TTS setup finished"
