# firmware-skills ESP32 家族 Phase 2 扩容边界评审

评审日期：2026-09-02

本文对齐 `../rust-skills/PHASE-2-EVALUATION.md` 的角色：在 20 技能基线落定后，评审 **ESP32 家族技能（实际落地的全部 9 个 esp32-\*）** 是否满足扩容门禁，并对**未收入**的候选技能给出初评。所有结论基于实读各 `skills/esp32-*/SKILL.md`（frontmatter 与 Hand-off 路由）与 `evaluation/scenarios/scenarios.esp32-*.json`，场景证据逐项标注 id，不做无证据判断。基线锚点：ESP-IDF v6.1（`evaluation/baseline-espidf.md`，走读 2026-09-02）、OpenWrt 25.12.5、ophub `c593d56`。

## 决策摘要

| # | 技能 | 可区分的触发描述 | ≥2 场景（含 1 handoff/refusal） | 结论 |
|---:|---|---|---|---|
| 1 | `esp32-idf` | 是 | 3 条：handoff `esp32-idf-02` | Approve |
| 2 | `esp32-freertos` | 是 | 3 条：handoff `esp32-freertos-01`，refusal `esp32-freertos-01/-02` | Approve |
| 3 | `esp32-variants` | 是 | 3 条：handoff `esp32-variants-01`，refusal `esp32-variants-02` | Approve |
| 4 | `esp32-peripherals` | 是 | 3 条：refusal `esp32-peripherals-01`，handoff `esp32-peripherals-03` | Approve |
| 5 | `esp32-wifi-provision` | 是 | 3 条：refusal `esp32-wifi-provision-03`（无跨技能 handoff 场景，见备注） | Approve |
| 6 | `esp32-ota` | 是 | 3 条：refusal + handoff `esp32-ota-03` | Approve |
| 7 | `esp32-lowpower` | 是 | 3 条：refusal `esp32-lowpower-02`，handoff `esp32-lowpower-01/-02` | Approve |
| 8 | `esp32-secureboot` | 是 | 3 条：refusal `esp32-secureboot-01`，handoff 断言 `esp32-secureboot-02` | Approve |
| 9 | `esp32-debug` | 是 | 3 条：handoff `esp32-debug-02`，refusal `esp32-debug-03` | Approve |

**摘要：9 Approve / 0 Conditional / 0 Defer；候选池 7 项（2 Conditional、5 Defer）。**

"Approve" 仅指**扩容边界门禁通过**（触发可区分 + 场景达标）。Go/No-Go G5（可执行 golden example）当前全仓 Pending（见 `TRACE-REPORT.md` 遗留待办），不阻断扩容结论，但阻断发布。

## 逐技能门禁证据

### 1. `esp32-idf` — Approve

- **触发可区分**：description 收口 `idf.py` 工作流、sdkconfig、分区表、组件管理器、v5→v6 迁移，并显式路由 8 个兄弟技能（"Route task/concurrency design to esp32-freertos, pin-level drivers to esp32-peripherals, chip selection to esp32-variants, and OTA, secure boot, Wi-Fi provisioning, low power, and crash debugging to their dedicated esp32-\* skills"）。
- **场景证据**（`scenarios.esp32-idf.json`）：`esp32-idf-01` v5.2→v6 编译报错迁移（含"不凭记忆断言被移除 API 清单"反幻觉断言）；`esp32-idf-02` handoff——只交付分区表骨架、"实施显式移交 esp32-ota"、"不直接产出完整 OTA 实现代码"；`esp32-idf-03` 从零建工程烧写。

### 2. `esp32-freertos` — Approve

