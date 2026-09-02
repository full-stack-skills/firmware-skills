#!/usr/bin/env python3
"""validate_skills.py — firmware-skills 仓库技能包校验器（仅用 python3 标准库）。

用法:
    python3 scripts/validate_skills.py                 # 严格模式（默认）
    python3 scripts/validate_skills.py --lenient       # 分阶段模式
    python3 scripts/validate_skills.py --root /path/to/firmware-skills
    python3 scripts/validate_skills.py --help

模式:
    strict（默认）  所有违规记为 error；存在 error 则退出码 1。
    --lenient       分阶段模式：仅将“清单中已声明、但目录或 SKILL.md 尚未落地”
                    的条目降级为 warn（供多 Phase 并行开发）；其余违规仍为 error。

检查项:
    1. .claude-plugin/plugin.json 的 skills 列表与 skills/* 目录双向一致
    2. 每个 SKILL.md 的 frontmatter 含非空 name + description，且 name == 目录名
       （name 需符合全小写连字符命名约定）
    3. SKILL.md <= --max-skill-lines（默认 500）行；references/* <= --max-ref-lines
       （默认 120）行
    4. Markdown 相对链接目标存在（跳过 http/https/mailto/锚点）
    5. 代码围栏（```）配对（成偶数）
    6. evaluation/scenarios/scenarios.*.json 符合 schema：
       顶层为数组，元素含 id(str)/prompt(str)/expected_skills(str数组)/
       assertions(str数组)；文件名中的技能名须已登记；已落地技能应有 >=2 条场景

退出码:
    0 = 通过（允许存在 warn）
    1 = 存在 error
    2 = 用法/IO 错误（仓库根不存在、plugin.json 缺失或损坏）

另: 已落地但场景数 <2、或场景文件指向未知技能名 → 仅 warn（不影响退出码）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^\s*```")
FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")

# 跳过的链接 scheme / 目标
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")


class Report:
    """收集 error / warn，统一输出。"""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warns: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"[error] {msg}")

    def warn(self, msg: str) -> None:
        self.warns.append(msg)
        print(f"[warn]  {msg}")

    def ok(self, msg: str) -> None:
        print(f"[ok]    {msg}")


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """极简 frontmatter 解析：'---' 开头，下一个 '---' 结束，key: value 行。

    返回 (字段字典或 None, 错误信息)。字段字典为 None 表示结构非法。
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "文件不以 '---' frontmatter 开头"
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, "frontmatter 未闭合（缺第二个 '---'）"
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        m = FRONTMATTER_KEY_RE.match(line)
        if not m:
            return None, f"frontmatter 行无法解析: {line!r}"
        fields[m.group(1)] = m.group(2).strip()
    return fields, ""


def check_markdown_file(path: Path, rep: Report, kind_label: str) -> None:
    """检查项 4（相对链接）与 5（代码围栏配对），适用于任意 .md。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    # 链接目标存在性
    for match in LINK_RE.finditer(text):
        target = match.group(1)
        if target.startswith(SKIP_LINK_PREFIXES):
            continue
        clean = target.split("#", 1)[0].strip()
        if not clean:
            continue  # 纯页内锚点
        resolved = (path.parent / clean).resolve()
        if not resolved.exists():
            rep.error(f"{kind_label} 相对链接目标不存在: {path} -> {target}")
    # 代码围栏配对
    fence_count = sum(1 for line in text.splitlines() if FENCE_RE.match(line))
    if fence_count % 2 != 0:
        rep.error(f"{kind_label} 代码围栏不配对（``` 出现奇数次 {fence_count}）: {path}")


def check_skill(skill_dir: Path, skill_name: str, rep: Report, args: argparse.Namespace) -> bool:
    """检查项 2/3/4/5。返回该技能是否"已落地"（存在合法 SKILL.md）。"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        # 调用方已按 lenient/strict 处理"未落地"，这里直接跳过
        return False

    text = skill_md.read_text(encoding="utf-8", errors="replace")
    n_lines = len(text.splitlines())
    if n_lines > args.max_skill_lines:
        rep.error(f"技能 {skill_name}: SKILL.md {n_lines} 行 > 上限 {args.max_skill_lines}")

    fields, err = parse_frontmatter(text)
    if fields is None:
        rep.error(f"技能 {skill_name}: frontmatter 非法 — {err}")
        return True
    name = fields.get("name", "").strip()
    desc = fields.get("description", "").strip()
    if not name:
        rep.error(f"技能 {skill_name}: frontmatter 缺少非空 name")
    if not desc:
        rep.error(f"技能 {skill_name}: frontmatter 缺少非空 description")
    if name and name != skill_name:
        rep.error(f"技能 {skill_name}: frontmatter name={name!r} 与目录名不一致")
    if name and not NAME_RE.match(name):
        rep.error(f"技能 {skill_name}: name 不符合全小写连字符命名约定: {name!r}")
    rep.ok(f"技能 {skill_name}: frontmatter name/description 齐备，SKILL.md {n_lines} 行")

    # references 行数 + 所有 md 的链接/围栏检查
    for sub in sorted(skill_dir.rglob("*")):
        if sub.is_file() and sub.suffix == ".md":
            rel = sub.relative_to(skill_dir).as_posix()
            if rel.startswith("references/") and len(sub.read_text(encoding="utf-8", errors="replace").splitlines()) > args.max_ref_lines:
                rep.error(f"技能 {skill_name}: {rel} 超过 {args.max_ref_lines} 行上限")
            check_markdown_file(sub, rep, f"技能 {skill_name}:")
    return True


