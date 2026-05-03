---
name: code-map
description: "代码地图构建能力：生成项目结构地图、模块关系图、上下文建构与引用关系分析。适用于快速理解陌生代码库、定位影响范围、评估重构风险。"
---

# code-map 技能

面向代码库理解与影响分析的技能：输出结构地图、关系图、上下文文档和引用链路，帮助在改动前建立可验证的全局认知。

## 何时使用本技能

满足以下任意条件时触发：
- 首次接手一个项目，需要快速理解目录、模块、边界和主流程
- 准备重构或替换模块，需要评估改动影响面
- 处理线上缺陷，需要追踪调用链与被依赖关系
- 做技术方案评审，需要产出可沟通的架构关系图
- 需要把口头认知沉淀为文档化上下文（便于团队协作）

## 禁止使用 / 边界

- 不直接修改业务代码；仅构建地图、关系和分析结论
- 不承诺 100% 精准静态分析；动态反射/运行时注入需结合运行日志
- 不在缺失关键上下文时强行结论；必要时先补充以下输入：
  - 技术栈（Python/Node.js/混合）
  - 目标范围（全仓库/子目录/单模块）
  - 输出形式（Markdown 地图/Graphviz/Mermaid/CSV）

## 快速参考

### 常用模式

**固定落盘位置（必须）**
```text
<repo>/artifacts/code-map/
  latest/                     # 最近一次完整产物
  history/<yyyyMMdd-HHmmss>/ # 每次运行的历史快照
```

**Node 项目范围规则（必须）**
```text
仅构建 src/ 目录。
若传入其它 scope，脚本会自动强制改为 src/。
若 src/ 不存在则直接报错停止。
```

**标准产物（必须）**
```text
structure-map.txt      # 文件结构地图
language-stats.txt     # 语言/扩展名统计
imports-python.txt     # Python 导入关系（可为空）
imports-tsjs.txt       # TS/JS 导入关系（可为空）
context-cards.md       # 模块上下文卡片
impact-analysis.md     # 影响分析
change-tracking.md     # 与上次快照差异
semantic-corpus.jsonl  # 语义语料（统一 schema）
semantic-vectors.jsonl # 稀疏向量索引（256 维）
semantic-standard.json # 语义与向量标准定义
manifest.json          # 元数据与命令记录
```

**模式1：生成目录结构地图（Windows PowerShell）**
```text
Get-ChildItem . -Recurse -File | ForEach-Object { $_.FullName.Replace((Get-Location).Path + '\\','') } | Out-File structure-map.txt -Encoding utf8
```

**模式2：生成目录结构地图（Bash）**
```text
rg --files > structure-map.txt
```

若 `rg` 不可用：
```text
find . -type f | sed 's#^./##' > structure-map.txt
```

**模式3：按语言统计代码体量**
```text
rg --files | awk -F. 'NF>1{ext=$NF; c[ext]++} END{for(e in c) print e, c[e]}' | sort
```

**模式4：提取导入关系（Python）**
```text
rg "^(from |import )" -n src > imports-python.txt
```

**模式5：提取导入关系（TS/JS）**
```text
rg "^import |require\(" -n src > imports-tsjs.txt
```

**模式6：生成 TypeScript 依赖图（madge）**
```text
npx madge src --extensions ts,tsx,js,mjs --image dep-graph.svg
```

**模式7：查找符号引用（文本级）**
```text
rg "symbolName" -n src
```

**模式8：构建模块上下文卡片（模板）**
```text
模块: <name>
职责: <single sentence>
输入: <public API / params>
输出: <return / side effects>
依赖: <calls/imports>
被依赖: <callers/importers>
风险: <tight coupling / global state>
```

**模式9：导出 Graphviz 关系图（DOT）**
```text
digraph G { "api" -> "service"; "service" -> "repo"; }
```

**模式10：输出变更影响清单**
```text
目标文件 -> 直接引用方 -> 间接引用方 -> 关键测试点
```

**模式11：增量追踪并更新 codemap（Bash）**
```text
bash .github/skills/code-map/scripts/update-codemap.sh src
```

**模式12：增量追踪并更新 codemap（PowerShell）**
```text
powershell -ExecutionPolicy Bypass -File .github/skills/code-map/scripts/update-codemap.ps1 -Scope src
```

**模式13：语义检索（PowerShell）**
```text
powershell -ExecutionPolicy Bypass -File .github/skills/code-map/scripts/semantic-search.ps1 -Query "支付失败重试" -TopK 10
```

## 规则与约束

