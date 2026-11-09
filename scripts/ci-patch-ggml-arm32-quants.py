#!/usr/bin/env python3
"""Give llama.cpp's AArch32 quants build the AArch64-only NEON helpers it calls.

`ggml/src/ggml-cpu/arch/arm/quants.c` uses vzip1q_u8 / vzip2q_u8 / vqtbl1q_u8 in its
Q2_0/Q4_0 dot products. Those are AArch64-only intrinsics; on armeabi-v7a they do not
exist, so the TU fails with "call to undeclared function". The 32-bit equivalents
(vzipq_u8, vtbl2_u8) produce identical results, so define thin wrappers instead of
changing the kernels.
"""
import pathlib
import sys

SHIMS = '''
/* MCA: AArch64-only NEON helpers used by this file, expressed with AArch32 NEON. */
#if !defined(__aarch64__)
inline static uint8x16_t vzip1q_u8(uint8x16_t a, uint8x16_t b) {
    return vzipq_u8(a, b).val[0];
}
inline static uint8x16_t vzip2q_u8(uint8x16_t a, uint8x16_t b) {
    return vzipq_u8(a, b).val[1];
}
inline static uint8x16_t vqtbl1q_u8(uint8x16_t table, uint8x16_t index) {
    const uint8x8x2_t halves = {{ vget_low_u8(table), vget_high_u8(table) }};
    return vcombine_u8(vtbl2_u8(halves, vget_low_u8(index)),
                       vtbl2_u8(halves, vget_high_u8(index)));
}
#endif
/* MCA end */
'''


def main(path: str) -> int:
    p = pathlib.Path(path)
    s = p.read_text()
    if "MCA: AArch64-only NEON helpers" in s:
        print("already patched")
        return 0
    for name in ("vzip1q_u8", "vzip2q_u8", "vqtbl1q_u8"):
        if name not in s:
            print(f"{path}: nothing to patch ({name} absent)")
            return 0
    lines = s.splitlines(keepends=True)
    last_include = 0
    for i, line in enumerate(lines[:200]):
        if line.lstrip().startswith("#include"):
            last_include = i
    lines.insert(last_include + 1, SHIMS)
    p.write_text("".join(lines))
    print("patched", p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
