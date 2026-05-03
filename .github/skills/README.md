# Skills 总览索引

本目录包含所有可复用的 **Skills（技能模块）**。每个技能以 `SKILL.md` 为入口，定义触发条件、边界与交付物。

## 技能目录

| 技能名 | 触发场景（何时用） | 入口文件 |
|:---|:---|:---|
| **code-map** | 首次接手项目建立全局认知、重构前影响分析、缺陷定位调用链追踪 | [code-map/SKILL.md](code-map/SKILL.md) |
| **deepseek-api** | 调用 DeepSeek API（Chat/工具调用/流式）、构建 DeepSeek Agent、调试 API 报错 | [deepseek-api/SKILL.md](deepseek-api/SKILL.md) |
| **headless-cli** | PowerShell 批量调用 DeepSeek（翻译/审查/格式化）、无人值守 AI 任务、YOLO 模式脚本 | [headless-cli/SKILL.md](headless-cli/SKILL.md) |
| **tmux-autopilot** | 读取/广播 tmux pane 输出、批量巡检多 AI 终端、蜂群 Agent 协作、卡死救援 | [tmux-autopilot/SKILL.md](tmux-autopilot/SKILL.md) |
| **zkali-mcp** | 构建 Python MCP Server（工具契约/sqlite3 持久化）、新增/修改 MCP 工具模块 | [zkali-mcp/SKILL.md](zkali-mcp/SKILL.md) |
| **skills-skills** | 从文档/规范/仓库创建新 Skill、重构现有 Skill、执行质量门控验证 | [skills-skills/SKILL.md](skills-skills/SKILL.md) |

## 快速工具

```bash
# 生成新技能骨架
python .github/skills/skills-skills/scripts/create-skill.py <skill-name> --full --output .github/skills

# 验证技能规范（基础 / 严格）
python .github/skills/skills-skills/scripts/validate-skill.py .github/skills/<skill-name>
python .github/skills/skills-skills/scripts/validate-skill.py .github/skills/<skill-name> --strict
```

## 操作规范

详见 [AGENTS.md](AGENTS.md)。新增技能请遵循 [skills-skills/SKILL.md](skills-skills/SKILL.md) 中的工作流与质量门控清单。
