# 已确认的M1修订（2026-10-04）

本文件覆盖 architecture-plan.md 中对应旧规划：

- proposal_to_ir 拆为 extract_sources（纯抽取）和 compile_scientific_ir（接收Agent理解结果）。
- 五份Schema增加 reference-observation，所有观察值标 observed/estimated/unknown。
- IR、layout、scene、draw.io和manifest使用 draft/reviewed/approved。核心待审项阻止批准；程序通过不能代替Agent对原文的Scientific QA。
- M1只实现 overall_research_approach_vertical、question_content_method_three_column、content_evidence_dual_layer。
- 不移植edge_ports、Graphviz或复杂路由。本次可独立实现基础几何校验；若无实质代码复用，来源通知明确记录这一点。
- 公开仓库只提交代码、文档和合成案例。私有case、图片、反馈、真实输出默认忽略。
- 实际生成完整合成案例与QA记录，报告完成后停止，不merge main。