- MUST：地图输出必须含来源依据（命令、路径、符号或搜索结果）
- MUST：先给范围再分析，避免把无关目录混入结论
- MUST：结论区分“确定事实”和“推断项”
- MUST：所有产物必须落盘到 `artifacts/code-map/`，禁止散落在仓库根目录
- MUST：每次更新必须写入历史快照，并同步覆盖 `latest/`
- MUST：`manifest.json` 必须记录时间、范围、命令、产物列表
- MUST：Node 项目只扫描 `src/`，禁止把 `node_modules/` 或仓库其它目录构建为项目地图
- MUST：语义向量标准统一为 `hashing-tf + 256 维 + l2 归一化 + cosine`
- MUST：语义检索与向量构建必须使用同一 tokenizer 与同一维度
- SHOULD：结构图、依赖图、调用链至少产出两种视角
- SHOULD：结合语言工具（LSP/静态分析）与文本搜索交叉验证
- NEVER：不凭主观猜测补全未验证关系
- NEVER：不在图中泄露密钥、令牌、隐私路径

## 示例

### 示例1：新项目接手（全局建图）
- 输入：仓库根目录 + 目标语言
- 步骤：
  1. 运行 `update-codemap.sh` 生成首个快照
  2. 输出模块分层（接口层/服务层/数据层）
  3. 生成依赖图（SVG 或 Mermaid）
  4. 为核心模块编写上下文卡片
- 预期输出 / 验收标准：
  - `artifacts/code-map/history/<timestamp>/` 产物完整
  - `artifacts/code-map/latest/` 与最新快照一致
  - 有 1 份结构地图 + 1 张关系图 + >=5 个模块卡片
  - 每条关系可追溯到具体文件或符号

### 示例2：重构前影响分析
- 输入：待重构模块路径（如 `src/service/payment`）
- 步骤：
  1. 运行 `update-codemap.sh src/service/payment`
  2. 查找直接 import/call 引用
  3. 标注高风险耦合点（全局状态、跨层调用、循环依赖）
  4. 给出分批重构顺序与回归测试建议
- 预期输出 / 验收标准：
  - `change-tracking.md` 展示与上次快照差异
  - 形成“影响范围清单”
  - 明确关键回归路径和最低测试集

### 示例3：缺陷定位调用链回溯
- 输入：报错点（函数名/文件路径/日志关键字）
- 步骤：
  1. 定位报错符号定义与调用点
  2. 追踪入口到报错点的主链路
  3. 补充关键配置和环境分支差异
  4. 输出修复上下文文档（含验证步骤）
- 预期输出 / 验收标准：
  - 链路起点与终点明确
  - 修复建议与验证步骤可执行

## 常见问题

- Q: 文本搜索和静态分析结果冲突怎么办？
  - A: 先以静态分析为主，再用文本搜索补充动态调用或字符串拼接场景。
- Q: 单仓库太大，图太杂如何处理？
  - A: 先按业务域拆分子图，再汇总顶层关系图。
- Q: 无法解析某些框架约定式路由？
  - A: 引入框架专用工具或运行时日志，补齐约定到实际文件的映射。

## 故障排查

- 关系图为空 -> 输入路径错误 / 忽略规则过宽 -> 检查扫描根路径与 exclude 配置 -> 缩小范围重跑
- 依赖图过大不可读 -> 范围过广 -> 按模块分组输出子图 -> 再做汇总图
- 引用缺失 -> 仅靠文本搜索 -> 增加 LSP 引用查询或语言专用分析工具
- 结论不稳定 -> 未记录命令与版本 -> 在产物中记录命令、时间、分支和提交号

## 参考资料

- `references/index.md`：导航索引
- `references/getting_started.md`：建图流程、术语与产物规范
- `references/api.md`：命令模板与输出格式参考
- `references/examples.md`：端到端产物示例
- `references/troubleshooting.md`：常见失败模式与修复路径

## 脚本

- `scripts/update-codemap.sh`：Bash 增量追踪生成器
- `scripts/update-codemap.ps1`：PowerShell 增量追踪生成器
- `scripts/semantic-search.ps1`：语义检索脚本（基于统一稀疏向量）

## 维护说明

- 来源：代码检索实践、静态分析常用工具链（rg/madge/LSP）
- 最后更新：2026-05-03
- 已知限制：动态加载、反射、运行时拼接关系需结合运行时证据

## 质量门控

发布前最低检查项（完整版见元技能 `skills-skills`）：

1. `description` 可判定（"做什么 + 何时用"）且包含触发关键词
2. 包含"何时使用本技能"且触发器可判定
3. 包含"禁止使用 / 边界"以减少误触发
4. 快速参考 <= 20 个模式且每个模式可直接使用
5. 包含 >= 3 个可复现示例（输入 -> 步骤 -> 验收）
6. 长篇内容在 `references/` 中，且有可导航的 `references/index.md`
7. 不确定的内容包含验证路径（禁止吹牛）
8. 快速参考中无文档堆砌
9. 读起来像操作手册，而非知识堆砌
