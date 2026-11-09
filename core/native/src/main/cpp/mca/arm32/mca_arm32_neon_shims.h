#pragma once
// 32-bit ARM (armeabi-v7a) NEON compatibility shims.
//
// llama.cpp's ggml/src/ggml-cpu/arch/arm/quants.c calls three AArch64-only NEON
// intrinsics (vzip1q_u8, vzip2q_u8, vqtbl1q_u8) from its Q2_0/Q4_0 dot-product kernels.
// On AArch32 the same results come from vzipq_u8 and vtbl2_u8, so provide thin
// wrappers instead of forking the kernels. This header is force-included only for
// armeabi-v7a builds; aarch64/x86_64 keep the real intrinsics.
#if defined(__ARM_NEON) && !defined(__aarch64__)

#include <arm_neon.h>

inline static uint8x16_t vzip1q_u8(uint8x16_t a, uint8x16_t b) {
    return vzipq_u8(a, b).val[0];
}

inline static uint8x16_t vzip2q_u8(uint8x16_t a, uint8x16_t b) {
    return vzipq_u8(a, b).val[1];
}

inline static int64x2_t vzip1q_s64(int64x2_t a, int64x2_t b) {
    return vcombine_s64(vget_low_s64(a), vget_low_s64(b));
}

inline static int64x2_t vzip2q_s64(int64x2_t a, int64x2_t b) {
    return vcombine_s64(vget_high_s64(a), vget_high_s64(b));
}

inline static uint8x16_t vqtbl2q_u8(uint8x16x2_t table, uint8x16_t index) {
    const uint8x8x4_t quarters = {{ vget_low_u8(table.val[0]), vget_high_u8(table.val[0]),
                                    vget_low_u8(table.val[1]), vget_high_u8(table.val[1]) }};
    return vcombine_u8(vtbl4_u8(quarters, vget_low_u8(index)),
                       vtbl4_u8(quarters, vget_high_u8(index)));
}

inline static uint8x16_t vqtbl1q_u8(uint8x16_t table, uint8x16_t index) {
    const uint8x8x2_t halves = {{ vget_low_u8(table), vget_high_u8(table) }};
    return vcombine_u8(vtbl2_u8(halves, vget_low_u8(index)),
                       vtbl2_u8(halves, vget_high_u8(index)));
}

#endif
