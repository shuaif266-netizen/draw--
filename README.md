# Scientific Framework Skill

面向中文科研项目申报书、基金申请书和课题申请书的个人科研框架图 Agent Skill。

目标流程：申请书 → 科研内容理解 → 有来源的 Scientific IR → 科研逻辑检查 → 2–3 个结构方向 → 版式与个人视觉语法 → 可编辑 draw.io → SVG/PNG 预览 → 科研与视觉检查 → 人工反馈修订。

优先级：科研逻辑准确、结构清晰、阅读顺序明确、可编辑、视觉美观。

## 当前阶段

Milestone 1已实现，详见[完成报告](docs/milestone-1-report.md)。Agent负责语义理解与视觉观察；脚本负责抽取、编译、校验和渲染。不是自动科研推理/OCR/模型训练器。

Skill入口是 [skills/scientific-framework/SKILL.md](skills/scientific-framework/SKILL.md)，含逐步命令和审查要求。上游参考项目为 [Agents365-ai/drawio-skill](https://github.com/Agents365-ai/drawio-skill)，本轮没有复制/改编实质代码，见[来源通知](THIRD_PARTY_NOTICES.md)。

## 运行与验证

Python 3.12已实测，输入支持UTF-8 TXT/Markdown、简单DOCX正文/表格。

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv/Scripts/python.exe -m unittest discover -s tests -p test_m1.py -v
.venv/Scripts/python.exe tests/run_case.py
```

macOS/Linux用`.venv/bin/python`。requirements.txt是运行依赖，requirements-dev另含Skill验证用PyYAML。完整技能文件夹可复制到个人skills目录调用 `$scientific-framework`，依赖须装到执行脚本的Python环境。本轮没有复制到全局skills或覆盖已有技能。

先抽取source_segments，再由Agent写agent_understanding并对照来源审查。IR不含几何；layout不能改科学角色或边。核心待审关系可生成draft，不可approved。修改语义后旧审查hash失效，必须重审；Schema通过不能证明原文蕴含。

三种实际可运行布局：overall_research_approach_vertical（纵向主轴）、question_content_method_three_column（中栏内容及共享方法）、content_evidence_dual_layer（内容与任务/资料分层）。其他9类只有选择指南。基础通道未做复杂避障；完整大图有交叉/标签拥挤和打印限制，QA会记录，不能冒充final。

没有draw.io CLI时输出同源scene_svg_fallback，native_drawio_render=skipped，preview.png缺省。浏览器QA截图不是原生PNG。

## 合成示例

[case_001](eval_cases/case_001/)含独立语义预期、Agent理解输入和[实际产物](eval_cases/case_001/generated/)：19节点、17关系、四内容/四任务/五方法，含探索性比较、预期工具和待审检验。A/B/C三布局均有draw.io/SVG及QA。完整示例不适合直接A4缩印。

参考学习由Agent实际看图填observation，各属性observed/estimated/unknown。profile拆visual_style/layout_grammar；去重后的两个独立构图可提出promotion candidate，仍须用户确认，不自动改默认。M1未实现PDF/OCR、Graphviz、复杂机制图、图片原生重建或反馈自动升级。

## 数据与示例

真实申请书、参考科研图、个人反馈和项目输出放eval_cases_private或指定本地路径，不push。公开case_001是合成，只有其generated允许跟踪，未来真实材料不要放case_001。根reference_images、reference_profiles、feedback和outputs内容默认忽略。参考学习视觉组织，不作为科研事实来源。
