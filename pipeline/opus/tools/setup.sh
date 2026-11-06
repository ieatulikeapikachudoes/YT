#!/usr/bin/env bash
# One-time setup for a fresh cloud workspace. Run from anywhere. No API keys needed.
set -e
cd "$(dirname "$0")/.."
[ -d node_modules/hyperframes ] || npm install --no-audit --no-fund hyperframes puppeteer-core >/dev/null
# kit assets that are not stored in the Project (binary / large)
mkdir -p kit/fonts kit/vendor
if [ ! -f kit/fonts/geist.woff2 ]; then T=$(mktemp -d); (cd $T && npm pack geist@1.3.1 >/dev/null 2>&1 && tar xzf geist-1.3.1.tgz); cp $T/package/dist/fonts/geist-sans/Geist-Variable.woff2 kit/fonts/geist.woff2; rm -rf $T; fi
if [ ! -f kit/vendor/gsap.min.js ]; then T=$(mktemp -d); (cd $T && npm pack gsap@3.14.2 >/dev/null 2>&1 && tar xzf gsap-3.14.2.tgz); cp $T/package/dist/gsap.min.js kit/vendor/gsap.min.js; rm -rf $T; fi
[ -f kit/hyperframes.json ] || echo '{"$schema":"https://hyperframes.heygen.com/schema/hyperframes.json","paths":{"assets":"assets"},"media":{"autoProxy":true}}' > kit/hyperframes.json
[ -f kit/package.json ] || echo '{"name":"short","private":true,"type":"module"}' > kit/package.json
pip install --break-system-packages -q kokoro-onnx soundfile sherpa-onnx numpy pillow
mkdir -p models && cd models
[ -f kokoro-v1.0.onnx ] || curl -sSL -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f voices-v1.0.bin ] || curl -sSL -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
[ -d sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8 ] || (curl -sSL -o p.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2 && tar xjf p.tar.bz2 && rm p.tar.bz2)
echo "export KOKORO_MODEL_DIR=$(pwd) PARAKEET_DIR=$(pwd)/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8"
