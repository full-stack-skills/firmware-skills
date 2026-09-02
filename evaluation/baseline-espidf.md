# ESP-IDF 日期化基线（供 8 个 ESP32 技能作者引用）

> 日期化基线（抓取 2026-09-02）——技能作者引用本文时必须带本日期；不自动更新。
> 置信度：高 = 直接抓取官方文档/GitHub；中 = 官方页转述或搜索摘要，SKILL.md 引用前需复核；未抓到 = UNVERIFIED。

## 1. 当前版本与发布日期

- **最新 stable：v6.1**，GitHub 发布时间戳 2026-08-27（带 "Latest" 徽章，非 pre-release，官方描述为 "minor update for ESP-IDF v6.0"）。
- 上一个 stable 线：**v6.0.2**（2026-06-29）；最新 v5.x 维护版：**v5.5.5**（2026-07-17）。官方不用 "LTS" 一词，采用 30 个月支持期政策（12 个月 Service + 18 个月 Maintenance）。
- 当前受支持版本（搜索摘要转述）：v6.1、v6.0.2、v5.5.5、v5.4.4、v5.3.5、v5.2.7。
- 来源：https://github.com/espressif/esp-idf/releases 、https://github.com/espressif/esp-idf/releases/tag/v6.1 、https://docs.espressif.com/projects/esp-idf/en/stable/esp32/versions.html ｜ 置信度：高（受支持版本清单为中）
- 注意：v6.0 移除了大量旧版驱动（legacy ADC/I2S/Timer 等）；v6.1 将 esp-mqtt 移入组件管理器（需 `espressif/mqtt` 依赖）。

## 2. 芯片矩阵（架构 / 无线能力）

| 芯片 | 架构（官方页原文） | 无线 | 来源置信度 |
|---|---|---|---|
| ESP32 | 双核 Xtensa LX6 240 MHz | Wi-Fi 2.4 GHz + Bluetooth（含 Classic+BLE，官方 get-started 未细分版本号） | 高 |
| ESP32-S2 | 单核 Xtensa LX7 240 MHz | 仅 Wi-Fi 2.4 GHz，**无蓝牙** | 高 |
| ESP32-S3 | 双核 Xtensa LX7 240 MHz | Wi-Fi 2.4 GHz + 仅 BLE（无 Classic） | 高 |
| ESP32-C3 | 单核 RISC-V 160 MHz | Wi-Fi 2.4 GHz + 仅 BLE | 高 |
| ESP32-C6 | 单核 RISC-V 160 MHz（另有 LP 核 20 MHz） | Wi-Fi 6 (802.11ax) + BLE 5 + IEEE 802.15.4（Thread/Zigbee） | 高 |
| ESP32-H2 | 单核 RISC-V 96 MHz | **无 Wi-Fi**；BLE 5 + 802.15.4（Thread 1.3 / Zigbee 认证） | 高 |
| ESP32-P4 | 双核 RISC-V 400 MHz + LP-Core 40 MHz | **无片上射频**；经 ESP-Hosted/ESP-AT 用 C/S 系列作伴生芯片 | 高 |
| ESP32-C5 | 单核 RISC-V 240 MHz | 双频 Wi-Fi + BLE（v6.1 release notes 提及；细节未抓取） | 中 |
| ESP32-S31 | 双核 RISC-V 320 MHz | v6.1 新增 preview 支持（release notes） | 中 |

- 架构来源：https://www.espressif.com/en/products/socs ｜ 无线来源：各芯片页（c6/h2/p4）及 docs 各 get-started 页（esp32/s2/s3/c3）。
- **各芯片最低 IDF 版本：UNVERIFIED**——未找到官方合并对照表；技能中不得写死"最低 vX.Y"，需运行时核验。

## 3. idf.py 核心工作流

- 标准顺序：`idf.py create-project <name>` → `idf.py set-target <target>`（清 build、重生成 sdkconfig；默认 target 为 esp32）→ `idf.py menuconfig` → `idf.py build` → `idf.py flash -p PORT`（-p 或环境变量 ESPPORT）→ `idf.py monitor`；可链式如 `idf.py -p PORT flash monitor`，执行顺序由 idf.py 自动保证。
- idf.py 是 CMake+Ninja+esptool 的前端；必须运行在含 CMakeLists.txt 的项目目录内。
- VS Code 官方插件存在：github.com/espressif/vscode-esp-idf-extension，支持 build/flash(UART/DFU/JTAG)/monitor/debug（含 coredump 与 GDB stub 事后调试）。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/tools/idf-py.html 、https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/index.html ｜ 置信度：高

## 4. 分区表机制

