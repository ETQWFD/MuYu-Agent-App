# MuYu-Agent（ET 发行版）

本仓库是 [MuYu Chat Agent](https://github.com/lyydfys/MuYu-Chat-Agent)（作者 lyydfys，Apache-2.0）的再发行版本，
主要改动集中在品牌、32 位支持与更新通道。原作者署名保留在「设置 → 关于」的「原作者」条目与 `NOTICE` 中。

## 与上游的差异

| 项目 | 上游 | MuYu-Agent |
| --- | --- | --- |
| 应用名 / 品牌 | MCA · MuYu Chat Agent | MuYu-Agent |
| 图标 | 蓝色对话气泡 | 木鱼（自适应图标） |
| ABI | arm64-v8a、x86_64 | arm64-v8a、**armeabi-v7a**、x86_64 |
| 32 位设备 | `CMakeLists.txt` 直接 `FATAL_ERROR` | 原生编译分支 + 运行时能力探测 |
| 更新源 | lyydfys/MuYu-Chat-Agent | ETQWFD/MuYu-Agent-App |
| 维护者 | lyydfys | ET（ETQWFD），原作者列为第二署名 |

## 32 位（armeabi-v7a）实现说明

1. **编译层**：`core/native` 与 `core/sd-native` 的 CMake 增加 `armeabi-v7a` 分支，使用 ARM NEON，
   关闭 KleidiAI（仅 AArch64）、OpenMP（NDK armv7 无运行时）与 OpenCL（平台实现仅在 arm64 手机路径）。
   llama.cpp 文本推理因此可以在 32 位进程内真实运行，而不是"能装不能聊"。
2. **打包层**：`abiFilters` 默认包含 `armeabi-v7a`，`app/build.gradle.kts` 的 debug ABI 校验改为
   "必须含 arm64-v8a 且只允许受支持集合"，不再强制 x86_64。
3. **运行层**：`core/deviceprofile` 的 `AbiSupport` 统一判断当前进程 ABI；厂商 NPU 库（QNN / GenieX /
   MediaTek Neuron / MNN 图像 / Qwen-Image）只有 arm64 二进制，32 位进程在「关于」页会明确标注
   "32 位兼容模式 · 厂商 NPU 不可用"，相关入口按能力降级。
4. **不闪退**：所有 `System.loadLibrary` 调用点都改为 `runCatching` + 能力查询
   （`NativeLlamaBridge`/`NativeQnnBridge`/`NativeMnnBridge`/`DshPtyNative`，以及此前会在
   `init` 中直接抛 `ExceptionInInitializerError` 的 `MediaTekNeuronJniBridge`）。

## 构建

CI（`.github/workflows/build-apk.yml`）使用上游文档化的 stub 开关构建可分发 APK：

```bash
./gradlew :app:assembleDebugDist \
  -PmcaQnnTypedBindingsRequired=false \
  -PmcaMnnVendorRequired=false \
  -PmcaWithMnnDiffusion=false \
  -Pmca.abis=arm64-v8a,armeabi-v7a
```

`debugDist` 是 `debug` 的派生类型，仅把 `isDebuggable` 置为 `false`，因此下载到的安装包不是可调试版本。
APK 使用仓库 Secrets 中的固定密钥签名，保证「检查更新 → 下载 → 安装」可以覆盖升级。

未打包的能力：高通 QNN/QAIRT 图像生成、MNN 扩散模型、Qwen-Image-2.1、MediaTek Neuron。
这些厂商运行时为 arm64 专有二进制，不在本仓库分发范围内。
