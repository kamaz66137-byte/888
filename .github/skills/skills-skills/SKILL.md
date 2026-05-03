---
name: skills-skills
description: "Claude Skills 元技能：将领域素材（文档/API/代码/规范）提炼为可复用的 Skill（SKILL.md + references/scripts/assets），并对现有 Skill 进行重构，提升清晰度、激活可靠性与质量门控。"
---

# Claude Skills 元技能

将散乱的领域素材转化为可复用、可维护、可靠激活的 Skill：
- `SKILL.md` 作为入口点（触发器、约束、模式、示例）
- `references/` 存放长篇证据与导航索引
- 可选的 `scripts/` 和 `assets/` 用于脚手架与模板

## 何时使用本技能

在以下情况触发本元技能：
- 从文档/规范/仓库从零创建新 Skill
- 重构现有 Skill（过长、不清晰、不一致、误触发）
- 设计可靠的激活机制（frontmatter + 触发器 + 边界）
- 从大型素材中提取简洁的快速参考
- 将长篇内容拆分为可导航的 `references/`
- 添加质量门控与验证器

## 禁止使用 / 边界

本元技能不适用于：
- 作为领域 Skill 本身使用（它是用来构建领域 Skill 的）
- 凭空捏造外部事实（素材无法证明时，如实说明并添加验证路径）
- 替代必要输入（输入缺失时，先提问 1-3 个问题再继续）

## 快速参考

### 交付物（必须产出）

输出内容必须包含：
1. 具体的目录结构（通常为 `.github/skills/<skill-name>/`）
2. 包含可判定触发器、边界与可复现示例的 `SKILL.md`
3. 长篇文档迁移至 `references/`，并附 `references/index.md`
4. 交付前检查清单（质量门控）

### 内置工具（必选）：Skill Seekers（本地副本）

本仓库在此元技能内内嵌了 Skill Seekers 源码，可从以下来源生成 Skill 初稿：
- 文档网站
- GitHub 仓库
- PDF 文件

初始化依赖（执行一次）：

```bash
python ./scripts/skill-seekers-bootstrap.py
```

运行 Skill Seekers（使用本地副本）：

```bash
python ./scripts/skill-seekers.py -- --version
python ./scripts/skill-seekers.py -- scrape --config ./scripts/Skill_Seekers-development/configs/react.json
python ./scripts/skill-seekers.py -- github --repo facebook/react --name react
```

将生成的 Skill 导入仓库规范的 `.github/skills/` 目录树：

```bash
python ./scripts/skill-seekers-import.py react
python ./scripts/skill-seekers-import.py react --force
```

更新本地副本快照（可选，需要网络）：

```bash
python ./scripts/skill-seekers-update.py
python ./scripts/skill-seekers-update.py --ref main
```

### 推荐目录结构（最小 -> 完整）

```
skill-name/
|-- SKILL.md              # 必需：带 YAML frontmatter 的入口文件
|-- references/           # 可选：长篇文档/证据/索引
|   `-- index.md          # 推荐：导航索引
|-- scripts/              # 可选：辅助脚本/自动化（优先 .py）
`-- assets/               # 可选：模板/配置/静态资源
```

最简版本只需一个 `SKILL.md`（`references/` 可后续添加）。

### YAML Frontmatter（必需）

```yaml
---
name: skill-name
description: "功能描述 + 使用时机（激活触发器）。"
---
```

Frontmatter 规则：
- `name` 必须匹配 `^[a-z][a-z0-9-]*$`，且应与目录名一致
- `description` 必须可判定（不能是"帮助处理 X"），并包含具体的触发关键词

### 最简 `SKILL.md` 骨架（可直接复制）

```markdown
---
name: my-skill
description: "[领域] 能力：包含 [能力1]、[能力2]。适用于 [可判定触发条件]。"
---

# my-skill 技能

一句话说明边界与交付物。

## 何时使用本技能

满足以下任意条件时触发：
- [触发器1：具体任务/关键词]
- [触发器2]
- [触发器3]

## 禁止使用 / 边界

- 本技能不会做什么（防止误触发与过度承诺）
- 必要输入；缺失时提问 1-3 个问题

## 快速参考

### 常用模式

**模式1：** 一行说明
```text
[可粘贴运行的命令/代码片段]
```

## 示例

### 示例1
- 输入：
- 步骤：
- 预期输出 / 验收标准：

### 示例2

### 示例3

## 参考资料

- `references/index.md`：导航索引
- `references/...`：按主题拆分的长篇文档

## 维护说明

- 来源：文档/仓库/规范（禁止凭空编造）
- 最后更新：YYYY-MM-DD
- 已知限制：明确超出范围的内容
```

### 编写规则（不可妥协）

1. 快速参考只放简短、可直接使用的模式
   - 尽量控制在 20 个模式以内。
   - 需要段落说明的内容放入 `references/`。
2. 激活必须可判定
   - Frontmatter `description` 应包含"做什么 + 何时用"及具体关键词。
   - "何时使用"必须列出具体任务/输入/目标，而非模糊的帮助文本。
   - "禁止使用 / 边界"为必填项，用于保证激活可靠性。
3. 禁止对外部细节吹牛
   - 素材无法证明时，如实说明并提供验证路径。
4. 辅助脚本优先 Python
  - `scripts/` 中新增辅助脚本时，优先使用 `.py`。
  - `.sh/.ps1` 应仅作为薄封装入口（设置环境并调用 `.py`）。
  - 仅在 Python 不可用或平台强依赖 shell 行为时，才允许脚本主体为 shell。

### 工作流（素材 -> Skill）

