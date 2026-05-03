# 模块上下文卡片 — skills-skills/scripts/

> 范围: .github/skills/skills-skills/scripts/  
> 语言: Python 3.12 (主) + Bash (thin wrappers)  
> 生成时间: 2026-05-03

---

## create-skill.py

| 字段 | 内容 |
|:--|:--|
| 职责 | 生成新技能的目录脚手架（SKILL.md + assets/ scripts/ references/） |
| 模式 | --minimal（最小）/ --full（含 references 子文档 + scripts/main.py） |
| 输入 | skill_name (positional), --output (目标父目录), --force (覆盖保护) |
| 输出 | 目标目录树 + SKILL.md（基于模板渲染） |
| 关键依赖 | ssets/template-minimal.md, ssets/template-complete.md |
| 被依赖 | create-skill.sh (thin wrapper) |
| 风险 | 模板文件缺失时直接 SystemExit；--force 全量覆盖无恢复 |

---

## validate-skill.py

| 字段 | 内容 |
|:--|:--|
| 职责 | 验证 SKILL.md 格式：frontmatter、必填字段、章节完整性 |
| 严格模式 | --strict：同时校验 
ame pattern + 所有必需章节 |
| 必需章节 | 何时使用/禁止使用/快速参考/示例/参考资料/维护说明（中英文） |
| 输入 | skill_dir (path to skill directory) |
| 输出 | stdout OK: <path> 或 stderr 错误信息，exit code 0/1 |
| 被依赖 | alidate-skill.sh (thin wrapper) |
| 风险 | YAML frontmatter 未闭合时 SystemExit，不做 graceful 恢复 |

---

## skill-seekers.py

| 字段 | 内容 |
|:--|:--|
| 职责 | 通过 .venv-skill-seekers venv 调度 skill_seekers.cli.main |
| 关键逻辑 | 
esolve_python() 优先 venv python，回退 system python |
| WSL 兼容 | 检测 wslpath，自动转换 PYTHONPATH 为 Windows 路径 |
| 输入 | 所有 args 透传给 skill_seekers.cli.main（passthrough） |
| 依赖 | Skill_Seekers-development/src/（vendored source），.venv-skill-seekers/ |
| 被依赖 | skill-seekers.sh (thin wrapper) |
| 风险 | vendored source 或 venv 不存在时 SystemExit；Windows/WSL 路径转换可能失败 |

---

## skill-seekers-bootstrap.py

| 字段 | 内容 |
|:--|:--|
| 职责 | 创建并初始化 .venv-skill-seekers venv（pip install + editable install） |
| 步骤 | venv create → pip upgrade → requirements.txt → pip install -e tool_dir |
| 输入 | --venv (可选，自定义 venv 路径) |
| 依赖 | Skill_Seekers-development/requirements.txt |
| 被依赖 | skill-seekers-bootstrap.sh |
| 风险 | 网络失败会抛出 subprocess 异常；tool_dir 缺失时 SystemExit |

---

## skill-seekers-import.py

| 字段 | 内容 |
|:--|:--|
| 职责 | 将 output/<skill_name>/ 导入到 .github/skills/<skill_name>/ |
| 覆盖保护 | 目标已存在 SKILL.md 时需 --force，否则 SystemExit |
| 导入逻辑 | 先清空 dest_dir，再 rglob 复制 src_dir（保持目录结构） |
| 输入 | skill_name (positional), --force |
| 源目录 | <repo_root>/output/<skill_name>/ |
| 目标目录 | <repo_root>/.github/skills/<skill_name>/ |
| 被依赖 | skill-seekers-import.sh |
| 风险 | 先删后写，中途失败会导致 dest_dir 不完整 |

---

## skill-seekers-update.py

| 字段 | 内容 |
|:--|:--|
| 职责 | 从 GitHub 下载 Skill_Seekers tarball，更新 vendored source |
| 来源 | https://codeload.github.com/{repo}/tar.gz/{ref} |
| 过滤 | 排除 .git/, docs/, 	ests/, CHANGELOG.md 等文档 |
| 安全模式 | --dry-run 仅打印计划，不执行覆盖 |
| 输入 | --repo, --ref, --dry-run |
| 依赖 | urllib.request, 	arfile（stdlib only） |
| 被依赖 | skill-seekers-update.sh |
| 风险 | 全量替换 vendored source，GitHub 不可达时 URLError |

---

## Shell Wrappers（*.sh）

所有 .sh 文件均为 **thin wrappers**，逻辑为：
1. 查找 python.exe / python3 / python  
2. 将所有参数委托给对应 .py 文件  
3. 不包含任何业务逻辑

| 文件 | 委托目标 |
|:--|:--|
| create-skill.sh | create-skill.py |
| alidate-skill.sh | alidate-skill.py |
| skill-seekers.sh | skill-seekers.py |
| skill-seekers-bootstrap.sh | skill-seekers-bootstrap.py |
| skill-seekers-import.sh | skill-seekers-import.py |
| skill-seekers-update.sh | skill-seekers-update.py |
