# Skill Seekers（内置工具）使用说明

本目录把 `Skill_Seekers-development` 的源码作为 `skills-skills` 的必备工具内置，用于把「文档 / GitHub 仓库 / PDF」快速转成一个可落地的 Skill 初稿。

## 目录约定

- 工具源码：`.github/skills/skills-skills/scripts/Skill_Seekers-development/`
- 运行入口：`.github/skills/skills-skills/scripts/skill-seekers.py`
- 依赖初始化：`.github/skills/skills-skills/scripts/skill-seekers-bootstrap.py`
- 导入到本仓库：`.github/skills/skills-skills/scripts/skill-seekers-import.py`
- 更新源码快照：`.github/skills/skills-skills/scripts/skill-seekers-update.py`（需要网络）

## 推荐工作流（强约束）

1. 用 Skill Seekers 生成初稿到 `output/<name>/`
2. 导入到 `.github/skills/<name>/`
3. 用 `validate-skill.py --strict` 做质量闸门
4. 回到 `skills-skills` 的规范对 `SKILL.md` 做“可激活性”与“边界”修订

## 最小可执行示例

```bash
# 1) 初始化（只需一次）
python ./.github/skills/skills-skills/scripts/skill-seekers-bootstrap.py

# 2) 生成（示例：抓 docs 配置）
python ./.github/skills/skills-skills/scripts/skill-seekers.py -- scrape --config ./.github/skills/skills-skills/scripts/Skill_Seekers-development/configs/react.json

# 3) 导入到 skills/
python ./.github/skills/skills-skills/scripts/skill-seekers-import.py react

# 4) 严格校验
python ./.github/skills/skills-skills/scripts/validate-skill.py .github/skills/react --strict
```

## 设计原则

- `.github/skills/skills-skills/` 负责：规范、模板、闸门、可激活性；不直接承载领域知识。
- Skill Seekers 负责：抓取与初稿生成；最终交付仍以本仓库的 `validate-skill.py --strict` 为准。
