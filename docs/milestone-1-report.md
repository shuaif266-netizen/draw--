# Milestone 1 完成报告

2026-10-04；feature/scientific-framework-v1。M1实现与回归完成，合成图仍为待审草稿；人类正式验收pending。不merge main，不进入M2。

## 1. 实现内容

五份Draft2020-12 Schema，27类科研角色、19类关系；extract_sources与compile_scientific_ir分离；引文/定位、ID、快照和批准门槛；Agent审查同时绑定来源及语义hash。修改type/状态/关系后必须重审，IR不含几何，layout不能覆盖科学语义。

三种scene布局、可编辑文字/形状/真实嵌套容器/连线，semantic IDs与来源摘要保存，不嵌正文。同端点不同关系不覆盖。长中文完整换行，XML特殊字符往返。draw.io与SVG同源，manifest明确实际后端。

reference observation→profile JSON/MD→双层style candidate已运行，unknown保留、重复像素/已确认变体去重，不自动改默认。Skill入口、UI元数据、九份参考文档、本地数据忽略规则均完成。

## 2. 未实现内容

PDF/OCR、自动图像理解/模型训练、Graphviz、edge_ports、复杂避障、复杂机制/辐射/汇聚布局、图片原生重建、增量同步、反馈自动升级或默认风格激活。反馈由Agent按约定记录到本地JSONL，当前无真实反馈。包可安装，本轮未复制到全局skills/覆盖已有技能。

## 3. 上游代码与通知

实质代码copied/adapted数量为零，全部独立实现。仅借鉴XML不变量、身份/来源分离和导出/验收边界，没有虚假vendor或geometry移植声明。固定上游提交88fd9236bc532aac4c25cb008a8bd59bc650b904，许可与来源见[THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md)。

## 4. 实际测试

35/35 unittest通过，覆盖用户全部12项测试，补充来源/定位错误、包含循环、旧layout/审查失效、XML手改、根ID、DOCX修订拒绝等。五Schema自校验、Skill quick_validate（Python UTF-8模式）、pip check通过。九次实际CLI调用覆盖抽取、编译、Scientific QA、布局、XML写出、结构/视觉QA、SVG预览、reference profile及候选聚合，均成功执行。

测试验证确定性行为，不证明科学分类或引文蕴含。Agent对照原文的summary/issues仍必需；hash只能防止旧记录误用，不能证明审查质量。

## 5. 合成案例

[case_001](../eval_cases/case_001/)实际抽取11个片段，编译19节点/17关系：四内容、四任务、五方法，另有问题、资料、比较、综合分析、预期工具、进度。没有自动创建四任务到四内容的一对一边；共享过程追踪法只有一个实体。

[generated](../eval_cases/case_001/generated/)包含source_segments、scientific_ir、logic_review、diagram_directions、layout_spec、diagram_scene、research-framework.drawio、preview.svg、render_manifest、scientific_qa、visual_qa、drawio_qa。B/C在layout-2/3；reference_profile及style_candidates也实际生成。

Scientific QA valid=true、approval_eligible=false：r-validation检验指标未定，needs_review=true，draft可生成，approved被拒绝。比较保持无方向，工具保持expected。参考仅一个独立构图，两条规律均candidate、default_changed=false。human_review没有虚构专家通过。

## 6. 三种实际布局

| 布局 | 可运行行为 | 完整案例残余视觉问题 |
|---|---|---|
| overall_research_approach_vertical | 中间主层、任务/方法侧层 | 8处严格正交交叉、局部标签近邻 |
| question_content_method_three_column | 中间内容、左问题、右共享方法 | 中栏包含任务/资料后过长，长线拥挤 |
| content_evidence_dual_layer | 内容主层与任务/资料辅助层 | 12处严格正交交叉、外侧标签拥挤 |

实际查看Edge headless渲染的三张SVG截图，两轮修正了穿节点通道与技术ID标签。当前未检测到穿无关节点，仍有上表问题；严格交叉统计不包括共线重叠或文字遮挡。Agent视觉记录completed_with_issues，人类验收pending。

完整IR的A4缩印主体字号约6.5pt（估算），辅助状态字更小，不适合直接申报书A4打印。实际A4/灰度打印与人类3–5秒识别not_run。示例不称final，需按用途缩减非核心显示投影或更大纸幅；不能修改科学结构凑对称。

## 7. 环境与缺失依赖

Python 3.12独立.venv；jsonschema4.26.0、Pillow12.1.1，开发验证用PyYAML6.0.3，pip check无冲突。中文测量使用现有字体；其他机器缺字体则标estimated。

没有draw.io CLI，Graphviz也未发现且M1不需要。没有安装/启动draw.io。SVG backend=scene_svg_fallback、native_drawio_render=skipped、preview.png未生成。Edge截图仅作SVG视觉观察，一张作为合成参考；不冒充原生PNG。真实CLI导出分支尚未在本机验收，XML结构通过不能代替原生应用验收。

## 8. 数据与可复现性

没有提交真实申请书、真实参考科研图、个人反馈或真实输出。case_001及截图均合成；私有目录/根输出/参考/反馈内容由.gitignore排除。空feedback-log.jsonl仅本地存在。

.gitattributes固定LF，JSON规范化hash，SVG/XML稳定序列化；暂存SVG实际SHA256与manifest已核对一致。额外从Git archive导出的干净副本运行35项测试和完整案例，均通过，三个SVG的manifest校验和一致。案例视觉记录仅在对应visual scene hash一致时复用，否则标stale。运行tests/run_case.py可重建产物，语义fixture由Agent提供，不把复跑说成脚本理解申报书。

## 9. 已知问题

- 科学判断依赖Agent输入，不能仅靠Schema确定因果/术语分类。
- DOCX仅普通正文/表格；修订、文本框、嵌套表格拒绝，页码/页眉/绘图不抽取。
- M1显示一节点一实体，暂无聚合；省略须理由，核心不可省略。
- 人工改XML后需要重审/更新scene，不支持反向同步。
- 固定通道可能交叉/标签重叠；A4和字体跨平台需要实际验收。
- CLI分支未真实验收，fallback不能替代该项。

## 10. 下一阶段与停止点

建议先用用户选定的实际用途调整投影/打印尺寸，私有运行并做人类语义与视觉验收；如需原生导出再准备有CLI的环境。edge_ports、复杂路由、PDF需后续单独授权，M1到此停止。
