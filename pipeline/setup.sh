#!/usr/bin/env bash
# One-time setup for a fresh machine or cloud sandbox. Run from the repo root.
set -e

npm install --no-audit --no-fund hyperframes gsap@3.14.2
pip install --break-system-packages -q kokoro-onnx soundfile openai python-dotenv requests

# Kokoro model files (GitHub release downloads; ~340MB total)
mkdir -p kokoro-model
[ -f kokoro-model/kokoro-v1.0.onnx ] || curl -L -o kokoro-model/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f kokoro-model/voices-v1.0.bin ]  || curl -L -o kokoro-model/voices-v1.0.bin  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

# Chrome: HyperFrames downloads its own headless shell when it can. In the cloud sandbox that is blocked,
# so point it at the preinstalled one.
if [ -x /opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell ]; then
  echo 'export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'
fi
echo 'export HYPERFRAMES_SKIP_SKILLS=1'
echo 'export KOKORO_MODEL_DIR='"$(pwd)/kokoro-model"
echo "Done. Export the lines above (or source them) before building."
