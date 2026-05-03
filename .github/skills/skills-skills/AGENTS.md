# .github/skills/skills-skills

该目录是一个**元技能（meta-skill）**：用于把任意领域材料（文档/API/代码/规范）沉淀为可复用 Skill（`SKILL.md` + `references/` + `scripts/` + `assets/`），并提供可执行的质量门禁与脚手架。

## 目录结构

```
skills-skills/
|-- AGENTS.md
|-- SKILL.md
|-- assets/
|   |-- template-minimal.md
|   `-- template-complete.md
|-- scripts/
|   |-- Skill_Seekers-development/
|   |-- create-skill.py
|   |-- create-skill.sh                 # thin wrapper -> create-skill.py
|   |-- skill-seekers-bootstrap.py
|   |-- skill-seekers-bootstrap.sh      # thin wrapper -> skill-seekers-bootstrap.py
|   |-- skill-seekers-configs -> Skill_Seekers-development/configs
|   |-- skill-seekers-import.py
|   |-- skill-seekers-import.sh         # thin wrapper -> skill-seekers-import.py
|   |-- skill-seekers.py
|   |-- skill-seekers.sh                # thin wrapper -> skill-seekers.py
|   |-- skill-seekers-src -> Skill_Seekers-development/src
|   |-- skill-seekers-update.py
|   |-- skill-seekers-update.sh         # thin wrapper -> skill-seekers-update.py
|   |-- validate-skill.py
|   `-- validate-skill.sh               # thin wrapper -> validate-skill.py
`-- references/
    |-- index.md
    |-- README.md
    |-- anti-patterns.md
    |-- skill-seekers.md
    |-- quality-checklist.md
    `-- skill-spec.md
```

## 文件职责

- `.github/skills/skills-skills/SKILL.md`: 入口文件（触发条件、交付物、工作流、质量门禁、工具链）。
- `.github/skills/skills-skills/assets/template-minimal.md`: 精简模板（小型领域 / 快速启动）。
- `.github/skills/skills-skills/assets/template-complete.md`: 完整模板（生产级 / 复杂领域）。
- `.github/skills/skills-skills/scripts/create-skill.py`: 脚手架生成器主实现（支持 minimal/full、输出目录、覆盖策略）。
- `.github/skills/skills-skills/scripts/create-skill.sh`: 薄封装入口（转发到 `create-skill.py`）。
- `.github/skills/skills-skills/scripts/Skill_Seekers-development/`: 内置（vendored）Skill Seekers 源码快照（代码 + 配置；不包含上游 Markdown 文档）。
- `.github/skills/skills-skills/scripts/skill-seekers-bootstrap.py`: 为内置 Skill Seekers 工具创建本地 venv 并安装依赖。
- `.github/skills/skills-skills/scripts/skill-seekers.py`: 从内置源码运行 Skill Seekers（docs/github/pdf -> output/<name>/）。
- `.github/skills/skills-skills/scripts/skill-seekers-import.py`: 将 output/<name>/ 导入标准目录 `.github/skills/<name>/`。
- `.github/skills/skills-skills/scripts/skill-seekers-update.py`: 从上游更新内置源码快照（需要网络）。
- `.github/skills/skills-skills/scripts/validate-skill.py`: 规范校验器（支持 `--strict`）。
- 对应 `.sh` 文件均为薄封装入口，默认只转发参数到 `.py` 主实现。
- `.github/skills/skills-skills/references/index.md`: 本元技能参考文档导航。
- `.github/skills/skills-skills/references/README.md`: 上游官方参考（为保证本仓库链接可用做了轻量调整）。
- `.github/skills/skills-skills/references/skill-spec.md`: 本地 Skill 规范（MUST/SHOULD/NEVER）。
- `.github/skills/skills-skills/references/quality-checklist.md`: 质量门禁清单 + 评分标准。
- `.github/skills/skills-skills/references/anti-patterns.md`: 常见反模式及修复方法。
- `.github/skills/skills-skills/references/skill-seekers.md`: 如何将内置工具作为“强制首版草稿生成器”使用。

## 依赖与边界

- `scripts/*.py`：为主实现入口，推荐直接调用。
- `scripts/*.sh`：薄封装入口（兼容历史命令）。
- Python 主脚本依赖：
  - `skill-seekers-bootstrap.py`：需要 `python3` + `pip`（访问 PyPI 需要网络）。
  - `skill-seekers-update.py`：需要网络访问 GitHub codeload。
- 本目录关注“如何构建 Skills”，而非某个具体领域；领域知识应放在 `.github/skills/<domain>/`。

## 脚本约定（新增）

- 在新建或重构 Skill 的 `scripts/` 时，辅助脚本优先使用 `.py`。
- `.sh` / `.ps1` 推荐作为薄封装入口：仅处理环境变量、路径与参数透传，再调用 `.py`。
- 只有在 Python 不可用或必须依赖 shell 平台特性时，才允许 shell 作为主实现。
