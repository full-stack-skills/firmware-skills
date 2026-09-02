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

## 第二层：行为证据（Pending）

如实记录当前状态，**本节无任何伪造的执行输出**：

- **OpenWrt 侧存在真实生产门禁先例**：TinyNAS 项目的 `tests/run-lint.sh` 模式（`sh -n` 全量语法 → uci-defaults 末行 `exit 0` → 禁手放 `/etc/rc.d/` → CGI 禁 `eval` → 无私钥入库，pass/fail 计数、全绿退出 0、任一失败退出 1），已作为模式提炼进 `fw-release-gate/references/release-checklist.md` 与 `fw-emulation/references/host-mocking.md`。该先例证明此类静态门禁在生产环境可落地。
- **本仓 golden examples 尚未执行，标记 `Pending`**：20 个技能的 `examples/` 目录当前为空占位，本仓没有任何一次 QEMU 启动冒烟或 `idf.py` 构建在本仓产物上真实跑通。因此第二层证据为空，这是发布前的阻断项（对应 `PHASE-2-EVALUATION.md` Go/No-Go G5）。
- 场景断言中出现的"Build Verification Only / Pending HIL"标注规范（CONVENTIONS §5）在文档层已落地并经结构校验，但其执行样例尚无本仓产物佐证。

## 第三层：forward-test 计划（Pending forward-test run）

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

当前状态：**`Pending forward-test run`（0/65 已执行）**。

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
| 1 | **golden examples 可执行化** | 发布阻断（第二层） | 20 个 `examples/` 目录均为空占位。ESP-IDF 侧需锁定版本的 `idf.py` 构建样例，OpenWrt 侧需 QEMU（armsr/armv8 combined-efi）启动冒烟样例；两者均待可用的构建/虚拟化环境。补齐前第二层证据为空。 |
| 2 | **真机 HIL 证据** | 硬件依赖（第二层） | 场景与技能文中承诺的 `HIL Verified` 徽章路径需要真实硬件（ESP32 系列 + 功率计/示波器；Amlogic 盒子 + 串口线）；待硬件到位后按 `fw-hil-testing` 验收矩阵取证。 |
| 3 | **forward-test run** | 第三层 | 65 条场景 0/65 已执行；执行方法见上节，须新上下文逐条跑，全断言满足才计 pass。 |
| 4 | **场景口径统一** | 低 | 把 assertions 内的 handoff 语义同步进 `expected_skills`（涉及 `esp32-freertos-01`、`openwrt-serial-recovery-03` 等），避免 forward-test 评分口径分歧。 |
| 5 | **TinyNAS 引用泛化** | 低（见收尾审计报告） | `skills/` 内 25 处 TinyNAS 提及中，多数为带免责声明的模式引用（可留）；少数含内部仓库路径/本机绝对路径/实名脚本案例，建议后续泛化，清单见 Phase 3 收尾汇报。 |
| 6 | **`esp32-matter` / `esp32-ble` / `openwrt-wireless` 候选基线走读** | 下一扩容批次 | 见 `PHASE-2-EVALUATION.md` 候选池；须在待办 1 的 golden example 基础设施就绪后启动。 |

严格模式校验当前 0 error，无校验类待办。
