#!/bin/bash
# ==============================================================================
# MLC-LLM Vulkan Compiler Script (Android Tensor G5)
# Run this on your build machine (Mac/Linux/Windows WSL)
# ==============================================================================

echo "--- Starting Vulkan AOT Compilation for Qwen 0.8B ---"

# 1. Verify mlc_llm is installed
if ! command -v mlc_llm &> /dev/null; then
    echo "Error: mlc_llm compiler not found!"
    echo "Please run: pip install --pre -U -f https://mlc.ai/wheels mlc-llm-nightly mlc-ai-nightly"
    exit 1
fi

MODEL_DIR="../"
MODEL_NAME="Qwen3.5-0.8B-uav-flight"
OUTPUT_DIR="dist/$MODEL_NAME-android"

echo "1. Converting weights to MLC format (q4f16_1 for mobile)..."
mlc_llm convert_weight $MODEL_DIR/$MODEL_NAME.gguf \
    --quantization q4f16_1 \
    --output $OUTPUT_DIR/params

echo "2. Generating mlc-chat-config.json..."
mlc_llm gen_config $MODEL_DIR/$MODEL_NAME.gguf \
    --quantization q4f16_1 \
    --conv-template chatml \
    --context-window-size 512 \
    --output $OUTPUT_DIR/params

echo "3. Compiling Vulkan shader library for Android NDK..."
mlc_llm compile $OUTPUT_DIR/params/mlc-chat-config.json \
    --device android \
    --output $OUTPUT_DIR/$MODEL_NAME-android.tar

echo "--- ✅ Compilation Complete ---"
echo "Your Vulkan library is ready: $OUTPUT_DIR/$MODEL_NAME-android.tar"
echo "Follow the Android_README.md to bundle this into your APK."
