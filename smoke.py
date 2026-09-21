#!/usr/bin/env python3
"""Cross-compile and link a C program to riscv64, and check what came out.

A sysroot that compiles but cannot link is the failure worth catching: headers
are easy, startup files and the libc linker script are not.
"""

import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
SYSROOT = ROOT / "sysroot"
GCC_LIB = SYSROOT / "lib" / "gcc-cross" / "14"

# Touches malloc, libm and stdio, so a link that resolves them has really found
# glibc rather than just the headers.
SOURCE = """
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
int main(void) {
    double *v = malloc(4 * sizeof(double));
    for (int i = 0; i < 4; i++) v[i] = sqrt((double)(i + 1));
    if (v[3] > 1.9) puts("ok");
    free(v);
    return 0;
}
"""


def build(out_dir, link):
    src = out_dir / "smoke.c"
    src.write_text(SOURCE, encoding="utf-8")
    out = out_dir / ("smoke.elf" if link else "smoke.o")
    cmd = ["clang", "--target=riscv64-unknown-linux-gnu", "--sysroot=" + str(SYSROOT)]
    if link:
        cmd += ["-fuse-ld=lld", "-B" + str(GCC_LIB), "-L" + str(GCC_LIB),
                str(src), "-o", str(out), "-lm"]
    else:
        cmd += ["-c", str(src), "-o", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc, out


def first_error(proc):
    for line in proc.stderr.splitlines():
        if "error" in line:
            return line.strip()
    return (proc.stderr.strip().splitlines() or ["(no output)"])[0]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)

        proc, obj = build(tmp, link=False)
        if proc.returncode != 0 or not obj.exists():
            print("FAIL  compile to riscv64: " + first_error(proc))
            return 1
        print("PASS  compiles to a riscv64 object")

        proc, elf = build(tmp, link=True)
        if proc.returncode != 0 or not elf.exists():
            print("FAIL  link against the sysroot: " + first_error(proc))
            return 1

        data = elf.read_bytes()
        # ELF64, little-endian, e_machine 243 = RISC-V.
        if data[:4] != b"\x7fELF" or data[4] != 2 or data[5] != 1:
            print("FAIL  output is not a 64-bit little-endian ELF")
            return 1
        machine = int.from_bytes(data[18:20], "little")
        if machine != 243:
            print("FAIL  e_machine is " + str(machine) + ", expected 243 (RISC-V)")
            return 1
        print("PASS  links a riscv64 executable (" + str(len(data)) + " bytes, e_machine 243)")

    print("2/2 checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
