# firmware-skills

**Verifiable, on-demand embedded firmware Agent Skills** — two families: OpenWrt (embedded-Linux gateway firmware) and ESP32 (MCU firmware), plus cross-cutting toolchain/emulation/HIL and a release gate.

[English](./README.md) | 简体中文

See [README.zh-CN.md](README.zh-CN.md) for the full skill inventory, routing DAG, install commands, and dated offline baselines. Authoring rules: [docs/CONVENTIONS.md](docs/CONVENTIONS.md).

## Skill inventory (20)

`fw-core` · OpenWrt: `openwrt-image-build` `openwrt-amlogic-remake` `openwrt-procd-init` `openwrt-uci-defaults` `openwrt-storage-mount` `openwrt-serial-recovery` · ESP32: `esp32-idf` `esp32-freertos` `esp32-peripherals` `esp32-wifi-provision` `esp32-ota` `esp32-lowpower` `esp32-secureboot` `esp32-debug` `esp32-variants` · Cross-cutting: `fw-toolchain` `fw-emulation` `fw-hil-testing` · Gate: `fw-release-gate`

## Install

```bash
npx skills add full-stack-skills/firmware-skills --list   # list only
npx skills add full-stack-skills/firmware-skills          # interactive
```

## Offline baselines (dated, not auto-updated)

OpenWrt 25.12.5 (walkthrough 2026-09-02) · ophub upstream `c593d56` (N1 board id `s905d`, kernel 6.12.y) · ESP-IDF locked per `evaluation/baseline-espidf.md`.

## License

Apache-2.0
