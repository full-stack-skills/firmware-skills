# firmware-skills 评测与验证基线（TRACE 三层证据）

基线日期：2026-09-02

插件版本：0.1.0

基线锚点（dated，不自动更新，引用须带本日期）：

- **OpenWrt = 25.12.5**（上游走读 2026-09-02）
- **ophub/amlogic-s9xxx-openwrt = 上游 HEAD `c593d56`**
- **ESP-IDF = v6.1**（GitHub 发布 2026-08-27，见 `evaluation/baseline-espidf.md`，抓取 2026-09-02）

## 评测定位

对齐 `../rust-skills/TRACE-REPORT.md` 的三层证据结构，把质量证据拆成三个可重复验证的层次：

1. **结构与规范**：由 `scripts/validate_skills.py` 自动检查（frontmatter、清单一致性、行数上限、相对链接、围栏配对、场景 schema）。
2. **行为证据**：golden example 在真实工具链上的执行记录（构建/启动冒烟）。
3. **触发与交接**：由 `evaluation/scenarios.json` 保存独立 Agent forward-test 输入与断言。

## 第一层：结构校验（已执行）

执行命令与真实输出摘要（2026-09-02，无删改）：

```bash
python3 scripts/validate_skills.py            # 严格模式
python3 scripts/validate_skills.py --lenient  # 分阶段模式
```

| 模式 | 结果 | 摘要行（原文） |
|---|---|---|
| strict（默认） | 通过，退出码 0 | `== 摘要: 已落地 20/20 技能, 0 error, 0 warn, 模式=strict ==` |
| --lenient | 通过，退出码 0 | `== 摘要: 已落地 20/20 技能, 0 error, 0 warn, 模式=lenient ==` |

覆盖明细（两模式一致）：

- 清单/目录一致性：`.claude-plugin/plugin.json` 20 项 ↔ `skills/*` 20 目录，双向一致。
- 全部 20 个 SKILL.md：frontmatter name/description 齐备、name == 目录名、行数 89–179 行（最长 `openwrt-image-build` 179 行，上限 500）。
- 全部 47 个 references/\*.md：行数 ≤ 85 行（最长 `fw-release-gate/references/release-checklist.md`，上限 120）。
- Markdown 相对链接与代码围栏配对：0 error。
- 场景 schema：20 个 `scenarios.*.json` 全部通过；每技能 ≥2 条，无 warn。

严格模式无 error，无因校验产生的待办。

## 第二层：行为证据（3 个黄金示例已执行，2026-09-02）

**已执行（3/20 技能覆盖，其余 17 个待补——诚实声明，见文末待办）**：

| GE | 技能 | 内容 | 徽章 | 证据位置 |
|---|---|---|---|---|
| GE-1 | `fw-emulation` | 官方 OpenWrt 25.12.5 armsr combined-efi 镜像在 Docker 内 QEMU（aarch64/TCG+QEMU_EFI）完整启动至 `br-lan forwarding`（t≈40s），31KB 启动日志，sha256 预校验 | `B1 Boot Verified (QEMU)` | `skills/fw-emulation/examples/ge-openwrt-qemu-boot/`（boot-log.txt + README） |
| GE-2 | `openwrt-image-build` | IB（armsr/armv8 25.12.5）`make image PROFILE=generic PACKAGES= FILES=` 实跑：**FILES= 覆盖合并**（marker 落入 rootfs）与 **init.d rc.common 自动 enable**（`/etc/rc.d/S99golden-boot`）双双实证；**关键发现：armsr IB 默认产出 `*-rootfs.tar.gz`**（ophub 链路输入天然存在） | `Build Verified` + 注入语义端到端 | `skills/openwrt-image-build/examples/ge-ib-files-overlay/`（build-log / artifacts-list / injection-verify + README） |
| GE-3 | `esp32-idf` | ESP-IDF **v6.1**（tag 浅克隆）+ `./install.sh esp32c3` + hello_world `idf.py build`：`Project build complete`，`hello_world.bin` 126,688B（88% free），sha256 存档，esptool v5.4.0 | `B0 Build Verification Only` | `skills/esp32-idf/examples/ge-idf-hello-build/`（evidence.txt + build-full-log.txt + README） |

**踩坑实录（已回写技能演进素材）**：Docker Desktop macOS 的 host bind mount 大小写不敏感 → OpenWrt 构建必须用**命名卷**；apt 安装与执行必须在同一 `docker run`；验证 rootfs 内容优先 `rootfs.tar.gz` 直读而非 debugfs 读未解压 `.img.gz`。

**仍然 Pending（不粉饰）**：真实硬件上的 flash + 上电运行（`HIL Verified` 徽章路径，ESP32 烧录与 Amlogic 盒子串口均待硬件）；其余 17 个技能的 examples 待按此三例的模板补齐。场景断言中出现的"Build Verification Only / Pending HIL"标注规范（CONVENTIONS §5）现已有本仓产物实例佐证。

