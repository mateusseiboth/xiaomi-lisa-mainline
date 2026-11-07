# Building and flashing

**This erases all data on the phone.** Keep the official fastboot ROM for
your region around to go back to HyperOS (for global:
`lisa_global_images_OS2.0.8.0.UKOMIXM_..._14.0_global_4b5ed299cf.tgz` from
`cdnorg.d.miui.com`, MD5 `4b5ed299cf17b00d892e5f3a836ebfb8`).

The bootloader must be unlocked.

## Build

```sh
git clone https://gitlab.nura.eco/postmarketOS/pmaports.git
cd pmaports
git am /path/to/xiaomi-lisa-mainline/pmaports/patches/*.patch
cd ..
pmbootstrap init        # device: xiaomi-lisa, any UI
pmbootstrap install
pmbootstrap export out/
```

The patches apply on pmaports `d58ca1a2` (2026-11-07). The packages are also
available as plain directories under `pmaports/` in this repository.

## Flash

Enter fastboot with Power + Volume down (not `adb reboot bootloader` or
`reboot bootloader`, see the traps in [abl-requirements.md](abl-requirements.md)).

```sh
fastboot -w
pmbootstrap flasher flash_vbmeta     # verification disabled
pmbootstrap flasher flash_dtbo       # no-op overlay the ABL needs
pmbootstrap flasher flash_kernel     # boot + vendor_boot
pmbootstrap flasher flash_rootfs     # userdata
fastboot reboot
```

`pmbootstrap flasher boot` does not work on this device: the ABL ignores a
staged `vendor_boot`.

If a flash fails with `Requested download size is more than max allowed`,
re-enter fastboot with the buttons and use `fastboot -S 256M flash ...`.

## Updating without wiping

Kernel and device package updates do not need a new rootfs. Install the new
packages on the phone with `apk add`, then flash only `boot` and
`vendor_boot` from `/boot` of the rootfs (or the `pmbootstrap export` output
of a rootfs chroot with the same UUIDs).
