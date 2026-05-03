# 影响分析 — skills-skills/scripts/

> 生成时间: 2026-05-03  
> 范围: .github/skills/skills-skills/scripts/  
> 方法: 静态分析 (Python import + 函数调用链)

---

## 依赖关系图（模块级）

`
create-skill.sh
  └── create-skill.py
        ├── assets/template-minimal.md     (读取)
        └── assets/template-complete.md    (读取)

validate-skill.sh
  └── validate-skill.py
        └── <skill_dir>/SKILL.md           (读取验证)

skill-seekers.sh
  └── skill-seekers.py
        ├── .venv-skill-seekers/           (venv python)
        └── Skill_Seekers-development/src/ (PYTHONPATH注入)
              └── skill_seekers.cli.main   (委托执行)

skill-seekers-bootstrap.sh
  └── skill-seekers-bootstrap.py
        ├── .venv-skill-seekers/           (写入/创建)
        └── Skill_Seekers-development/     (pip install -e)

skill-seekers-import.sh
  └── skill-seekers-import.py
        ├── <repo>/output/<name>/          (读取来源)
        └── <repo>/.github/skills/<name>/ (写入目标)

skill-seekers-update.sh
  └── skill-seekers-update.py
        ├── GitHub tarball                 (网络下载)
        └── Skill_Seekers-development/     (写入/替换)
`

---

## 高风险耦合点

| 风险点 | 文件 | 说明 | 级别 |
|:--|:--|:--|:--:|
| templates 路径硬编码 | create-skill.py:38 | 依赖 ../assets/template-*.md，移动 SKILL 目录会崩溃 | 高 |
| vendored source 路径 | skill-seekers.py:16 | Skill_Seekers-development/src/ 必须存在 | 高 |
| parents[4] 假定层级 | skill-seekers-import.py:21 | Path(__file__).resolve().parents[4] 假定固定目录深度 | 中 |
| 先删后写无事务 | skill-seekers-import.py:38-47 | 清空 dest_dir 后若 copy 中途失败，dest 将不完整 | 中 |
| 全量替换 vendored | skill-seekers-update.py | 无版本回滚机制 | 中 |
| wslpath 路径转换 | skill-seekers.py:45-51 | 仅在 WSL 下检测，Windows native 下无问题 | 低 |

---

## 变更影响矩阵

| 若改动 | 影响范围 |
|:--|:--|
| ssets/template-minimal.md | create-skill.py 渲染输出 → 所有 --minimal 生成产物 |
| ssets/template-complete.md | create-skill.py → 所有 --full 生成产物 |
| Skill_Seekers-development/src/ | skill-seekers.py（CLI失效）+ skill-seekers-bootstrap.py（editable install）|
| REQUIRED_SECTIONS 常量 | alidate-skill.py → 所有现存 SKILL.md 验证结果 |
| .venv-skill-seekers/ | skill-seekers.py（需重新 bootstrap）|
| skill-seekers-update.py 的过滤规则 | vendored source 的内容组成 |

---

## 回归测试最小集

1. python validate-skill.py .github/skills/skills-skills --strict → OK
2. python create-skill.py test-x --minimal --output /tmp/test-out → 生成+验证
3. python create-skill.py test-x --full --output /tmp/test-out --force → main.py 存在
4. python skill-seekers.py --version → skill-seekers 2.1.1
5. python skill-seekers-import.py nonexistent → exit 1，清晰错误消息
6. python skill-seekers-update.py --dry-run → 打印计划，exit 0
