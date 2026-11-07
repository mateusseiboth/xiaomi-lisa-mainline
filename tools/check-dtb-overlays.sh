#!/bin/sh
# Apply the overlays the stock Xiaomi ABL applies (Gunyah hypervisor + dtbo
# board entry) to a DTB, using the upstream libufdt host tool.
#
# usage: check-dtb-overlays.sh <dtb> [ufdt_apply_overlay]
set -eu

dtb=$1
ufdt=${2:-ufdt_apply_overlay}
here=$(dirname "$0")
dtbo_src=$here/../pmaports/device/testing/device-xiaomi-lisa/dtbo-overlay.dts
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

dtc -@ -q -I dts -O dtb -o "$work/hyp.dtbo" "$here/hyp-sim-overlay.dts"
dtc -@ -q -I dts -O dtb -o "$work/board.dtbo" "$dtbo_src"

for node in /reserved-memory/splash_region /mem-offline /firmware/android/fstab; do
	fdtget -l "$dtb" "$node" >/dev/null 2>&1 || { echo "missing node: $node"; exit 1; }
done

"$ufdt" "$dtb" "$work/hyp.dtbo" "$work/step1.dtb"
"$ufdt" "$work/step1.dtb" "$work/board.dtbo" "$work/final.dtb"
echo "OK: both overlays apply"
