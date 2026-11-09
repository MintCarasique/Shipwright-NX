#!/bin/bash
# Builds soh.nro (Docker, devkitA64) and soh.o2r (host tools) into build-switch/ and build-host/.
#   tools/switch/build.sh            incremental build
#   tools/switch/build.sh configure  reconfigure first
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
IMAGE=shipwright-nx-builder

docker image inspect $IMAGE >/dev/null 2>&1 || docker build -t $IMAGE -f "$ROOT/tools/switch/Dockerfile" "$ROOT/tools/switch"

docker run --rm -v "$ROOT":/src -w /src $IMAGE bash -c "
if [ '$1' = configure ] || [ ! -f build-switch/build.ninja ]; then
  cmake -H. -Bbuild-switch -GNinja -DCMAKE_TOOLCHAIN_FILE=/opt/devkitpro/cmake/Switch.cmake -DCMAKE_BUILD_TYPE=Release
fi
cmake --build build-switch --target soh_nro
"

# soh.o2r needs the host compiler (cmake, ninja, zlib, bzip2, libpng)
if [ "$1" = configure ] || [ ! -f "$ROOT/build-host/build.ninja" ]; then
  cmake -S "$ROOT" -B "$ROOT/build-host" -GNinja -DSOH_TOOLS_ONLY=ON -DCMAKE_BUILD_TYPE=Release
fi
cmake --build "$ROOT/build-host" --target GenerateSohOtr

echo "soh.nro: $ROOT/build-switch/soh/soh.nro"
echo "soh.o2r: $ROOT/build-host/soh/soh.o2r"