- **触发可区分**：收口 IDF FreeRTOS 变体专属事实（栈单位为字节、`CONFIG_FREERTOS_MAX_PRIORITIES=25` 可配、`xTaskCreatePinnedToCore`/SMP、portMUX），与 esp32-idf（工程/sdkconfig）、esp32-debug（崩溃）互斥路由。
- **场景证据**（`scenarios.esp32-freertos.json`）：`esp32-freertos-01` refusal——拒绝拍脑袋给"安全栈数值"，且断言含"崩溃现场取证显式移交 esp32-debug（handoff）"；`esp32-freertos-02` refusal——纠正 `vTaskSuspendAll` 不能当双核互斥；`esp32-freertos-03` SMP 绑核重分配（无硬件证据标 Build Verification Only）。
- **备注（轻微，不阻断）**：`esp32-freertos-01` 断言要求移交 esp32-debug，但 `expected_skills` 未列 `esp32-debug`；建议 forward-test 前补齐，避免评分口径不一致。

### 3. `esp32-variants` — Approve

- **触发可区分**：唯一收口芯片选型（架构/核数/无线能力矩阵 + 决策树），并显式声明"不写死各芯片最低 IDF 版本（UNVERIFIED）"。
- **场景证据**（`scenarios.esp32-variants.json`）：`esp32-variants-01` C6/H2 三无线过滤选型，断言含"芯片确定后移交 esp32-idf（handoff 语义）"；`esp32-variants-02` refusal——拒绝"直接告诉我个准数"的最低 IDF 版本，给三步运行时核验法；`esp32-variants-03` 纠正 P4 无片上射频高频错误点。

### 4. `esp32-peripherals` — Approve

- **触发可区分**：收口引脚级外设驱动选型与接线契约，反幻觉红线（"REFUSES to quote default pin numbers for a chip from memory"）写进 description。
- **场景证据**（`scenarios.esp32-peripherals.json`）：`esp32-peripherals-01` refusal——拒绝编造"C3 的 I2C 默认引脚号"，给 datasheet/原理图核验路径；`esp32-peripherals-02` v6.x 新式 `driver/i2c_master.h`（2026-09-02 官方 stable 核验）；`esp32-peripherals-03` handoff——legacy ADC 移除根因定位后，"工程层面迁移策略移交 esp32-idf"。

### 5. `esp32-wifi-provision` — Approve

- **触发可区分**：唯一收口配网（四种官方方式、Security 0/1/2、状态机、NVS 持久化），并路由 esp32-ota（升级通道）与 esp32-variants（无无线芯片）。
- **场景证据**（`scenarios.esp32-wifi-provision.json`）：`esp32-wifi-provision-01` 选型对比（默认推荐 Unified Provisioning + Security 2，告知 SmartConfig 为 legacy）；`esp32-wifi-provision-02` BLE + Security 2 全流程实施；`esp32-wifi-provision-03` refusal——拒绝"把 SSID/密码写死固件"，不给任何写死凭据的实现示例。
- **备注（轻微，不阻断）**：三条场景均为技能内闭环，无跨技能 handoff 断言；refusal 已满足门禁。建议 forward-test 后补一个"OTA 升级 vs 配网"分流场景验证 description 路由不误触发。

### 6. `esp32-ota` — Approve

- **触发可区分**：收口 OTA 双槽 + otadata、镜像状态机、回滚语义、esp_https_ota，并显式排除离线烧录（→esp32-idf）、eFuse 防回滚（→esp32-secureboot）、崩溃定位（→esp32-debug）。
- **场景证据**（`scenarios.esp32-ota.json`）：`esp32-ota-01` 回滚全流程（拒绝编造分区偏移，Offset 留空自动排布；断电回滚验收标 Pending HIL）；`esp32-ota-02` "升级成功却跑旧版"排查（PENDING_VERIFY 未确认）；`esp32-ota-03` refusal + handoff——拒绝"离线也能 OTA"前提，USB 串口烧录路由 esp32-idf，不编造任何离线 OTA 机制。

### 7. `esp32-lowpower` — Approve

