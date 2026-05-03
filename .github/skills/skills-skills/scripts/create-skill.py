#!/usr/bin/env python3
"""Skill 脚手架生成器。

根据 minimal（精简）或 full（完整）模式，在指定输出目录下生成标准技能目录结构：
  SKILL.md + references/ + scripts/ + assets/ + AGENTS.md（full 模式）

使用示例：
  python create-skill.py my-skill --full --output .github/skills
  python create-skill.py my-skill --minimal --output .github/skills
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
  """解析命令行参数。

  Returns:
      包含 skill_name、minimal、full、output、force 字段的命名空间对象。
  """
  parser = argparse.ArgumentParser(description="创建技能脚手架目录结构")
  parser.add_argument("skill_name", help="技能名称，必须匹配 ^[a-z][a-z0-9-]*$")
  parser.add_argument("--minimal", action="store_true", help="生成精简骨架（仅 SKILL.md）")
  parser.add_argument("--full", action="store_true", help="生成完整骨架（含 references/scripts/AGENTS.md）")
  parser.add_argument("-o", "--output", default=".", help="输出父目录（默认为当前目录）")
  parser.add_argument("-f", "--force", action="store_true", help="目标目录已存在时强制覆盖")
  return parser.parse_args()


def render_template(src: Path, dest: Path, skill_name: str) -> None:
  """读取模板文件并将 {{skill_name}} 占位符替换为实际名称后写入目标路径。

  Args:
      src: 模板文件路径。
      dest: 目标输出文件路径。
      skill_name: 用于替换占位符的技能名称。
  """
  content = src.read_text(encoding="utf-8").replace("{{skill_name}}", skill_name)
  dest.write_text(content, encoding="utf-8", newline="\n")


def write_references(target_dir: Path, skill_name: str) -> None:
  """生成 references/ 目录下的标准参考文件（full 模式）。

  Args:
      target_dir: 技能根目录路径。
      skill_name: 技能名称，用于文件内容标题。
  """
  refs = target_dir / "references"

  (refs / "getting_started.md").write_text(
    f"""# {skill_name} 入门指南与词汇表

## 目标

- 定义本领域最重要的 10 个术语
- 提供从零到可运行的最短路径

## 核心概念

| 术语 | 说明 |
|:---|:---|
| （术语1） | （说明） |
| （术语2） | （说明） |

## 快速上手

1. （步骤一）
2. （步骤二）
3. （步骤三）
""",
    encoding="utf-8",
    newline="\n",
  )

  (refs / "api.md").write_text(
    f"""# {skill_name} API / CLI / 配置参考

## 组织原则

- 按使用场景分类，而非字母顺序
- 关键参数：默认值、取值范围、常见误用
- 常见错误：错误信息 -> 原因 -> 修复步骤

## 常用命令

```bash
# （示例命令1）
# （示例命令2）
```

## 常见错误

| 错误信息 | 原因 | 修复方案 |
|:---|:---|:---|
| （错误1） | （原因） | （修复） |
""",
    encoding="utf-8",
    newline="\n",
  )

  (refs / "examples.md").write_text(
    f"""# {skill_name} 长篇示例

超过约 20 行的示例放在此处，按使用场景分类：

## 场景1：（描述）

（详细步骤与代码）

## 场景2：（描述）

（详细步骤与代码）
""",
    encoding="utf-8",
    newline="\n",
  )

  (refs / "troubleshooting.md").write_text(
    f"""# {skill_name} 故障排查与边界情况

格式：症状 -> 可能原因 -> 诊断方法 -> 修复方案

## 常见问题

### 问题1：（症状描述）

- **可能原因**：
- **诊断方法**：
- **修复方案**：

### 问题2：（症状描述）

- **可能原因**：
- **诊断方法**：
- **修复方案**：
""",
    encoding="utf-8",
    newline="\n",
  )


def write_scripts_main(target_dir: Path, skill_name: str) -> None:
  """生成 scripts/main.py 辅助脚本模板（full 模式）。

  Args:
      target_dir: 技能根目录路径。
      skill_name: 技能名称，用于模块文档字符串。
  """
  # 使用普通字符串（非 f-string）避免与生成代码中的 {} 语法混淆，统一用 __SKILL_NAME__ 占位符替换
  template = '''#!/usr/bin/env python3
"""__SKILL_NAME__ 技能辅助脚本入口。

