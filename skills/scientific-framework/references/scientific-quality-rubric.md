# Scientific QA（先于生成draw.io）

Agent对照固定原文核查：核心问题完整；术语未改；内容/任务/方法/进度区分；无新增因果；每条关键边是否真被来源支持；比较/影响/因果/证据/检验/时间各自明确；预期保留预期；不确定性不被消除；不为对称合并概念。

validate_ir程序核对Schema、ID、端点、引用、逐字引文、片段hash、状态、包含循环和核心待审门槛。它不能验证引文是否蕴含关系，不能从术语自动证明科研分类，也不能用高confidence证明科学真实性。Agent必须先完成summary和issues。

errors=契约/来源错误，不允许生成；blockers=科学待审或不足，可生成draft，不能approved；warnings=限度或需要观察事项。core节点缺来源由Schema拒绝；core关系无证据/待审阻止批准。无证据causes无论core与否均阻止批准。

Scientific QA和Visual QA独立；好看或结构校验通过不消除科学blockers。人工确认只有在来源问题解决并重新校验后才能提升状态，不能简单改字符串。
