#!/usr/bin/env bash
# Stage libgirepository dev files into the venv so PyGObject can build from
# source WITHOUT any system-level (sudo) install.
#
# PyGObject's sdist needs girepository's headers + pkg-config entry, which
# Ubuntu doesn't ship by default. This downloads the .deb (no root), unpacks
# it under $VENV/gi-dev, binds the dev .so symlink to the system's already-
# present runtime library, and writes a correct girepository-2.0.pc that
# points at the staged prefix.
#
# Usage:
#   tools/stage-girepository.sh            # stages into .venv/gi-dev
#   tools/stage-girepository.sh .venv2     # custom venv path
#
# Then install with the staged pkg-config on PATH:
#   PKG_CONFIG_PATH="$PWD/.venv/gi-dev/usr/lib/x86_64-linux-gnu/pkgconfig" \
#     .venv/bin/pip install -r requirements.txt
set -euo pipefail

VENV="${1:-.venv}"
VENV="$(cd "$(dirname "$VENV")" 2>/dev/null && pwd)/$(basename "$VENV")"
STAGE="$VENV/gi-dev"
BUILD="$VENV/gi-build"

ARCH="$(dpkg --print-architecture 2>/dev/null || echo amd64)"
MULTIARCH="$(dpkg-architecture -qDEB_HOST_MULTIARCH 2>/dev/null || echo x86_64-linux-gnu)"
LIBS="$STAGE/usr/lib/$MULTIARCH"
PKGCONFIG="$LIBS/pkgconfig"

mkdir -p "$BUILD"
cd "$BUILD"

if ! ls libgirepository-2.0-dev_*.deb >/dev/null 2>&1; then
    apt download libgirepository-2.0-dev
fi
DEB="$(ls libgirepository-2.0-dev_*.deb | head -1)"
[ -n "$DEB" ] || { echo "apt download failed" >&2; exit 1; }

rm -rf "$STAGE"
mkdir -p "$STAGE"
dpkg-deb -x "$DEB" "$STAGE"

# The dev package's .so is a relative symlink (-> libgirepository-2.0.so.0);
# the runtime .so.0 itself ships separately. Bind it to the system runtime
# shared lib, which is already present on the box this repo targets.
RUNTIME="$(ls /usr/lib/$MULTIARCH/libgirepository-2.0.so.0* 2>/dev/null | head -1)"
if [ -n "$RUNTIME" ] && [ -L "$LIBS/libgirepository-2.0.so" ]; then
    ln -sf "$RUNTIME" "$LIBS/libgirepository-2.0.so.0"
fi

# Regenerate a correct .pc: the shipped one hardcodes prefix=/usr. Headers
# live under include/glib-2.0/girepository, so Cflags must add that subdir.
mkdir -p "$PKGCONFIG"
cat > "$PKGCONFIG/girepository-2.0.pc" <<EOF
prefix=$STAGE/usr
datadir=\${prefix}/share
includedir=\${prefix}/include
libdir=$LIBS

gidatadir=\${datadir}/gobject-introspection-1.0
girdir=\${datadir}/gir-1.0
typelibdir=\${libdir}/girepository-1.0
gi_compile_repository=\${libdir}/glib-2.0/gi-compile-repository

Name: girepository
Description: GObject Introspection repository parser
Version: 2.88.0
Requires: glib-2.0, gobject-2.0
Requires.private: gmodule-no-export-2.0, gio-2.0, libffi >= 3.0.0
Libs: -L\${libdir} -lgirepository-2.0
Libs.private: -lm
Cflags: -I\${includedir}/glib-2.0
EOF

echo "staged girepository dev files -> $STAGE"
echo
echo "install like so:"
echo "PKG_CONFIG_PATH=\"$PKGCONFIG\" .venv/bin/pip install -r requirements.txt"