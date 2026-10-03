# 科研角色与状态

类型枚举以Schema为准；全部27类包括 background、research_gap、research_problem、scientific_question、hypothesis、overall_objective、sub_objective、research_content、work_package、research_task、progress、research_object、material、data、method、comparison、condition、evidence、mechanism、process、validation、feedback、intervention、cultivation、output、innovation、limitation。

- 内容：要研究的认识问题。
- 任务：具体执行活动，产生资料；可贯穿多个内容。
- 方法：获得/分析/解释资料的方式；可共享。
- 进度：月份和工作安排；不进入机制因果链。
- 证据：支持/检验什么命题；尚待收集保留planned。
- 机制：拟解释的作用命题；不能将技术步骤自动升级为机制。
- 验证：检验的对象与条件；验证计划不等于验证成功。
- 反馈：什么信号更新哪个对象；只说反馈不够创建循环。
- 产出：拟形成的结果/工具/论文，expected不等于reported。

同一实体单一主要type；复合段落可拆多个实体并各自引用。label保持术语，short_label缩短但不改变科学含义。statement_status为definition/background_claim/planned/hypothesized/expected/reported；reported仅表示原文报告。

contains是归属；temporal_before是时间；compares_with和contrasts_with是非因果比较；influences不自动升级causes；evidence_for/validates需要明确支持/检验对象；feeds_back_to需要明确更新对象。uses/addresses/produces为常用辅助关系；causes只录入原文明示命题且保持假设/计划/报告状态。
