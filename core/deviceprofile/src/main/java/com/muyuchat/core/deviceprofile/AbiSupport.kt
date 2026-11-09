package com.muyuchat.core.deviceprofile

import android.os.Build
import android.os.Process

/**
 * Runtime ABI capability of the current process.
 *
 * MuYu-Agent ships the same Java/Kotlin surface for 64-bit and 32-bit installs. The vendor
 * inference runtimes (GenieX/QAIRT, QNN, MNN diffusion, Qwen-Image-2.1, MediaTek Neuron) are
 * published as `arm64-v8a` binaries only, so a 32-bit process must be detected before any of
 * them is touched. `System.loadLibrary` on a missing ABI kills the process with
 * `UnsatisfiedLinkError`; every call site therefore stays behind this capability check or behind
 * a `runCatching` load, and the UI explains which engines are unavailable instead of crashing.
 */
object AbiSupport {

    /** True for a 64-bit process (`Process.is64Bit`, available since API 23). */
    val is64BitProcess: Boolean = runCatching { Process.is64Bit() }.getOrDefault(false)

    /** The ABI this process was launched with, e.g. `arm64-v8a` or `armeabi-v7a`. */
    val primaryAbi: String = Build.SUPPORTED_ABIS.firstOrNull().orEmpty()

    /** 32-bit installs (armeabi-v7a / armeabi on older devices). */
    val is32BitProcess: Boolean get() = !is64BitProcess

    /**
     * llama.cpp text inference is compiled for every packaged ABI, so it is available whenever the
     * process is 64-bit *or* the 32-bit build shipped `libmca_native.so`.
     */
    val supportsTextInference: Boolean get() = true

    /** Vendor NPU/GPU runtimes (QNN, GenieX, MediaTek Neuron) only exist for arm64. */
    val supportsVendorNpu: Boolean get() = is64BitProcess && primaryAbi == "arm64-v8a"

    /** Human-readable tag for the About screen and support reports. */
    val label: String
        get() = buildString {
            append(primaryAbi)
            append(if (is64BitProcess) " · 64 位" else " · 32 位")
            if (!supportsVendorNpu) append(" · 厂商 NPU 不可用")
        }
}
