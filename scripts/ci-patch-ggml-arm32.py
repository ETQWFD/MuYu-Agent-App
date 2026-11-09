#!/usr/bin/env python3
"""Drop ggml's 32-bit ARM fallback for vcvtnq_s32_f32 on clang.

NDK r29 (clang 20) arm_neon.h already declares vcvtnq_s32_f32 for AArch32, so the
hand-rolled fallback inside `#if !defined(__aarch64__)` becomes a redefinition and
breaks the armeabi-v7a build. The other fallbacks in that block (vaddlvq_s16,
vpaddq_s16, ...) are genuinely missing on AArch32 and stay untouched.
"""
import pathlib
import sys

SIG = "inline static int32x4_t vcvtnq_s32_f32(float32x4_t v) {"

def main(path: str) -> int:
    p = pathlib.Path(path)
    s = p.read_text()
    if "#if !defined(__clang__)  // MCA: clang arm_neon.h provides vcvtnq_s32_f32" in s:
        print("already patched")
        return 0
    start = s.index(SIG)
    i = s.index("{", start)
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                end = j + 1
                break
    block = s[start:end]
    patched = (
        "#if !defined(__clang__)  // MCA: clang arm_neon.h provides vcvtnq_s32_f32\n"
        + block
        + "\n#endif  // MCA: clang arm_neon.h provides vcvtnq_s32_f32"
    )
    p.write_text(s[:start] + patched + s[end:])
    print("patched", p)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
