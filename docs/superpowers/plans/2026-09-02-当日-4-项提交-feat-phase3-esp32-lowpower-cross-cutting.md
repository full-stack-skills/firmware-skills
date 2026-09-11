# firmware-skills 历史任务：当日 4 项提交（feat(phase3): esp32-lowpower + cross-cutting 3 + release-gate; merge 65 scenarios; PHASE-2-EVALUATION + TRACE-REPORT; strict 20/20 0E0W; sanitize local path 等）（2026-09-02）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **本计划为历史任务回填**：依据 git 提交记录还原，全部任务已完成，复选框均为 `- [x]`。

**Goal:** 本日完成 4 项提交：

1. feat(phase3): esp32-lowpower + cross-cutting 3 + release-gate; merge 65 scenarios; PHASE-2-EVALUATION + TRACE-REPORT; strict 20/20 0E0W; sanitize local path
2. feat(phase2): 8 esp32 skills + 12 scenarios (baseline v6.1, UNVERIFIED discipline, lenient 0 error/5 warn)
3. docs(phase2): ESP-IDF dated baseline v6.1 (web-verified 2026-09-02, 11 items, UNVERIFIED flags honored)
4. feat(phase1): fw-core + 6 openwrt skills + validator + 21 scenarios (3 parallel authors, lenient 0 error)

**Architecture:** 仓库元数据与文档维护、技能内容更新（SKILL.md）、技能参考/示例资料更新、脚本或文档结构更新。

**Tech Stack:** JSON、Markdown、Python。

**Spec:** 无独立规格文档；依据提交 `032e9b1`, `1ef9ba5`, `94a9199`, `42ac3a1` 还原。

## Global Constraints

- 本计划依据 git 历史回填，仅记录已完成工作（4 个提交均已落地）
- 不含未完成或计划中的工作；步骤复选框全部为已完成状态

---

### Task 1: feat(phase3): esp32-lowpower + cross-cutting 3 + release-gate; merge 65 scenarios; PHASE-2-EVALUATION + TRACE-REPORT; strict 20/20 0E0W; sanitize local path

**Files:**
- `PHASE-2-EVALUATION.md`
- `TRACE-REPORT.md`
- `evaluation/scenarios.json`
- `evaluation/scenarios/scenarios.esp32-lowpower.json`
- `evaluation/scenarios/scenarios.fw-emulation.json`
- `evaluation/scenarios/scenarios.fw-hil-testing.json`
- `evaluation/scenarios/scenarios.fw-release-gate.json`
- `evaluation/scenarios/scenarios.fw-toolchain.json`
- `scripts/__pycache__/validate_skills.cpython-314.pyc`
- `scripts/merge_scenarios.py`
- `skills/esp32-lowpower/SKILL.md`
- `skills/esp32-lowpower/references/sleep-modes.md`
- `skills/esp32-lowpower/references/wakeup-sources.md`
- `skills/fw-emulation/SKILL.md`
- `skills/fw-emulation/references/host-mocking.md`
- …等共 25 个文件

- [x] **Step 1: 完成「feat(phase3): esp32-lowpower + cross-cutting 3 + release-gate; merge 65 scenarios; PHASE-2-EVALUATION + TRACE-REPORT; strict 20/20 0E0W; sanitize local path」（loong10k）**
- [x] **Step 2: 提交** — `032e9b1` feat(phase3): esp32-lowpower + cross-cutting 3 + release-gate; merge 65 scenarios; PHASE-2-EVALUATION + TRACE-REPORT; strict 20/20 0E0W; sanitize local path

---

### Task 2: feat(phase2): 8 esp32 skills + 12 scenarios (baseline v6.1, UNVERIFIED discipline, lenient 0 error/5 warn)

**Files:**
- `evaluation/scenarios/scenarios.esp32-debug.json`
- `evaluation/scenarios/scenarios.esp32-freertos.json`
- `evaluation/scenarios/scenarios.esp32-idf.json`
- `evaluation/scenarios/scenarios.esp32-ota.json`
- `evaluation/scenarios/scenarios.esp32-peripherals.json`
- `evaluation/scenarios/scenarios.esp32-secureboot.json`
- `evaluation/scenarios/scenarios.esp32-variants.json`
- `evaluation/scenarios/scenarios.esp32-wifi-provision.json`
- `skills/esp32-debug/SKILL.md`
- `skills/esp32-debug/references/crash-triage.md`
- `skills/esp32-debug/references/jtag-openocd.md`
- `skills/esp32-freertos/SKILL.md`
- `skills/esp32-freertos/references/smp-pinning.md`
- `skills/esp32-freertos/references/task-checklist.md`
- `skills/esp32-idf/SKILL.md`
- …等共 33 个文件

- [x] **Step 1: 完成「feat(phase2): 8 esp32 skills + 12 scenarios (baseline v6.1, UNVERIFIED discipline, lenient 0 error/5 warn)」（loong10k）**
- [x] **Step 2: 提交** — `1ef9ba5` feat(phase2): 8 esp32 skills + 12 scenarios (baseline v6.1, UNVERIFIED discipline, lenient 0 error/5 warn)

---

### Task 3: docs(phase2): ESP-IDF dated baseline v6.1 (web-verified 2026-09-02, 11 items, UNVERIFIED flags honored)

**Files:**
- `evaluation/baseline-espidf.md`

- [x] **Step 1: 完成「docs(phase2): ESP-IDF dated baseline v6.1 (web-verified 2026-09-02, 11 items, UNVERIFIED flags honored)」（loong10k）**
- [x] **Step 2: 提交** — `94a9199` docs(phase2): ESP-IDF dated baseline v6.1 (web-verified 2026-09-02, 11 items, UNVERIFIED flags honored)

---

### Task 4: feat(phase1): fw-core + 6 openwrt skills + validator + 21 scenarios (3 parallel authors, lenient 0 error)

**Files:**
- `.claude-plugin/plugin.json`
- `README.md`
- `README.zh-CN.md`
- `docs/CONVENTIONS.md`
- `evaluation/scenarios/scenarios.fw-core.json`
- `evaluation/scenarios/scenarios.openwrt-amlogic-remake.json`
- `evaluation/scenarios/scenarios.openwrt-image-build.json`
- `evaluation/scenarios/scenarios.openwrt-procd-init.json`
- `evaluation/scenarios/scenarios.openwrt-serial-recovery.json`
- `evaluation/scenarios/scenarios.openwrt-storage-mount.json`
- `evaluation/scenarios/scenarios.openwrt-uci-defaults.json`
- `scripts/__pycache__/validate_skills.cpython-314.pyc`
- `scripts/validate_skills.py`
- `skills/fw-core/SKILL.md`
- `skills/fw-core/references/routing-esp32.md`
- …等共 40 个文件

- [x] **Step 1: 完成「feat(phase1): fw-core + 6 openwrt skills + validator + 21 scenarios (3 parallel authors, lenient 0 error)」（loong10k）**
- [x] **Step 2: 提交** — `42ac3a1` feat(phase1): fw-core + 6 openwrt skills + validator + 21 scenarios (3 parallel authors, lenient 0 error)
