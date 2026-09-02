# firmware-skills: 剩余 17 Golden Examples 实施计划

> 状态：**待执行**（配额耗尽，2026-09-03 03:28:04 重置后继续）
> 执行日期：2026-09-03

## 上下文

仓库：`/Users/wandl/workspaces/workspace-agent-skills/full-stack-skills-repositories/firmware-skills/`
已有 3 个 GE 示例（GE-1/2/3），剩余 17 个技能的 `examples/` 为空。
严格校验保持 20/20 0E0W；补齐后更新 TRACE-REPORT 第二层。

---

## 三路并行分工

### 路线 A：OpenWrt 家族 7 个（可执行 shell + 配置 + 文档）

| 技能 | 示例目录 | 类型 | 徽章 |
|---|---|---|---|
| openwrt-procd-init | `examples/ge-procd-service/` | 可执行脚本×2（procd+legacy） | S1 |
| openwrt-uci-defaults | `examples/ge-uci-defaults/` | 可执行脚本 + 配置样例 | S1 |
| openwrt-storage-mount | `examples/ge-storage-mount/` | hotplug 脚本 + fstab 配置 | B0 |
| openwrt-serial-recovery | `examples/ge-recovery-decision/` | 三级梯度决策树文档 | B0 |
| openwrt-amlogic-remake | `examples/ge-amlogic-n1-build/` | N1 完整构建命令序列文档 | B0 |
| fw-release-gate | `examples/ge-release-check/` | 发布前检查脚本（pass/fail 计数） | S1 |
| fw-toolchain | `examples/ge-cross-compile-verify/` | 交叉编译验证脚本 | S1 |

### 路线 B：ESP32 家族 8 个（代码片段 + 配置 + 文档）

| 技能 | 示例目录 | 类型 | 徽章 |
|---|---|---|---|
| esp32-freertos | `examples/ge-freertos-task-queue/` | C 代码片段（task+queue+pinnedToCore） | B0 |
| esp32-peripherals | `examples/ge-peripheral-init/` | C 代码片段（GPIO+UART 初始化） | B0 |
| esp32-wifi-provision | `examples/ge-wifi-provision/` | 配网配置 + 状态机 JSON | B0 |
| esp32-ota | `examples/ge-ota-rollback/` | 分区表 CSV + 回滚逻辑 C 代码 | B0 |
| esp32-lowpower | `examples/ge-deep-sleep/` | 深睡+GPIO唤醒 C 代码片段 | B0 |
| esp32-secureboot | `examples/ge-key-governance/` | 密钥治理脚本 + 签名流水线文档 | S1 |
| esp32-debug | `examples/ge-coredump-parse/` | coredump 解析脚本 + 排查清单 | S1 |
| esp32-variants | `examples/ge-chip-selection/` | 7 芯片选型决策表 | B0 |

### 路线 C：核心 2 个（决策文档 + HIL 矩阵）

| 技能 | 示例目录 | 类型 | 徽章 |
|---|---|---|---|
| fw-core | `examples/ge-task-routing/` | 10 个路由决策记录 + 结构化 JSON | B0 |
| fw-hil-testing | `examples/ge-hil-matrix/` | OpenWrt + ESP32 各 10 行验收矩阵 + G1-G4 流程 | B0 |

---

## 通用纪律

- 每个 README.md ≤100 行，对齐已有 GE README 格式
- 脚本/代码顶部注释："golden example，供技能验证用，非生产代码"
- µA 数值、引脚号、分区偏移一律标"运行时核验"
- 不引用 TinyNAS 专属内容（CONVENTIONS §4）
- `chmod +x` 所有 .sh 文件
- 不得修改 `skills/` 下已有文件

## 执行后动作

1. 更新 `TRACE-REPORT.md` 第二层（20/20 示例补齐）
2. `python3 scripts/validate_skills.py` 严格模式 0E0W
3. `git commit`
4. 更新记忆文件
