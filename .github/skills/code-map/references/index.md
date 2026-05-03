# code-map 参考索引

## 快速入口

- 入门与术语：`getting_started.md`
- 命令与输出格式：`api.md`
- 语义与向量标准：`semantic-standard.md`
- 长篇实战案例：`examples.md`
- 故障排查与边界：`troubleshooting.md`

## 追踪脚本

- Bash：`.github/skills/code-map/scripts/update-codemap.sh`
- PowerShell：`.github/skills/code-map/scripts/update-codemap.ps1`
- 语义检索：`.github/skills/code-map/scripts/semantic-search.ps1`

## 推荐阅读顺序

1. 先看 `getting_started.md` 明确输出目标与流程
2. 再按技术栈选取 `api.md` 的命令模板
3. 参考 `examples.md` 产出完整地图文档
4. 遇到异常时查 `troubleshooting.md`

## 产物清单建议

- `structure-map.txt`：文件级结构地图
- `dependency-graph.svg` 或 `dependency-graph.mmd`：模块关系图
- `context-cards.md`：模块上下文卡片
- `impact-analysis.md`：变更影响分析
- `change-tracking.md`：跟随更新差异
- `semantic-corpus.jsonl`：语义语料
- `semantic-vectors.jsonl`：语义向量索引
- `semantic-standard.json`：语义向量标准
- `manifest.json`：执行元数据（时间、范围、命令、产物）
