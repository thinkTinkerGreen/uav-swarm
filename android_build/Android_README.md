# 📱 UAV Swarm Mobile Deployment (Tensor G5)

This folder contains the build pipeline to cross-compile our fine-tuned 0.8B SLM into a highly-optimized Vulkan shader library for the Google Pixel 10 (Tensor G5). 

This completely bypasses the weak mobile CPU, offloading inference directly to the Tensor GPU for sub-100ms latency!

## Step 1: Compile the Weights
Because cross-compiling for Android requires the Android NDK and Rust, you should run this on your local developer machine (e.g., your MacBook or Windows PC).

1. Install the compiler: `pip install --pre -U -f https://mlc.ai/wheels mlc-llm-nightly mlc-ai-nightly`
2. Run the build script: `./compile_vulkan.sh`

This generates a `<model>-android.tar` file. This tar file contains the baked Vulkan matrix-multiplication math.

## Step 2: Build the Android APK
1. Clone the official MLC-LLM Android template:
   ```bash
   git clone https://github.com/mlc-ai/mlc-llm.git
   cd mlc-llm/android
   ```
2. Copy the `.tar` file we generated into `mlc-llm/android/library/`.
3. Open `mlc-llm/android/MLCChat/app/src/main/assets/mlc-app-config.json` and add our model:
   ```json
   {
     "model_list": [
       {
         "model_id": "Qwen3.5-0.8B-uav-flight",
         "model_lib": "Qwen3.5-0.8B-uav-flight-android",
         "model_url": "local"
       }
     ]
   }
   ```
4. Open the project in **Android Studio**.
5. Build and deploy the APK to your Pixel 10!

## Step 3: Bridging the Physics Engine
Once the LLM is running locally on the phone natively via Vulkan, you will integrate `swarm_env.py` (the physics sandbox) onto the phone. The recommended approach is using [Chaquopy](https://chaquo.com/chaquopy/), an incredibly fast Python SDK for Android.

Inside your Kotlin/Java app:
```kotlin
// Android Kotlin Code
val env = Python.getInstance().getModule("swarm_env").callAttr("SwarmEnvironment")
// The Android App now runs the 33Hz physics engine natively!
```
