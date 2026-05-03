#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Create skill scaffold")
  parser.add_argument("skill_name")
  parser.add_argument("--minimal", action="store_true")
  parser.add_argument("--full", action="store_true")
  parser.add_argument("-o", "--output", default=".")
  parser.add_argument("-f", "--force", action="store_true")
  return parser.parse_args()


def render_template(src: Path, dest: Path, skill_name: str) -> None:
  content = src.read_text(encoding="utf-8").replace("{{skill_name}}", skill_name)
  dest.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
  args = parse_args()
  skill_name = args.skill_name

  if not re.fullmatch(r"[a-z][a-z0-9-]*", skill_name):
    raise SystemExit("Error: skill-name must match ^[a-z][a-z0-9-]*$")

  mode = "minimal" if args.minimal else "full"
  if args.full:
    mode = "full"

  script_dir = Path(__file__).resolve().parent
  assets_dir = script_dir.parent / "assets"
  template = assets_dir / ("template-minimal.md" if mode == "minimal" else "template-complete.md")
  if not template.exists():
    raise SystemExit(f"Error: template not found: {template}")

  output_dir = Path(args.output).resolve()
  target_dir = output_dir / skill_name

  if target_dir.exists() and not args.force:
    raise SystemExit(f"Error: target already exists: {target_dir} (use --force)")

  (target_dir / "assets").mkdir(parents=True, exist_ok=True)
  (target_dir / "scripts").mkdir(parents=True, exist_ok=True)
  (target_dir / "references").mkdir(parents=True, exist_ok=True)

  render_template(template, target_dir / "SKILL.md", skill_name)

  (target_dir / "references" / "index.md").write_text(
    f"""# {skill_name} Reference Index

## Quick Links

- Getting started: `getting_started.md`
- API/CLI/config: `api.md` (if applicable)
- Examples: `examples.md`
- Troubleshooting: `troubleshooting.md`

## Notes

- Put long-form content here: excerpts, evidence links, edge cases, FAQ
- Keep `SKILL.md` Quick Reference short and directly usable
""",
    encoding="utf-8",
    newline="\n",
  )

  if mode == "full":
    (target_dir / "references" / "getting_started.md").write_text(
      """# Getting Started & Vocabulary

## Goals

- Define the 10 most important terms in this domain
- Provide the shortest path from zero to working
""",
      encoding="utf-8",
      newline="\n",
    )
    (target_dir / "references" / "api.md").write_text(
      """# API / CLI / Config Reference (If Applicable)

## Suggested Structure

- Organize by use case, not alphabetically
- Key parameters: defaults, boundaries, common misuse
- Common errors: message -> cause -> fix steps
""",
      encoding="utf-8",
      newline="\n",
    )
    (target_dir / "references" / "examples.md").write_text(
      """# Long Examples

Put examples longer than ~20 lines here, split by use case:

- Use case 1: ...
- Use case 2: ...
""",
      encoding="utf-8",
      newline="\n",
    )
    (target_dir / "references" / "troubleshooting.md").write_text(
      """# Troubleshooting & Edge Cases

Write as: symptom -> likely causes -> diagnosis -> fix.
""",
      encoding="utf-8",
      newline="\n",
    )
    (target_dir / "scripts" / "main.py").write_text(
      """#!/usr/bin/env python3
\"\"\"Skill helper script entrypoint.

Keep core helper logic in Python for portability.
Use .sh/.ps1 only as thin wrappers when needed.
\"\"\"

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=\"Skill helper script\")
  parser.add_argument(\"--workspace\", default=\".\", help=\"Workspace root path\")
  return parser.parse_args()


def main() -> int:
  args = parse_args()
  workspace = Path(args.workspace).resolve()
  print(f\"workspace={workspace}\")
  return 0


if __name__ == \"__main__\":
  raise SystemExit(main())
""",
      encoding="utf-8",
      newline="\n",
    )

  print()
  print(f"OK: Skill generated: {target_dir}/")
  print()
  print("Layout:")
  print(f"  {target_dir}/")
  print("  |-- SKILL.md")
  print("  |-- assets/")
  print("  |-- scripts/")
  print("  \\-- references/")
  print("      \\-- index.md")
  print()
  print("Next steps:")
  print(f"  1) Edit {target_dir}/SKILL.md (triggers/boundaries/quick reference/examples)")
  print(f"  2) Put long-form docs into {target_dir}/references/ and update index.md")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