## 第三层：forward-test（已执行第一轮，2026-09-02）

**输入**：`evaluation/scenarios.json`（本报告同日生成），顶层 `{version: 0.1.0, generated: 2026-09-02, count: 65}`，65 条场景覆盖全部 20 个技能，由 `scripts/merge_scenarios.py` 合并（按技能名字典序、按 id 去重、`--check` 可复核一致性）。

**每技能覆盖数表**（全部 ≥2，达标 20/20；handoff/refusal 逐条实读场景文件归类）：

| 技能 | 场景数 | ≥2 | handoff 场景 | refusal 场景 |
|---|---:|:-:|---|---|
| esp32-debug | 3 | ✓ | -02（→fw-hil-testing） | -03 |
| esp32-freertos | 3 | ✓ | -01（断言移交 esp32-debug） | -01、-02 |
| esp32-idf | 3 | ✓ | -02（→esp32-ota） | -02 |
| esp32-lowpower | 3 | ✓ | -01、-02（→fw-hil-testing） | -01、-02 |
| esp32-ota | 3 | ✓ | -03（→esp32-idf） | -03 |
| esp32-peripherals | 3 | ✓ | -03（→esp32-idf） | -01 |
| esp32-secureboot | 3 | ✓ | -02（断言 →esp32-ota / fw-release-gate） | -01 |
| esp32-variants | 3 | ✓ | -01（断言移交 esp32-idf） | -02 |
| esp32-wifi-provision | 3 | ✓ | （description 层路由） | -03 |
| fw-core | 4 | ✓ | -02、-03、-04（跨技能路由链） | -01（refuse Rust no_std，移交包外） |
| fw-emulation | 3 | ✓ | -02（→fw-hil-testing） | -02 |
| fw-hil-testing | 4 | ✓ | （断言内引用发布门禁回环） | -02 |
| fw-release-gate | 4 | ✓ | （-02 断言含 fw-hil-testing 回环） | -02 |
| fw-toolchain | 3 | ✓ | -02（→esp32-idf 链） | -01、-02 |
| openwrt-amlogic-remake | 4 | ✓ | （-02 断言 →openwrt-image-build 回环） | -01 |
| openwrt-image-build | 4 | ✓ | -02（→openwrt-amlogic-remake） | （-01 覆盖语义纠偏） |
| openwrt-procd-init | 3 | ✓ | -02（→openwrt-image-build） | -02 |
| openwrt-serial-recovery | 3 | ✓ | -03（断言 →procd-init/uci-defaults/storage-mount） | -02 |
| openwrt-storage-mount | 3 | ✓ | -02（纠正 + 引导回 fstab） | （-03 含"拒绝加载"事实性提醒） |
| openwrt-uci-defaults | 3 | ✓ | （-02 断言 →procd-init 侧所有权） | -02 |
| **合计** | **65** | **20/20** | — | — |

已知口径备注（诚实记录，不粉饰）：部分场景的 handoff 语义写在 assertions 而未同步进 `expected_skills`（如 `esp32-freertos-01`、`openwrt-serial-recovery-03`）；forward-test 评分前建议先统一口径。

**执行方法**（对齐 rust-skills forward-test 规则）：

1. 每条 case 使用**全新 Agent 上下文**：只提供用户 prompt 与已安装的本包技能，不提供期望技能、assertions 或本文档。
2. 记录实际加载的技能、输出、命令、日志与产物。
3. 评估触发准确率、错误交接、事实正确性与验证完成度。
4. **只有原始证据满足该 case 全部 assertions 才计 pass**；部分满足计 fail 并注明未满足断言。
5. 修改技能后重跑受影响 case；版本升级时全量重跑。

当前状态：**第一轮 forward-test 已执行（2026-09-02，65/65）**。

### 第一轮执行记录

- **方法**：批量新鲜上下文仿真——7 个并行执行器（FT-1…FT-7），各自先仅读 20 个 SKILL.md 前 12 行 frontmatter 构建"插件清单"并据此路由（禁止预读正文），再实读被路由技能全文与相关 references 作答，逐断言引用技能文件小节/行号判定。逐场景独立处理。**与 rust-skills 逐条全新上下文的严格形态相比为仿真近似**，方法学差异如实声明。
- **结果**（`evaluation/forward-test/forward-test-summary.json`，含逐场景明细）：

| 维度 | 结果 |
|---|---|
| 场景 | **54 pass / 10 warn / 1 fail**（65） |
| 断言 | **276 pass / 11 warn / 1 fail**（288） |
| 路由（expected_skills 成员资格） | **65/65 命中** |
| 亮点 | refusal 类场景（编 DTB/私钥进 git/写死凭据/C3 默认引脚）全部被 description 字面命中；跨技能行号引用自洽 |