- **触发可区分**：唯一收口睡眠策略（light/deep、六类唤醒源、ULP 分布、RTC 内存 vs NVS），并把"拒绝凭记忆报深睡 µA 数值"写进 description（基线 UNVERIFIED）。
- **场景证据**（`scenarios.esp32-lowpower.json`）：`esp32-lowpower-01` 深睡 + RTC timer/EXT0 组合策略，断言含"拒绝给深睡 µA 具体数字"与"真机验收路由 fw-hil-testing（handoff）"；`esp32-lowpower-02` refusal——拒绝按转述的 10µA 算续航，给功率计实测方法；`esp32-lowpower-03` UART 唤醒标 UNVERIFIED 不凭记忆作答。

### 8. `esp32-secureboot` — Approve

- **触发可区分**：唯一收口 SBv2 + Flash Encryption + 密钥治理，并把"拒绝签名私钥进 git/CI、不断言 ED25519（UNVERIFIED）"写进 description。
- **场景证据**（`scenarios.esp32-secureboot.json`）：`esp32-secureboot-01` refusal——拒绝"私钥提交 git 仓库"，给构建/签名分离治理方案与已泄露处置；`esp32-secureboot-02` 量产启用顺序，断言含"OTA 通道就绪确认（→esp32-ota）"与"发布制品走 fw-release-gate 门禁"（handoff 断言）；`esp32-secureboot-03` 纠正"开发模式无限刷机"误区（≤3 次明文烧录）。

### 9. `esp32-debug` — Approve

- **触发可区分**：唯一收口崩溃/复位调试（调试手段矩阵、panic 回溯→coredump 流程、复位原因分类），并显式声明"经典 ESP32 无内置 USB-Serial/JTAG、不支持 SWD"。
- **场景证据**（`scenarios.esp32-debug.json`）：`esp32-debug-01` 随机重启三分类决策树 + 补 coredump 配置；`esp32-debug-02` handoff——软件证据穷尽后"hand-off fw-hil-testing：真机在环电源测量验证供电嫌疑"，不给无实测定论；`esp32-debug-03` refusal——纠正"SWD 连 ESP32"误区，接线与 TCK 频率不编造。

## 候选池（未收入技能初评）

对齐 rust-skills 的边界哲学：**不要"一个包一个技能"**。一个包属于已有技能，当它实现的是同一个工程决策与验证契约；只有拥有独立任务边界时才新立技能。

| 候选 | 初评 | 理由 |
|---|---|---|
| `esp32-ulp` 专项 | Defer | ULP 已由 `esp32-lowpower` 收口（`references/sleep-modes.md`、`wakeup-sources.md` 覆盖 ULP-FSM / RISC-V ULP / LP 核分布与唤醒源）。ULP 程序开发是低功耗边界内的实现细节；单独立技能即"一个外设一个技能"反模式。等真实需求出现且 lowpower 的 references（≤120 行/文件）装不下时再议，届时以"ULP 程序生命周期"为任务边界而非"ULP 介绍"。 |
| `esp32-matter` | Defer | 全仓零覆盖（grep 无 Matter 命中）。但 Matter/Thread 协议栈依赖 esp-matter + connectedhomeip，版本与 IDF 匹配矩阵在当前基线（`baseline-espidf.md`）中 UNVERIFIED；`esp32-variants-01` 已显式把"Matter/Thread 协议栈实现"划出选型边界。晋级 Conditional 的前提：完成 esp-matter dated 基线走读 + 一个可复现的 C6 commissioning golden example（锁定 esp-matter 版本）。 |
| `esp32-coredump` 深化 | Defer | coredump 提取/符号化已由 `esp32-debug` 收口（`references/crash-triage.md`，`idf.py coredump-info/coredump-debug`）。深化项（coredump 分区容量规划、GDB 自动化脚本）是 esp32-debug 的 reference 增量，不构成独立任务边界；新立技能会造成同一崩溃取证流程被两个技能瓜分。 |
| `esp32-ble`（GATT 应用开发） | Conditional | 现有 9 个 esp32-\* 均未收口 BLE GATT server/client 应用开发（配网技能只覆盖 provisioning 传输层的 BLE 用法）。这是一个真实且独立的任务边界（NimBLE vs Bluedroid 选型、GATT 服务表、MTU/连接参数）。Conditional 前提：NimBLE dated 基线走读（IDF v6.1 下 Bluedroid 去留为高频变化点）、≥2 场景含 1 handoff（配网传输层用法仍路由 esp32-wifi-provision）、不做"一个 profile 一个技能"。 |
| `openwrt-wireless` | Conditional | 现有 6 个 OpenWrt 技能 grep 无 wireless/hostapd/wpad 覆盖——真实真空带。Wi-Fi（AP/STA、`/etc/config/wireless`、wpad）是网关固件高频任务边界，与 uci-defaults（首启机制）、image-build（构建期注入）可区分。Conditional 前提：OpenWrt 25.12.5 wireless 文档 dated 走读；≥2 场景含 1 handoff（首启预置路由 openwrt-uci-defaults）；驱动/芯片专属细节沉 references，不做"一驱动一技能"。 |
| `openwrt-uhttpd-cgi` 专项 | Defer | uHTTPd 已由 `openwrt-uci-defaults` 收口（description 声明 docroot/cgi_prefix/rfc1918_filter 等 + `references/uhttpd-config.md`）。为单包立技能即"一个包一个技能"反模式。若 LAN web 服务需求膨胀，正确边界是"openwrt-web-services（uHTTPd + CGI + LuCI 定制）"这类任务边界聚合，而非单包技能。 |
| `openwrt-firewall` 深化 | Defer | 当前 fw-core 路由表把"防火墙"指给 `openwrt-uci-defaults`，后者覆盖 lan-zone 默认可达性（`firewall.config` lan 区 input ACCEPT）。流量策略级的 fw4/nftables 规则集是潜在增量，但当前无场景证据表明 uci-defaults 收口不足；先在 uci-defaults 内以 reference 增量扩容，装不下再按任务边界新立。 |

