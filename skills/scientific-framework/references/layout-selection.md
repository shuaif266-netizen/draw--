# 结构选择与显示投影

Agent先基于IR提出2–3个方向，写diagram_directions.md。每项说明主线、主要模块、压缩、优点、风险与适合的实际关系；不能只换颜色。科研不适合某结构时说明原因，不为凑数创造机制/闭环。

M1实现三个ID：

| ID | 主层 | 辅助层/风险 |
|---|---|---|
| overall_research_approach_vertical | 真实问题/内容/过程/目标/机制/产出 | 方法、任务、证据侧层；上下相邻不表示有关系 |
| question_content_method_three_column | 中栏研究内容 | 左侧问题/目标，右侧共享方法；只创建一个方法节点，不按行复制 |
| content_evidence_dual_layer | 上层内容/问题 | 下层任务、方法、数据/证据、进度；不按数量一一连边 |

diagram_scene.py只按确定类型和level布局，不进行语义推断。自动init layout包含全部IR节点；Agent可改display_node_ids和omitted_nodes，但须显式说明遗漏理由。核心节点不可省略；跨省略节点的关系记录为未显示，并阻止approved。M1不支持视觉聚合（预留扩展），保持一节点一实体更可核查。

layout以ir_sha256绑定语义快照；不接受标签/type覆盖。status不能高于IR，待审核心关系或未完成Agent审查不能批准。容器可嵌套，但不用于暗示未经确认的科学归属。只有明确的容器与node_ids才建立展示父子关系。