- CSV 位于 0x8000（默认），格式 `# Name, Type, SubType, Offset, Size, Flags`；最多 95 项 + MD5 校验；Offset 空 = 自动排布；app 分区须 64KB 对齐，数据分区 4KB 对齐。
- Type：`app`/`data`/`bootloader`/`partition_table`；app SubType：`factory`、`ota_0`(0x10)~`ota_15`(0x1F)、`test`；data SubType：`nvs`、`phy`、`ota`(otadata)、`coredump`、`fat`、`spiffs` 等。
- **OTA 双分区布局**：factory + ota_0 + ota_1 + otadata（0x2000）；bootloader 按 otadata 的 ota_seq 选择启动槽，otadata 为空则启动 factory。menuconfig 预设："Single factory app, no OTA" / "Factory app, two OTA definitions"。
- 命令：`idf.py partition-table`（打印）、`partition-table-flash`；CSV↔bin 由 gen_esp32part.py 转换；构建时校验镜像必须放进某个 app 分区。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/partition-tables.html ｜ 置信度：高

## 5. OTA 机制要点

- OTA 需要 **至少两个 OTA app 槽（ota_0/ota_1）+ otadata 分区**；新固件写入非活动槽，校验通过后才改 otadata。
- 原生流程：`esp_ota_begin`（可传 OTA_SIZE_UNKNOWN）→ `esp_ota_write`（分块循环）→ `esp_ota_end`（校验镜像）→ `esp_ota_set_boot_partition`；`esp_ota_get_next_update_partition()` 轮转选槽。
- 有效性状态存于 **otadata**（非镜像内）：VALID/UNDEFINED 可启动；INVALID/ABORTED 不启动；NEW→PENDING_VERIFY→（确认）VALID 或（失败）ABORTED 回滚。
- **CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE**：新 app 首启置 PENDING_VERIFY，应用须自检后调 `esp_ota_mark_app_valid_cancel_rollback()` 或 `esp_ota_mark_app_invalid_rollback_and_reboot()`；未确认即重启则回滚旧版。仅 OTA 槽可回滚，factory 不可。
- 防回滚：CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK（secure_version 烧 eFuse，仅可递增）。
- 高层封装 **esp_https_ota**（esp_https_ota_config_t；bulk_flash_erase、buffer_size 等调优项）。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/ota.html ｜ 置信度：高

## 6. Secure Boot v2 与 Flash Encryption

- **SBv2 签名方案**：ESP32（rev 3.0+）与 ESP32-C3 官方页均只描述 **RSA-3072（RSA-PSS）**；ECDSA SBv2 存在于部分芯片（v6.1 release notes：因漏洞对 H2/C5/P4 禁用 ECDSA SBV2，可间接证明这些芯片支持 ECDSA）；**ED25519：UNVERIFIED**。
- 公钥 **SHA-256 摘要烧入 eFuse**（ESP32: BLK2；C3: BLOCK_KEY0-5 + KEY_PURPOSE=SECURE_BOOT_DIGESTX）；须写保护但**不可读保护**（软件校验需读取，读保护会导致无法启动）。私钥永不进设备。
- 槽数：ESP32 仅 1 个；C3 最多 3 个（KEY_REVOKEX 撤销，不可逆；支持保守/激进撤销策略）。
- **Flash Encryption**：AES-256（硬件引擎）；密钥存 eFuse block1，烧录后写+读保护，**软件不可读回**；Development 模式明文串口烧录 ≤3 次（FLASH_CRYPT_CNT 计数）；Release 模式烧保护位后无法再明文烧录，新镜像只能经 OTA。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/security/secure-boot-v2.html 、…/esp32c3/security/secure-boot-v2.html 、…/esp32/security/flash-encryption.html 、https://github.com/espressif/esp-idf/releases/tag/v6.1 ｜ 置信度：高（ECDSA/ED25519 归属为中）

## 7. Wi-Fi 配网方式清单

- IDF 官方配网索引列出 4 种方法：**Unified Provisioning**、**SmartConfig**、**Wi-Fi Easy Connect (DPP)**、底层 **protocomm**。
- Unified Provisioning：传输层 **SoftAP(+HTTP)** 与 **BLE(GATT)**；基于 protocomm（安全方案与传输的底座）；安全方案 Security 0（无加密）/ Security 1（Curve25519 + AES-256-CTR，可带 PoP）/ Security 2（SRP6a + AES-256-GCM，推荐）；BLE 传输约需 110KB RAM；配套 iOS/Android App（ESP BLE Provisioning / ESP SoftAP Provisioning）。
- 组件：现行组件 `network_provisioning`（registry/GitHub 示例）；旧组件 `wifi_provisioning`（v5.5 文档仍在）。凭证由 Wi-Fi 驱动持久化（NVS）——未在抓取页直接确认，标运行时核验。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/provisioning/index.html 、…/provisioning/provisioning.html ｜ 置信度：高（NVS 持久化为中）

## 8. 低功耗模式事实