## Go/No-Go 门禁清单

一个 esp32-\*（或候选）技能可以进入本包，仅当全部满足：

1. **触发可区分**：description 的 "Use when" 触发词与全部既有技能（含 fw-core 路由表逐行）不重叠，且显式声明路由/拒答边界——在该触发时唯一命中，不误触发兄弟技能。
2. **决策而非 API**：工作流围绕工程决策组织（如"选哪种睡眠/哪个槽/哪级安全方案"），芯片/包/协议专属细节沉入 references（单文件 ≤120 行），不堆 API 清单。
3. **日期化基线**：版本、命令、参数带"截至 2026-09-02"口径；UNVERIFIED 事实（各芯片最低 IDF 版本、ED25519、深睡 µA 数值等）不得写死，必须给运行时核验路径。
4. **≥2 forward-test 场景**，其中 ≥1 个 handoff 或 refusal 场景，断言可机器判定；`expected_skills` 与断言口径一致。
5. **≥1 个可执行 golden example**：锁定工具链/组件版本、可离线复现（ESP-IDF 侧为 `idf.py` 构建，OpenWrt 侧为 QEMU 冒烟）——**当前全仓 Pending**（见 `TRACE-REPORT.md` 遗留待办），是发布前唯一未闭合的门禁。
6. **诚实性红线**：无硬件证据的能力标 `Build Verification Only` / `Pending HIL`；禁止伪造"已在硬件上验证"；破坏性操作（写 eMMC/烧 flash）前必须确认目标盘符。
7. **任务边界唯一**：不做"一个包/一个外设/一个协议一个技能"；新增能力优先以现有技能的 reference 增量扩容，只有拥有独立工程决策与验证契约时才新立技能。

## 与发布的关系

扩容门禁（本表）与发布门禁（`TRACE-REPORT.md` 三层证据）相互独立：本评审通过仅说明 **20 技能的边界划分成立**；发布还需闭合 G5 golden example 执行与 forward-test run。候选池中两个 Conditional（`esp32-ble`、`openwrt-wireless`）建议作为下一扩容批次的优先项，且须在 golden example 基础设施就绪后启动，避免再造一批"只有文档没有可执行证据"的技能。