将核心辅助逻辑保留在 Python 中以保证跨平台可移植性。
如需 Shell 包装，请在 .sh / .ps1 中仅做参数转发，不写主逻辑。
"""
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
  """解析命令行参数。

  Returns:
      包含 workspace 字段的命名空间对象。
  """
  parser = argparse.ArgumentParser(description="__SKILL_NAME__ 技能辅助脚本")
  parser.add_argument("--workspace", default=".", help="工作区根路径（默认为当前目录）")
  return parser.parse_args()


def main() -> int:
  """主入口：执行技能辅助任务。

  Returns:
      0 表示成功，非 0 表示失败。
  """
  args = parse_args()
  workspace = Path(args.workspace).resolve()
  print(f"workspace={workspace}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
'''
  (target_dir / "scripts" / "main.py").write_text(
    template.replace("__SKILL_NAME__", skill_name),
    encoding="utf-8",
    newline="\n",
  )


def write_agents_md(target_dir: Path, skill_name: str) -> None:
  """生成技能目录的 AGENTS.md 文件（full 模式）。

  Args:
      target_dir: 技能根目录路径。
      skill_name: 技能名称，用于文档标题。
  """
  (target_dir / "AGENTS.md").write_text(
    f"""# .github/skills/{skill_name}

本目录是 `{skill_name}` 技能的实现目录。

## 目录结构

```
{skill_name}/
|-- AGENTS.md         # 本文件：目录结构说明与职责边界
|-- SKILL.md          # 入口：触发条件/边界/交付物/流程
|-- references/       # 参考资料与导航索引
|   `-- index.md      # 导航入口（必须）
|-- scripts/          # 可执行脚本与自动化（优先 .py）
|   `-- main.py       # 辅助脚本主实现
`-- assets/           # 模板/配置/静态资源
```

## 文件职责

- `SKILL.md`：技能入口，描述触发条件、边界、快速参考与示例。
- `references/index.md`：参考文档导航索引，长篇内容的入口。
- `scripts/main.py`：技能辅助脚本主实现（保持跨平台可移植）。

## 依赖与边界

- 本目录只承载 `{skill_name}` 领域的知识与工具。
- 通用逻辑请下沉到仓库级公共目录，避免跨技能目录的隐式依赖。

## 脚本约定

- `scripts/` 中新增辅助脚本优先使用 `.py`。
- `.sh` / `.ps1` 仅作薄封装入口（环境变量、路径、参数透传）。
""",
    encoding="utf-8",
    newline="\n",
  )


def main() -> int:
  """主入口：解析参数，生成技能目录结构。

  Returns:
      0 表示成功生成；非 0 表示失败。

  Raises:
      SystemExit: 技能名称不合法、模板文件缺失或目标目录已存在（未指定 --force）时退出。
  """
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
    f"""# {skill_name} 参考文档索引

## 快速链接

- 入门指南：`getting_started.md`
- API/CLI/配置：`api.md`（如适用）
- 长篇示例：`examples.md`
- 故障排查：`troubleshooting.md`

## 说明

- 长篇内容（摘录、证据链接、边界情况、FAQ）放在本目录。
- `SKILL.md` 的快速参考保持简短且可直接使用。
""",
    encoding="utf-8",
    newline="\n",
  )

  if mode == "full":
    write_references(target_dir, skill_name)
    write_scripts_main(target_dir, skill_name)
    write_agents_md(target_dir, skill_name)

  print()
  print(f"OK: 技能目录已生成：{target_dir}/")
  print()
  print("目录结构：")
  print(f"  {target_dir}/")
  if mode == "full":
    print("  |-- AGENTS.md")
  print("  |-- SKILL.md")
  print("  |-- assets/")
  print("  |-- scripts/")
  if mode == "full":
    print("  |   \\-- main.py")
  print("  \\-- references/")
  print("      \\-- index.md")
  print()
  print("下一步：")
  print(f"  1) 编辑 {target_dir}/SKILL.md（触发器/边界/快速参考/示例）")
  print(f"  2) 将长篇文档放入 {target_dir}/references/ 并更新 index.md")
  print(f"  3) 运行验证：python validate-skill.py {target_dir} --strict")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
