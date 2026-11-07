# Reading the bootloader's own logs

The ABL gives no feedback on screen when it refuses a boot. It does log
everything, though: XBL/UEFI and the ABL write `UefiLog0.txt` to
`UefiLog4.txt` (rotating) to the `logfs` partition, a small FAT volume.

Xiaomi's fastboot has no `fetch` command, so `logfs` has to be read from a
running system with root. The official LineageOS recovery for `lisa` works
well for this: it has `adb` as root.

## Steps

1. Download the LineageOS `boot.img`, `dtbo.img` and `vendor_boot.img` for
   `lisa` from <https://download.lineageos.org/devices/lisa> and check the
   SHA-256.
2. After a failed boot, enter fastboot with Power + Volume down.
3. Run `tools/get-uefi-log.sh <dir-with-lineage-images>`. It flashes the
   recovery to slot `a`, boots into it, copies `logfs` and prints the log of
   the last normal boot attempt. Enable ADB in the recovery menu
   (Advanced → Enable ADB) if `adb` shows the device as `unauthorized`.
4. Flash your own images again afterwards. The script overwrites `boot_a`,
   `dtbo_a` and `vendor_boot_a`.

## What to look for

```
KeyPress:0, BootReason:32
Fastboot=0, Recovery:0
Booting Into Mission Mode            <- normal boot (Recovery:1 means recovery mode)
Decompressing kernel image total time: 331 ms
ApplyOverlay: ufdt apply overlay failed
Error: Dtb overlay failed
Launching fastboot
```

Useful messages and what they meant on this device:

| Message | Cause |
| --- | --- |
| `Booting Into Recovery Mode` with `BootReason:34` | Android left a recovery request, see the traps in [abl-requirements.md](abl-requirements.md) |
| `DtboImgBuffer is NULL` | dtbo partition erased |
| `ufdt apply overlay failed` | main DTB lacks `__symbols__`/phandles for the hypervisor overlay |
| `Could not get splash memory region node` | `/reserved-memory/splash_region` missing |

## The DTB the ABL actually passed

From the LineageOS recovery, `/sys/firmware/fdt` holds the final DTB after
all overlays. Comparing it with the base DTB plus the board overlay shows what
the ABL and the hypervisor added on their own.

## Checking a DTB on the PC

`tools/check-dtb-overlays.sh` builds nothing and needs only `dtc` and the host
tool from AOSP libufdt:

```sh
git clone https://android.googlesource.com/platform/system/libufdt
cd libufdt
gcc -Iinclude -Isysdeps/include -I. ufdt_convert.c ufdt_node.c ufdt_node_pool.c \
    ufdt_overlay.c ufdt_prop_dict.c sysdeps/libufdt_sysdeps_posix.c \
    tests/src/ufdt_overlay_test_app.c tests/src/util.c -lfdt -o ufdt_apply_overlay
```
