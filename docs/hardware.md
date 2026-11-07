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
| Ultra-wide camera | Not yet | Sony IMX355, mainline driver exists |
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

- On some boots phoc's first modeset fails with
  `Atomic commit failed: Resource busy` and the screen stays black.
  Restarting the session (`systemctl restart greetd`) brings it back.
- The camera app (Snapshot) sometimes fails to start.
- libcamera has no sensor helper for the S5K5E9, so gain control is rough.
