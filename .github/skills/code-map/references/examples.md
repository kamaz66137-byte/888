# 长篇示例

## 示例 1：陌生仓库 30 分钟建图

目标：在半小时内输出结构图、关系图和 1 页上下文摘要。

步骤：

1. 结构扫描

```bash
rg --files > structure-map.txt
```

2. 导入关系扫描

```bash
rg "^import |require\(" -n src > imports-tsjs.txt
rg "^(from |import )" -n src > imports-python.txt
```

3. TypeScript 依赖图（可选）

```bash
npx madge src --extensions ts,tsx,js,mjs --image dependency-graph.svg
```

4. 输出上下文摘要（建议结构）

```text
- 核心入口：src/main.ts
- 业务分层：controller -> service -> repository
- 高耦合模块：src/shared/state.ts
- 风险点：跨层调用、循环依赖、全局可变状态
```

验收：
- 输出文件齐全：`structure-map.txt`、`dependency-graph.svg`、`context-summary.md`
- 每个结论都能回链到具体证据

## 示例 2：重构前引用关系审计

目标：重构模块前先拿到影响面与回归策略。

输入：`src/service/payment`

步骤：

1. 查找直接引用

```bash
rg "payment" -n src > payment-refs.txt
```

2. 构建影响清单

```text
变更点: src/service/payment
直接影响: controller/order.ts, worker/settlement.ts
间接影响: reports/daily.ts
关键链路: 下单 -> 支付 -> 对账 -> 报表
```

3. 形成测试建议

```text
- 单测: payment service rule branches
- 集成: order -> payment success/fail paths
- 回归: settlement worker and report generation
```

验收：
- `impact-analysis.md` 包含直接/间接影响与测试建议
- 明确上线观察指标与回滚条件

## 示例 3：线上缺陷的调用链回溯

目标：从日志关键字快速定位根因链路。

输入：日志关键字 `InventoryLockedError`

步骤：

1. 全局定位符号

```bash
rg "InventoryLockedError" -n src
```

2. 定位抛错点和入口调用

```bash
rg "throw new InventoryLockedError|InventoryLockedError\(" -n src
```

3. 输出回溯链路

```text
api/order/create -> service/order -> service/inventory -> InventoryLockedError
```

4. 提供修复上下文

```text
可能原因: 并发锁未释放 / 重试策略缺失
修复建议: finally 中强制释放锁；幂等键补充；冲突时降级返回
验证步骤: 压测并发下单 1000 次，检查锁残留与错误率
```

验收：
- 链路图与修复建议同一文档可复现
- 验证步骤可执行并可量化
