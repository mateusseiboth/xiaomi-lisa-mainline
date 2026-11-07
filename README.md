# Xiaomi 11 Lite 5G NE (lisa) on mainline Linux

Mainline Linux for the Xiaomi 11 Lite 5G NE / 11 LE (`lisa`, Snapdragon 778G
SM7325), booted straight from the **stock Xiaomi bootloader** (HyperOS 2),
without U-Boot or a custom UEFI. Packaged for
[Nura](https://nura.eco) (formerly postmarketOS).

Display, GPU, touch, Wi-Fi, Bluetooth, battery, speaker, earpiece and the
macro camera work. See [docs/hardware.md](docs/hardware.md).

## What is here

| Path | Content |
| --- | --- |
| [`pmaports/`](pmaports) | `device-xiaomi-lisa`, `firmware-xiaomi-lisa` and the `linux-postmarketos-qcom-sc7280` changes (kernel patches and config) |
| [`pmaports/patches/`](pmaports/patches) | The same changes as `git am` patches for pmaports |
| [`docs/abl-requirements.md`](docs/abl-requirements.md) | What the stock ABL requires from a mainline DTB and boot image |
| [`docs/debugging.md`](docs/debugging.md) | Reading the bootloader's own logs from the `logfs` partition |
| [`docs/flashing.md`](docs/flashing.md) | Building, flashing and updating |
| [`docs/hardware.md`](docs/hardware.md) | Hardware status and camera sensors |
| [`tools/`](tools) | UEFI log dump script, an offline DTB overlay check and a decoder for the CamX sensor module blobs |

## Why this was hard

The upstream DTS (merged into torvalds/master in late 2026) boots, but the stock ABL refuses it
without any message. Its logs showed five requirements, none documented before:
DTB ids, a `splash_region` node with the stock size, two nodes the ABL edits,
`__symbols__` for the overlay the Gunyah hypervisor injects, and a dtbo entry in
Xiaomi's format. Details in [docs/abl-requirements.md](docs/abl-requirements.md).

## Upstreaming

- Device and firmware packages: merge request to
  [pmaports](https://gitlab.nura.eco/postmarketOS/pmaports).
- Kernel patches: [sc7280-mainline/linux](https://github.com/sc7280-mainline/linux)
  and then the kernel mailing lists.

## Credits

- Oleksii Onchul: the upstream `sm7325-xiaomi-lisa` DTS.
- Jens Reidel and the [mainlining](https://github.com/mainlining) team: the
  original port, the CSOT VTDR6130 panel driver, the S5K5E9 driver and the
  firmware package.
- The Nothing Phone (1) (`nothing-spacewar`) port: same SoC and amplifiers,
  the reference for the audio setup.

## License

Kernel patches are GPL-2.0-only. Package recipes follow pmaports (MIT).
