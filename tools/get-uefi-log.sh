#!/bin/sh
# Boot the LineageOS recovery, copy the logfs partition and print the UEFI/ABL
# log of the last normal ("Mission Mode") boot attempt.
#
# usage: get-uefi-log.sh <dir with lineage boot.img dtbo.img vendor_boot.img> [out dir]
#
# The phone must be in fastboot (Power + Volume down). This OVERWRITES boot_a,
# dtbo_a and vendor_boot_a; flash your own images again afterwards.
set -eu

lineage=$1
out=${2:-uefi-log-$(date +%Y%m%d-%H%M%S)}

for img in boot dtbo vendor_boot; do
	fastboot -S 256M flash "${img}_a" "$lineage/$img.img"
done
fastboot reboot recovery

echo "waiting for the recovery (enable ADB in Advanced if it shows unauthorized)"
until adb devices | grep -q 'recovery$'; do
	sleep 1
done

mkdir -p "$out"
adb exec-out 'dd if=/dev/block/by-name/logfs bs=1M 2>/dev/null' > "$out/logfs.img"
mcopy -s -n -i "$out/logfs.img" ::/ "$out/"
adb exec-out 'cat /sys/firmware/fdt' > "$out/final-fdt.dtb"

for log in "$out"/UefiLog*.txt; do
	tr -d '\0' < "$log" | grep -aq 'Mission Mode' || continue
	echo "== $(basename "$log")"
	tr -d '\0' < "$log" | sed -n '/Booting Into Mission Mode/,/Launching fastboot/p'
done
