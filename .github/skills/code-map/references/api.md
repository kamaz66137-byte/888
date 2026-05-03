# 命令与输出格式参考

## 落盘位置（统一）

所有产物统一写入：

```text
artifacts/code-map/
	latest/
	history/<yyyyMMdd-HHmmss>/
```

规则：
- 每次执行创建 `history/<timestamp>/`
- 同步刷新 `latest/` 为本次结果
- 任何临时文件不得写在仓库根目录

## 范围限制（强制）

- 仅允许扫描 `src/`
- 即使传入其它 scope，脚本也会自动收敛到 `src/`
- 若 `src/` 不存在，脚本会报错并停止

## 输出标准（固定文件名）

| 文件名 | 必须 | 说明 |
|---|---|---|
| `structure-map.txt` | 是 | 文件结构地图（相对路径） |
| `language-stats.txt` | 是 | 扩展名统计 |
| `imports-python.txt` | 是 | Python 导入扫描（无结果可空） |
| `imports-tsjs.txt` | 是 | TS/JS 导入扫描（无结果可空） |
| `context-cards.md` | 是 | 核心模块上下文卡片 |
| `impact-analysis.md` | 是 | 影响分析模板填充结果 |
| `change-tracking.md` | 是 | 与上次快照的新增/删除/变化 |
| `semantic-corpus.jsonl` | 是 | 语义语料（统一 schema） |
| `semantic-vectors.jsonl` | 是 | 稀疏向量索引 |
| `semantic-standard.json` | 是 | 语义与向量标准 |
| `manifest.json` | 是 | 元数据：时间、范围、命令、产物 |

## 通用扫描命令

### 一键增量追踪（推荐）

```bash
bash .github/skills/code-map/scripts/update-codemap.sh src
```

```powershell
powershell -ExecutionPolicy Bypass -File .github/skills/code-map/scripts/update-codemap.ps1 -Scope src
```

### 语义检索

```powershell
powershell -ExecutionPolicy Bypass -File .github/skills/code-map/scripts/semantic-search.ps1 -Query "订单支付失败" -TopK 10
```

## 统一语义向量标准（v1.0）

- 语义单元：文件级（仅 `src/`）
- 文本模板：`path + title + domain + extension`
- tokenizer：`unicode-lower-split-nonalnum`
- 向量算法：`hashing-tf`
- 向量维度：`256`
- 归一化：`l2`
- 相似度：`cosine`
- 默认返回：`TopK=10`

### 文件结构扫描

```bash
rg --files > structure-map.txt
```

若环境无 `rg`：

```bash
find . -type f | sed 's#^./##' > structure-map.txt
```

```powershell
Get-ChildItem . -Recurse -File |
	ForEach-Object { $_.FullName.Replace((Get-Location).Path + '\\','') } |
	Out-File structure-map.txt -Encoding utf8
```

### 导入与引用扫描

```bash
rg "^(from |import )" -n src > imports-python.txt
rg "^import |require\(" -n src > imports-tsjs.txt
```

```bash
rg "函数名|类名|symbolName" -n src > symbol-refs.txt
```

## 关系图工具

### TypeScript / JavaScript（madge）

```bash
npx madge src --extensions ts,tsx,js,mjs --image dependency-graph.svg
npx madge src --extensions ts,tsx,js,mjs --circular
```

输出：
- `dependency-graph.svg`：依赖图
- 终端循环依赖列表

### Graphviz（DOT）

示例 DOT：

```dot
digraph G {
	rankdir=LR;
	"controller" -> "service";
	"service" -> "repository";
}
```

渲染：

```bash
dot -Tsvg architecture.dot -o architecture.svg
```

## 输出模板

### 上下文卡片模板

```text
模块：<name>
职责：<single sentence>
入口：<routes/commands/events>
输入：<params/contracts>
输出：<result/side effects>
依赖：<imports/calls>
被依赖：<callers>
风险：<global state/circular dep/hot path>
证据：<file:line or command output>
```

### 影响分析模板

```text
变更点：<path or symbol>
直接影响：<direct callers/importers>
间接影响：<transitive consumers>
高风险路径：<critical flows>
建议测试：<unit/integration/e2e>
回滚预案：<feature flag/compat mode>
```

## 常见误用

- 只看 import 不看运行时入口，导致漏掉事件驱动链路
- 全仓库一次性建图，结果图过大不可用
- 不记录命令参数，导致他人无法复现你的地图
- 只生成当前结果，不保留历史快照，无法追踪演进