- **FAIL（1）**：`esp32-idf-02` —— 场景设计与包自路由规则矛盾（expected 首元素为 esp32-idf，但 esp32-idf description 明示 OTA → esp32-ota）。**已修**：expected_skills 重排为 `[esp32-ota, esp32-idf]` 并泛化两条视角绑定断言（场景文件内含修正注记）。
- **WARN（10）→ 全部已修**（内容增补直接闭合缺口，grep 复核在位，严格校验保持 0E0W）：

| 场景 | 缺口 | 修复落点 |
|---|---|---|
| openwrt-amlogic-remake-04 | 查无 BOARD 报错串未记录 | `board-database.md` 补 `confirm_version` 报错（上游 L687-692） |
| fw-core-02 | 破坏性操作契约不随单技能路由 | `emmc-install.md` 补破坏性操作契约 |
| openwrt-uci-defaults-01 | 时区零覆盖 | `uci-defaults-lifecycle.md` 补 timezone 配置 |
| openwrt-uci-defaults-02 | root+远程拉取供应链风险未显式关联 | `SKILL.md` 补供应链红线 |
| fw-emulation-03 | 真实例不可定位 | `host-mocking.md` 补公开仓溯源（无本机路径） |
| fw-release-gate-02 | 私钥泄露无处置 runbook | `release-checklist.md` 补 4 步 runbook |
| openwrt-image-build-04 | postinst 失败无收敛操作法 | `files-injection-semantics.md` 补最小二分+反绕过 |
| esp32-peripherals-01 | 引脚落点机制缺 | `SKILL.md` Workflow 1 补显式写入步骤 |
| esp32-peripherals-03 | 迁移 hand-off 无专行 | `SKILL.md` Hand-off 表补迁移行 |
| esp32-debug-02 | 缓解类观察项缺内容支撑 | `crash-triage.md` 补"假设性缓解"措辞规范 |

- **口径说明**：routing_match 按 expected_skills **成员资格**判定（FT-5 曾按首元素比较致 esp32-idf-02 误计 false，汇总时已规范化并在本节注明）。
- **再验证策略**：本轮 11 处修复均为内容增补/场景重排，grep 复核在位 + 严格校验通过；受影响 case 的复跑并入下一轮全量 forward-test。

## 自动化基线维护

`evaluation/scenarios.json` 为生成产物，勿手改；源文件变更后重新生成并校验：

```bash
python3 scripts/merge_scenarios.py --generated <日期>   # 重新合并
python3 scripts/merge_scenarios.py --generated <日期> --check   # 复核一致
python3 scripts/validate_skills.py                     # 结构门禁
```

## 遗留待办清单（诚实，不伪装完成）

| # | 待办 | 阻塞层级 | 说明 |
|---:|---|---|---|
| 1 | **golden examples 补齐其余 17 技能** | 第二层收尾 | ~~全部空占位~~ → 3 个黄金示例已执行（GE-1 QEMU 冒烟 / GE-2 IB+FILES= 注入 / GE-3 IDF v6.1 构建，见第二层）；其余 17 技能按三例模板补齐待排期。PHASE-2-EVALUATION G5 的"≥1 可执行 golden example"已解除空仓状态。 |
| 2 | **真机 HIL 证据** | 硬件依赖（第二层） | GE-1/2/3 覆盖了"构建→启动冒烟→注入验证"三个前级徽章（B0/B1）；真机 flash + 上电运行的 `HIL Verified`（B2）待硬件（ESP32 系列 + Amlogic 盒子 + 串口线），按 `fw-hil-testing` 验收矩阵取证。 |
| 3 | **forward-test 第二轮** | 第三层 | 第一轮已于 2026-09-02 执行（54/10/1，11 处发现全部修复，见第三层执行记录）；受影响 case 复跑 + 版本升级全量重跑待排期。 |
| 4 | **场景口径统一** | 低 | 把 assertions 内的 handoff 语义同步进 `expected_skills`（涉及 `esp32-freertos-01`、`openwrt-serial-recovery-03` 等），避免 forward-test 评分口径分歧。 |
| 5 | **TinyNAS 引用泛化** | 低（见收尾审计报告） | `skills/` 内 25 处 TinyNAS 提及中，多数为带免责声明的模式引用（可留）；少数含内部仓库路径/本机绝对路径/实名脚本案例，建议后续泛化，清单见 Phase 3 收尾汇报。 |
| 6 | **`esp32-matter` / `esp32-ble` / `openwrt-wireless` 候选基线走读** | 下一扩容批次 | 见 `PHASE-2-EVALUATION.md` 候选池；须在待办 1 的 golden example 基础设施就绪后启动。 |

严格模式校验当前 0 error，无校验类待办。
