# firmware-skills — Authoring Conventions（全体技能作者必读）

> 本文件是技能作者的**硬约束**。评审（validate + TRACE）按此执行。

## 0. 格式范本

先精读 `../rust-skills/skills/rust-stable/SKILL.md` 与 `rust-embedded/SKILL.md`，再动笔。

## 1. SKILL.md 结构（固定顺序）

1. frontmatter：`name` + `description`（三合一：能做什么 + "Use when..." 触发词 + 显式 hand-off 指引）
2. 任务分型（Determine Task Type）
3. Prerequisites / Preflight（**必须先运行时核验**环境真实版本）
4. Offline Baseline（dated 声明："…走读 2026-09-02，不自动更新"）
5. Contracts（设备/硬件契约；不确定**禁止编造**）
6. Capability Boundaries + **Hand-off 路由表**（User Intent → Skill）
7. Workflow（编号步骤，含命令与期望输出）
8. Validation Gates（可执行验证）
9. Pitfalls（每条含"不要做 X"）
10. Official Sources（官方文档 URL，唯一允许外链的 section）
11. Privacy（不采集、不外发用户数据/凭据）

## 2. 硬指标

- SKILL.md ≤ 500 行；单个 reference ≤ 120 行；一个决策点一个 reference 文件 + read-when 条件
- 禁手写 `/etc/rc.d/` 指引类内容进 OpenWrt 技能（IB 自动 enable 是事实）
- dated baseline 固定口径：OpenWrt=25.12.5（走读 2026-09-02）；ophub=上游 HEAD `c593d56`；ESP-IDF=以 Phase 2 基线文档为准
- 反幻觉红线：DTB 文件名、引脚/复用、分区偏移、内存布局、寄存器 —— 不确定即停，路由到运行时核验或官方源

## 3. 场景用例（每技能 ≥2，其中 ≥1 个 handoff/refusal）

写入 `evaluation/scenarios/scenarios.<skill-name>.json`：

```json
[
  {"id": "<skill>-01", "prompt": "真实用户口语（中英皆可）", "expected_skills": ["<skill>"],
   "assertions": ["assertion_a", "assertion_b"]}
]
```

## 4. 与项目知识的边界

TinyNAS 专属产物（五段式命名实例、14 项清单、92 分支策略）**不进**本通用包；通用包只收模式（如"五段式命名作为 release 命名模板"写在 fw-release-gate）。

## 5. 完成诚实性

无真实运行证据的能力，必须标注 `Build Verification Only` 或 `Pending HIL`；禁止伪造"已在硬件上验证"。
