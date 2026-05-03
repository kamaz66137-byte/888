# 语义化与向量标准（v1.0）

## 目标

- 让 codemap 产物具备可检索的语义结构
- 用统一向量标准保证构建与检索一致
- 将语义检索结果可追溯到具体文件路径

## 语义建模对象

- 范围：仅 `src/`
- 单元：文件级 chunk（一个文件一个语义记录）
- 记录主键：`cm_<sha1(path)>`

## 统一记录 Schema

`semantic-corpus.jsonl` 每行一个 JSON：

```json
{
  "schema_version": "1.0",
  "id": "cm_xxx",
  "type": "file",
  "path": "src/module/a.ts",
  "title": "a",
  "domain": "module",
  "extension": "ts",
  "tokens": ["src", "module", "a", "ts"],
  "text": "path src/module/a.ts title a domain module extension ts",
  "source": "code-map"
}
```

## 向量标准

- 算法：`hashing-tf`
- 维度：`256`
- tokenizer：`unicode-lower-split-nonalnum`
- 归一化：`l2`
- 相似度：`cosine`
- 检索默认 TopK：`10`

`semantic-vectors.jsonl` 每行一个 JSON：

```json
{
  "schema_version": "1.0",
  "id": "cm_xxx",
  "path": "src/module/a.ts",
  "vector": {
    "dim": 256,
    "indices": [2, 17, 93],
    "values": [0.58, 0.58, 0.58]
  }
}
```

## 一致性约束

- 构建脚本与搜索脚本必须使用同一 tokenizer
- 构建脚本与搜索脚本必须使用同一维度（256）
- 构建脚本与搜索脚本必须使用同一相似度（cosine）
- 若升级维度或算法，必须提升 `schema_version`

## 演进方案

- v1.0：文件级语义 + 稀疏哈希向量
- v1.1（建议）：增加函数/类级 chunk
- v2.0（建议）：替换为模型 embedding（保持 schema 兼容层）
