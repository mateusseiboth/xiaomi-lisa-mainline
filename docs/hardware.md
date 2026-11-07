# Hardware status

Kernel 7.2.9 (`linux-postmarketos-qcom-sc7280`) with the patches in
`pmaports/device/community/linux-postmarketos-qcom-sc7280`.

| Component | Status | Notes |
| --- | --- | --- |
| Boot from stock ABL | Works | see [abl-requirements.md](abl-requirements.md) |
| Display | Works | CSOT VTDR6130 AMOLED, DSI video mode, DSC. Driver from the mainlining fork |
| GPU | Works | Adreno 642L (`msm`), Mesa freedreno |
| Touchscreen | Works | Goodix Berlin (gt9897) over SPI |
| Wi-Fi, Bluetooth | Work | WCN6750 |
| Battery, charging | Work | pmic_glink / battmgr |
| Remoteprocs | Work | modem, ADSP, CDSP, WPSS |
| Speaker, earpiece | Work | two TFA9873 on PRIMARY_MI2S, q6asm/q6afe. No speaker protection calibration, avoid long loud playback |
| Microphones | Not yet | LPASS VA/TX macros not described |
| Macro camera | Works | Samsung S5K5E9YX04, 2584x1944 @ 30 fps through libcamera's soft ISP |
| Ultra-wide camera | Works | Sony IMX355, 1636x1232 @ 30 fps. Full resolution (3272x2464) resets the phone |
| Main camera | Not yet | Samsung S5KGW3 (64 MP), no mainline driver |
| Front camera | Not yet | Samsung S5K3T2 (20 MP), no mainline driver |
| Focus motor | Not yet | Dongwoon DW9800 (main and macro), no mainline driver |
| Calls, SMS, mobile data | Untested | |
| Fingerprint, haptics | Not yet | |

## Camera modules

From `vendor/lib64/camera` of the stock ROM:

| Camera | Sensor | Module makers |
| --- | --- | --- |
| Main (wide) | S5KGW3 | OFilm, SEMCO |
| Ultra-wide | IMX355 | OFilm |
| Macro | S5K5E9YX04 | OFilm, Sunny |
| Front | S5K3T2 | Sunny |

The `com.qti.sensormodule.*.bin` files carry the register tables (init and
modes) for each sensor.

## Known issues

- The first DSI bring-up after the bootloader hand-off leaves the panel dark
  and deaf to DCS commands. An initramfs hook cycles the panel once
  (`50-xiaomi-lisa-panel-cycle.sh`); a proper fix in the msm DSI hand-off is
  still to do.
- UPower shows the battery as discharging while charging (the firmware reports
  the charge current as negative).
- The camera app (Snapshot) sometimes fails to start.
- libcamera has no sensor helper for the S5K5E9, so gain control is rough.