- 两大模式：**Light-sleep**（时钟门控、状态保持、无线断电）与 **Deep-sleep**（CPU/大部分 RAM/数字外设断电，仅 RTC 控制器、ULP、RTC FAST/SLOW 内存供电）。
- 深睡唤醒源（ESP32 页）：RTC Timer（µs 精度）、Touch、EXT0（单 RTC GPIO）、EXT1（多 RTC GPIO，S2/S3/C6/H2 额外支持 ANY_LOW）、**ULP 协处理器**、deepsleep GPIO wake 等；可组合。
- 深睡电流为 **µA 数量级**（官方页仅给 SPI Flash 待机 <30µA / Deep Power-Down <1µA；"10µA 典型 / ULP 运行 ~150µA" 出自数据手册搜索转述，未直接抓取 PDF）——具体数值标运行时核验。
- ULP 类型：ESP32 为 ULP-FSM（技术参考手册描述其 FSM ULP）；S2/S3 的 ULP 可为 RISC-V 或 FSM 核（官方 get-started 原文）；C6/P4 为 LP 核（20/40 MHz，官方页）。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/sleep_modes.html ｜ 置信度：高（µA 具体数值为中）

## 9. 组件管理器

- **存在且为官方推荐**：组件注册表 https://components.espressif.com ；`idf.py add-dependency <ns/name=ver>` 写入 `idf_component.yml`；依赖递归解析后下载到 **managed_components/**（勿手改）；生成 **dependencies.lock**（损坏可用 `idf.py reconfigure` 恢复）；也支持 Git 来源。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/tools/idf-component-manager.html ｜ 置信度：高

## 10. 调试手段

- **JTAG/OpenOCD**：OpenOCD 随 IDF 安装（`openocd -f board/xxx.cfg`）；ESP32 无内置 USB-Serial/JTAG（需外部适配器如 ESP-Prog，不支持 SWD）；支持经 JTAG 烧录（program_esp）与 GDB（xtensa-esp32-elf-gdb）。
- **Core dump**：panic 时自动保存；目的地为 **flash（data/coredump 分区）或 UART**（CONFIG_ESP_COREDUMP_TO_FLASH_OR_UART）；用 `idf.py coredump-info` / `coredump-debug`（封装 esp-coredump 工具）分析。
- **GDB stub**：存在运行时 GDB stub（CONFIG_ESP_SYSTEM_GDBSTUB_RUNTIME，官方 JTAG 页提及）——无需 JTAG 串口调试；专用文档页 URL 未抓到（UNVERIFIED）。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/jtag-debugging/index.html 、…/api-guides/core_dump.html ｜ 置信度：高

## 11. FreeRTOS 变体事实

- IDF 自带 **IDF FreeRTOS**：基于 **Vanilla FreeRTOS v10.5.1** 修改的内核（官方原文），非上游原版。
- **SMP**：双核目标为 ESP32、ESP32-S3、ESP32-P4、ESP32-H4（Core 0=PRO_CPU / Core 1=APP_CPU）；S2/C3 等单核恒为 unicore（CONFIG_FREERTOS_UNICORE）。覆盖 Xtensa（ESP32/S3）与 RISC-V（P4）两种架构。
- 关键差异：`xTaskCreatePinnedToCore()` 核心亲和；**栈大小单位为字节**（上游为字）；每核独立调度器与 idle 任务；临界区用 portMUX 自旋锁；vTaskSuspendAll 仅挂起当前核（不能当互斥用）。
- 优先级范围：默认 `CONFIG_FREERTOS_MAX_PRIORITIES = 25`（有效 0–24，数字越大越高；idle=0）——来自官方仓库 issue 与社区一致结论，官方页未直接写明，**引用时标注"默认 25，可配，运行时以 sdkconfig 为准"**。
- 来源：https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/system/freertos_idf.html 、https://github.com/espressif/esp-idf/issues/13041 ｜ 置信度：高（优先级默认值为中）

---

## 技能作者注意事项

1. **可直接写入 SKILL.md（高置信、稳定）**：idf.py 命令序列；分区表 CSV 字段与 factory/ota_0/ota_1/otadata 语义；OTA begin/write/end 流程与 rollback Kconfig 名称及 esp_ota_mark_app_* API；SBv2 密钥摘要入 eFuse、不可读回、私钥不出设备；Flash Encryption 3 次明文烧录限制；组件管理器三件套（idf_component.yml / managed_components / dependencies.lock）；配网 Security 0/1/2 与 SoftAP/BLE 传输；FreeRTOS 栈单位为字节、xTaskCreatePinnedToCore。
2. **必须带"运行时核验"标注**：具体版本号（v6.1/v6.0.2/v5.5.5 等——引用时必须注明"截至 2026-09-02"）；CONFIG_FREERTOS_MAX_PRIORITIES 默认 25；深睡 µA 具体数值（10/150µA）；NVS 保存配网凭证；gdbstub 专用文档 URL。
3. **禁止写入（UNVERIFIED）**：各芯片最低 IDF 版本号；ED25519 Secure Boot 方案归属；C5/S31 无线细节细节级描述。
4. 芯片矩阵中 P4 无射频、H2 无 Wi-Fi、S2 无蓝牙是高频错误点，技能中应显式提示。
5. 所有文档链接建议使用 `/en/stable/` 前缀；v6.x 相对 v5.x 有破坏性变更（旧驱动移除、esp-mqtt 转组件管理器），技能示例应避免依赖已移除的 legacy API。
