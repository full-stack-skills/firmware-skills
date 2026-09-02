#!/usr/bin/env python3
"""merge_scenarios.py — 把 evaluation/scenarios/scenarios.<skill>.json 合并为单个 evaluation/scenarios.json。

仅用 python3 标准库。

用法:
    python3 scripts/merge_scenarios.py                 # 默认仓库根 = 脚本上一级
    python3 scripts/merge_scenarios.py --root /path    # 指定仓库根
    python3 scripts/merge_scenarios.py --check         # 只校验已生成文件与源文件一致，不写入

合并规则:
    1. 读取 evaluation/scenarios/ 下所有 scenarios.<skill-name>.json（每个文件顶层为数组）。
    2. 按技能名字典序排序文件，组内保持文件内原有顺序。
    3. 全部元素平铺，按 id 去重（重复 id 报错并列出，不静默丢弃）。
    4. 写出顶层结构:
       {"version":"0.1.0","generated":"<日期>","count":N,"scenarios":[...]}

退出码:
    0 = 成功（--check 模式下表示一致）
    1 = 场景文件非法 / id 重复 / --check 不一致
    2 = 用法/IO 错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

SCENARIO_FILE_RE = re.compile(r"scenarios\.(.+)\.json$")
VERSION = "0.1.0"


def load_groups(scen_dir: Path) -> list[tuple[str, list[dict]]]:
    """返回 [(skill_name, [scenario, ...]), ...]，按技能名字典序排序。"""
    if not scen_dir.is_dir():
        print(f"[fatal] 场景目录不存在: {scen_dir}", file=sys.stderr)
        raise SystemExit(2)
    groups: list[tuple[str, list[dict]]] = []
    for path in sorted(scen_dir.glob("*.json")):
        m = SCENARIO_FILE_RE.fullmatch(path.name)
        if not m:
            print(f"[fatal] 文件名不符合 scenarios.<skill-name>.json 约定: {path.name}", file=sys.stderr)
            raise SystemExit(1)
        skill = m.group(1)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[fatal] {path.name} 不是合法 JSON: {exc}", file=sys.stderr)
            raise SystemExit(1)
        if not isinstance(data, list) or not data:
            print(f"[fatal] {path.name} 顶层必须是非空数组", file=sys.stderr)
            raise SystemExit(1)
        for i, item in enumerate(data):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                print(f"[fatal] {path.name}[{i}] 缺少非空字符串字段 id", file=sys.stderr)
                raise SystemExit(1)
        groups.append((skill, data))
    groups.sort(key=lambda kv: kv[0])
    return groups


def merge(groups: list[tuple[str, list[dict]]]) -> list[dict]:
    seen: dict[str, str] = {}
    flat: list[dict] = []
    for skill, items in groups:
        for item in items:
            sid = item["id"]
            if sid in seen:
                print(f"[fatal] 场景 id 重复: {sid!r} 同时出现于 {seen[sid]} 与 {skill}", file=sys.stderr)
                raise SystemExit(1)
            seen[sid] = skill
            flat.append(item)
    return flat


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="merge_scenarios.py",
        description="合并 evaluation/scenarios/*.json 为 evaluation/scenarios.json",
    )
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent),
                        help="仓库根目录（默认: 脚本所在目录的上一级）")
    parser.add_argument("--generated", default=date.today().isoformat(),
                        help="写入 generated 字段的日期（默认: 今天）")
    parser.add_argument("--check", action="store_true",
                        help="不写入，只校验已生成的 scenarios.json 与源文件一致")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    scen_dir = root / "evaluation" / "scenarios"
    out_path = root / "evaluation" / "scenarios.json"

    groups = load_groups(scen_dir)
    flat = merge(groups)
    payload = {
        "version": VERSION,
        "generated": args.generated,
        "count": len(flat),
        "scenarios": flat,
    }

    if args.check:
        if not out_path.is_file():
            print(f"[fatal] 未生成 {out_path}", file=sys.stderr)
            return 1
        current = json.loads(out_path.read_text(encoding="utf-8"))
        if current != payload:
            print("[error] evaluation/scenarios.json 与源文件合并结果不一致，请重新运行合并", file=sys.stderr)
            return 1
        print(f"[ok] check 通过: {out_path.name} 与 {len(groups)} 个源文件合并结果一致")
        return 0

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[ok] 写出 {out_path}: {len(flat)} 条场景（来自 {len(groups)} 个技能文件，按技能名字典序）")
    for skill, items in groups:
        print(f"       {skill}: {len(items)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