不可跳过步骤：
0. 若来源为文档站/GitHub 仓库/PDF：先用内置 Skill Seekers 工具生成初稿，再导入 `.github/skills/<skill-name>/`
1. 定义范围：编写 MUST/SHOULD/NEVER（三句话即可）
2. 提取模式：挑选 10-20 个高频模式（命令/代码片段/流程）
3. 添加示例：>= 3 个端到端示例（输入 -> 步骤 -> 验收）
4. 定义边界：超出范围的内容 + 必要输入
5. 拆分参考资料：将长文迁移至 `references/` 并编写 `references/index.md`
6. 执行门控：运行检查清单与验证器
7. 若需要自动化脚本：优先创建 `scripts/main.py`，再按需添加 `scripts/run.sh`/`scripts/run.ps1` 入口

### 质量门控（交付前检查清单）

最低检查项（完整版见 `references/quality-checklist.md`）：
1. `name` 匹配 `^[a-z][a-z0-9-]*$` 且与目录名一致
2. `description` 包含"做什么 + 何时用"及具体触发关键词
3. 包含"何时使用本技能"且触发器可判定
4. 包含"禁止使用 / 边界"以减少误触发
5. 快速参考 <= 20 个模式且每个模式可直接使用
6. 包含 >= 3 个可复现示例
7. 长篇内容在 `references/` 中，且 `references/index.md` 可导航
8. 不确定的内容包含验证路径（禁止吹牛）
9. 读起来像操作手册，而非文档堆砌

本地验证：

```bash
# 从仓库根目录（基础验证）
python ./.github/skills/skills-skills/scripts/validate-skill.py .github/skills/<skill-name>

# 从仓库根目录（严格验证）
python ./.github/skills/skills-skills/scripts/validate-skill.py .github/skills/<skill-name> --strict

# JSON 输出（适合 CI 集成）
python ./.github/skills/skills-skills/scripts/validate-skill.py .github/skills/<skill-name> --strict --format json

# 批量验证全部技能
python ./.github/skills/skills-skills/scripts/audit-skills.py --strict

# 从 .github/skills/skills-skills/ 目录（基础验证）
python ./scripts/validate-skill.py ../<skill-name>

# 从 .github/skills/skills-skills/ 目录（严格验证）
python ./scripts/validate-skill.py ../<skill-name> --strict
```

### 工具与模板

生成新 Skill 骨架：

```bash
# 从仓库根目录（生成到 ./.github/skills/）
python ./.github/skills/skills-skills/scripts/create-skill.py my-skill --full --output .github/skills

# 从 skills-skills/ 目录（生成到 ../ 即 ./.github/skills/）
python ./scripts/create-skill.py my-skill --full --output ..

# 最简骨架
python ./.github/skills/skills-skills/scripts/create-skill.py my-skill --minimal --output .github/skills
```

批量验证所有技能：

```bash
# 从仓库根目录（基础批量验证）
python ./.github/skills/skills-skills/scripts/audit-skills.py

# 跳过元技能自身
python ./.github/skills/skills-skills/scripts/audit-skills.py --skip skills-skills

# 严格模式 + JSON 输出（适合 CI）
python ./.github/skills/skills-skills/scripts/audit-skills.py --strict --format json
```

模板文件：
- `assets/template-minimal.md`
- `assets/template-complete.md`

## 示例

### 示例1：从文档创建 Skill

- 输入：官方文档/规范 + 2-3 个真实代码样例 + 常见失败模式
- 步骤：
  1. 运行 `create-skill.py` 生成 `.github/skills/<skill-name>/` 脚手架
  2. 按"做什么 + 何时用"编写 frontmatter `description`
  3. 提取 10-20 个高频模式到快速参考
  4. 添加 >= 3 个带验收标准的端到端示例
  5. 将长篇内容放入 `references/` 并关联 `references/index.md`
  6. 运行 `validate-skill.py --strict` 并迭代优化

### 示例2：重构"文档堆砌"型 Skill

- 输入：现有的包含大量粘贴文档的 `SKILL.md`
- 步骤：
  1. 区分哪些是模式，哪些是长篇说明
  2. 将长篇文本迁移至 `references/`（按主题拆分）
  3. 将快速参考改写为简短的可粘贴模式
  4. 添加或修复示例，直到可复现为止
  5. 添加"禁止使用 / 边界"以减少误触发

### 示例3：验证并执行质量门控

- 输入：`.github/skills/<skill-name>/`
- 步骤：
  1. 运行 `validate-skill.py`（非严格模式）获取警告
  2. 修复 frontmatter/name 不匹配及缺失章节
  3. 运行 `validate-skill.py --strict` 强制执行规范
  4. 发布前运行 `references/quality-checklist.md` 中的评分标准

## 参考资料

本地文档：
- `references/index.md`
- `references/skill-spec.md`
- `references/quality-checklist.md`
- `references/anti-patterns.md`
- `references/README.md`（上游官方参考）
- `references/skill-seekers.md`（内置工具集成 + 工作流）

外部资源（官方）：
- https://support.claude.com/en/articles/12512176-what-are-skills
- https://support.claude.com/en/articles/12512180-using-skills-in-claude
- https://support.claude.com/en/articles/12512198-creating-custom-skills
- https://docs.claude.com/en/api/skills-guide

## 维护说明

- 来源：`.github/skills/skills-skills/references/` 中的本地规范文件 + `references/README.md` 中的上游官方文档
- 最后更新：2026-05-03
- 已知限制：`validate-skill.py` 为启发式验证；严格模式假定使用推荐的章节标题
