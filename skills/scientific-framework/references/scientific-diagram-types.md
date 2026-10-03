# 科研图型选择库

12类均有选择指南；M1只有layout-selection.md所列三种可运行布局，其他不宣称已实现。

## 总体研究思路框架图

```json
{
  "purpose": "研究怎样推进",
  "suitable_content_structure": "阶段推进有原文依据",
  "unsuitable_cases": "阶段顺序未明",
  "reading_direction": "TB",
  "main_backbone": "入口/问题/研究阶段/产物",
  "recommended_major_modules": [
    "入口",
    "问题",
    "研究阶段",
    "产物"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "对象",
    "方法",
    "任务",
    "进度"
  ],
  "preferred_edge_semantics": [
    "temporal_before",
    "addresses",
    "produces"
  ],
  "common_failure_modes": [
    "把相邻模块连成因果"
  ]
}
```

## 研究框架图

```json
{
  "purpose": "问题目标内容支撑",
  "suitable_content_structure": "内容层级清楚",
  "unsuitable_cases": "仅章节目录",
  "reading_direction": "TB",
  "main_backbone": "问题/目标/内容",
  "recommended_major_modules": [
    "问题",
    "目标",
    "内容"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "方法",
    "资料",
    "证据"
  ],
  "preferred_edge_semantics": [
    "contains",
    "supports"
  ],
  "common_failure_modes": [
    "将目录当研究关系"
  ]
}
```

## 技术路线图

```json
{
  "purpose": "资料如何处理转换",
  "suitable_content_structure": "输入处理验证有依据",
  "unsuitable_cases": "并列内容无时序",
  "reading_direction": "LR/TB",
  "main_backbone": "输入/处理/验证/输出",
  "recommended_major_modules": [
    "输入",
    "处理",
    "验证",
    "输出"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "方法",
    "条件"
  ],
  "preferred_edge_semantics": [
    "transforms_to",
    "validates"
  ],
  "common_failure_modes": [
    "凭空补技术阶段"
  ]
}
```

## 研究设计图

```json
{
  "purpose": "条件任务采集分析",
  "suitable_content_structure": "有对象条件及对照",
  "unsuitable_cases": "无设计材料",
  "reading_direction": "LR",
  "main_backbone": "对象/条件/任务/采集",
  "recommended_major_modules": [
    "对象",
    "条件",
    "任务",
    "采集"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "方法",
    "证据"
  ],
  "preferred_edge_semantics": [
    "applies_to",
    "compares_with"
  ],
  "common_failure_modes": [
    "暗示未提供的随机化"
  ]
}
```

## 机制图

```json
{
  "purpose": "作用命题与检验",
  "suitable_content_structure": "有明确或待检验作用关系",
  "unsuitable_cases": "只有工作步骤",
  "reading_direction": "LR/network",
  "main_backbone": "机制路径",
  "recommended_major_modules": [
    "机制路径"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "条件",
    "证据"
  ],
  "preferred_edge_semantics": [
    "influences",
    "validates"
  ],
  "common_failure_modes": [
    "假设画成已证实"
  ]
}
```

## 问题—内容—方法三栏

```json
{
  "purpose": "内容为主方法支撑",
  "suitable_content_structure": "问题内容方法有真实映射",
  "unsuitable_cases": "行对齐会误导共享方法",
  "reading_direction": "LR",
  "main_backbone": "中间内容",
  "recommended_major_modules": [
    "中间内容"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "左右问题",
    "共享方法"
  ],
  "preferred_edge_semantics": [
    "addresses",
    "uses"
  ],
  "common_failure_modes": [
    "方法按行复制成独立实体"
  ]
}
```

## 纵向阶段递进

```json
{
  "purpose": "真实研究顺序",
  "suitable_content_structure": "有阶段时序",
  "unsuitable_cases": "纯并列任务",
  "reading_direction": "TB",
  "main_backbone": "阶段",
  "recommended_major_modules": [
    "阶段"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "对象",
    "任务",
    "证据"
  ],
  "preferred_edge_semantics": [
    "temporal_before"
  ],
  "common_failure_modes": [
    "顺序伪装因果"
  ]
}
```

## 平行任务汇聚

```json
{
  "purpose": "多路任务共同产出",
  "suitable_content_structure": "并列后真实汇总",
  "unsuitable_cases": "任务前后依赖",
  "reading_direction": "TB",
  "main_backbone": "多支路/汇总",
  "recommended_major_modules": [
    "多支路",
    "汇总"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "方法",
    "条件"
  ],
  "preferred_edge_semantics": [
    "parallel_with",
    "produces"
  ],
  "common_failure_modes": [
    "为对称增加支路"
  ]
}
```

## 中心机制＋周围证据

```json
{
  "purpose": "证据检验核心机制",
  "suitable_content_structure": "核心命题与多证据来源",
  "unsuitable_cases": "没有核心机制",
  "reading_direction": "center-out",
  "main_backbone": "机制/证据圈",
  "recommended_major_modules": [
    "机制",
    "证据圈"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "对象",
    "实验"
  ],
  "preferred_edge_semantics": [
    "evidence_for",
    "validates"
  ],
  "common_failure_modes": [
    "放射线混成双向影响"
  ]
}
```

## 输入—过程—机制—输出

```json
{
  "purpose": "转换与解释链",
  "suitable_content_structure": "真实输入过程机制",
  "unsuitable_cases": "无机制仍硬套",
  "reading_direction": "LR",
  "main_backbone": "输入/过程/机制/产物",
  "recommended_major_modules": [
    "输入",
    "过程",
    "机制",
    "产物"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "方法",
    "条件"
  ],
  "preferred_edge_semantics": [
    "transforms_to",
    "produces"
  ],
  "common_failure_modes": [
    "为凑槽位补机制"
  ]
}
```

## 多阶段闭环

```json
{
  "purpose": "反馈更新具体对象",
  "suitable_content_structure": "有信号返回和对象",
  "unsuitable_cases": "只说反馈无对象",
  "reading_direction": "TB+return",
  "main_backbone": "主路径/返回",
  "recommended_major_modules": [
    "主路径",
    "返回"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "验证条件"
  ],
  "preferred_edge_semantics": [
    "feeds_back_to"
  ],
  "common_failure_modes": [
    "局部修订扩成全项目循环"
  ]
}
```

## 问题—任务—证据双层

```json
{
  "purpose": "研究什么及如何取证",
  "suitable_content_structure": "内容任务证据不等同",
  "unsuitable_cases": "两层关系不明确",
  "reading_direction": "TB",
  "main_backbone": "内容层/任务证据层",
  "recommended_major_modules": [
    "内容层",
    "任务证据层"
  ],
  "hierarchy_depth": "优先2层；有必要才3层",
  "typical_secondary_layers": [
    "方法",
    "进度"
  ],
  "preferred_edge_semantics": [
    "uses",
    "evidence_for"
  ],
  "common_failure_modes": [
    "按同数量建立一对一边"
  ]
}
```