def check_scenarios(scen_dir: Path, manifest: set[str], landed: set[str], rep: Report) -> None:
    """检查项 6。"""
    if not scen_dir.is_dir():
        rep.warn("evaluation/scenarios/ 目录不存在，尚无任何场景用例")
        return
    per_skill: dict[str, int] = {}
    files = sorted(scen_dir.glob("*.json"))
    if not files:
        rep.warn("evaluation/scenarios/ 下没有任何 *.json 场景文件")
    for path in files:
        m = re.fullmatch(r"scenarios\.(.+)\.json", path.name)
        if not m:
            rep.error(f"场景文件名不符合 scenarios.<skill-name>.json 约定: {path.name}")
            continue
        skill = m.group(1)
        if skill not in manifest:
            rep.warn(f"场景文件 {path.name} 指向未登记技能 {skill!r}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            rep.error(f"场景文件 {path.name} 不是合法 JSON: {exc}")
            continue
        if not isinstance(data, list) or not data:
            rep.error(f"场景文件 {path.name} 顶层必须是非空数组")
            continue
        for i, item in enumerate(data):
            label = f"{path.name}[{i}]"
            if not isinstance(item, dict):
                rep.error(f"场景 {label} 必须是对象")
                continue
            for key in ("id", "prompt"):
                if not isinstance(item.get(key), str) or not item.get(key):
                    rep.error(f"场景 {label} 缺少非空字符串字段 {key}")
            for key in ("expected_skills", "assertions"):
                val = item.get(key)
                if not isinstance(val, list) or not val or not all(isinstance(v, str) and v for v in val):
                    rep.error(f"场景 {label} 字段 {key} 必须是非空字符串数组")
            if isinstance(item.get("id"), str) and item["id"]:
                per_skill[skill] = per_skill.get(skill, 0) + 1
        rep.ok(f"场景文件 {path.name}: {len(data)} 条，schema 通过")
    # 已落地技能应有 >=2 条场景（CONVENTIONS §3）；不足仅 warn（供分阶段）
    for skill in sorted(landed):
        count = per_skill.get(skill, 0)
        if count < 2:
            rep.warn(f"已落地技能 {skill} 场景数 {count} < 2（CONVENTIONS §3）")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_skills.py",
        description="firmware-skills 技能包校验器（用法与退出码语义见模块 docstring）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码: 0=通过(可有 warn)  1=存在 error  2=用法/IO 错误",
    )
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent),
                        help="仓库根目录（默认: 脚本所在目录的上一级）")
    parser.add_argument("--lenient", action="store_true",
                        help="分阶段模式: 清单已声明但未落地的技能降级为 warn")
    parser.add_argument("--max-skill-lines", type=int, default=500,
                        help="SKILL.md 行数上限（默认 500）")
    parser.add_argument("--max-ref-lines", type=int, default=120,
                        help="references/ 单文件行数上限（默认 120）")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    rep = Report()

    plugin_path = root / ".claude-plugin" / "plugin.json"
    skills_root = root / "skills"
    if not plugin_path.is_file():
        print(f"[fatal] 未找到 {plugin_path}", file=sys.stderr)
        return 2
    try:
        manifest_list = json.loads(plugin_path.read_text(encoding="utf-8")).get("skills", [])
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[fatal] plugin.json 读取/解析失败: {exc}", file=sys.stderr)
        return 2
    if not isinstance(manifest_list, list) or not manifest_list:
        print("[fatal] plugin.json 的 skills 列表为空或非法", file=sys.stderr)
        return 2
    manifest = [str(x) for x in manifest_list]

    if not skills_root.is_dir():
        print(f"[fatal] 未找到 {skills_root}", file=sys.stderr)
        return 2
    dirs = sorted(d.name for d in skills_root.iterdir() if d.is_dir())
    manifest_set = set(manifest)
    dirs_set = set(dirs)

    # ---- 检查 1: 清单 <-> 目录 双向一致 ----
    landed: set[str] = set()
    for name in manifest:
        if name not in dirs_set:
            msg = f"清单声明技能 {name!r} 但 skills/{name}/ 目录缺失（未落地？）"
            rep.warn(msg) if args.lenient else rep.error(msg)
    for name in dirs:
        if name not in manifest_set:
            rep.error(f"skills/{name}/ 存在但未登记进 .claude-plugin/plugin.json")
    rep.ok(f"清单/目录一致性: 清单 {len(manifest)} 项, 目录 {len(dirs)} 个")

    # ---- 检查 2/3/4/5: 逐技能 ----
    for name in dirs:
        if name not in manifest_set:
            continue  # 已在检查 1 报错
        skill_dir = skills_root / name
        if not (skill_dir / "SKILL.md").is_file():
            msg = f"技能 {name}: skills/{name}/SKILL.md 缺失（未落地？）"
            rep.warn(msg) if args.lenient else rep.error(msg)
            continue
        if check_skill(skill_dir, name, rep, args):
            landed.add(name)

    # ---- 检查 6: 场景文件 ----
    check_scenarios(root / "evaluation" / "scenarios", manifest_set, landed, rep)

    print()
    print(f"== 摘要: 已落地 {len(landed)}/{len(manifest)} 技能, "
          f"{len(rep.errors)} error, {len(rep.warns)} warn, "
          f"模式={'lenient' if args.lenient else 'strict'} ==")
    if rep.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
