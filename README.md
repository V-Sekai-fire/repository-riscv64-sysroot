# repository-riscv64-sysroot

A committed riscv64-linux-gnu sysroot, so clang on any host can build and link RISC-V Linux binaries without a cross-toolchain or a container.

## What it is for

It holds headers and libraries only, extracted from the sha256-pinned distribution packages listed in `pins.txt`, and sandbox guest programs are built against it. The one change from a plain copy is the C library's linker script, whose absolute paths are rewritten so lld resolves them inside the sysroot. `toolchain.cmake` points a CMake build at it.

## Build and run

```sh
pixi run verify
pixi run smoke
```

`verify` checks the committed tree against its pins, and `smoke` cross-compiles and links a C program against it and compiles a C++ one.

## Licence

The sysroot is redistributed binaries. glibc is LGPL-2.1-or-later, and libgcc and libstdc++ are GPL-3.0 with the GCC Runtime Library Exception. Their corresponding sources are the source packages named in `pins.txt`, available from https://deb.debian.org/debian/ and its archive. The repository's own scripts state no licence.
