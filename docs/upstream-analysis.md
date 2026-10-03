# drawio-skill 上游分析与取舍

分析日期：2026-10-04（Asia/Shanghai）。本轮是设计分析，没有实现或安装新的科研 Skill，也没有复制上游业务代码。

## 1. 仓库与证据基线

| 项目 | 本轮确认的状态 |
|---|---|
| 目标仓库 | [shuaif266-netizen/draw--](https://github.com/shuaif266-netizen/draw--)；开始时为空，默认分支 main，无 HEAD；GitHub 连接器返回拥有者具有 push 权限 |
| 本机目标 checkout | `C:/Users/40491/Documents/ChatGPT/科研绘图/draw--` |
| 初始化 | main 上只创建 README.md、LICENSE、AGENTS.md；本地初始提交 `9e2ef07`，随后切到用户指定分支 `feature/scientific-framework-v1` |
| 上游 | [Agents365-ai/drawio-skill](https://github.com/Agents365-ai/drawio-skill) |
| 固定版本 | `88fd9236bc532aac4c25cb008a8bd59bc650b904`；本机 checkout 与 GitHub remote HEAD 一致，checkout 无本地修改 |
| 上游 Skill 版本 | 固定提交的 `skills/drawio-skill/SKILL.md` 声明 3.4.0；版本号不代替提交号 |
| 上游许可 | [MIT License](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/LICENSE)，Copyright (c) 2026 Agents365-ai；已通过 GitHub 工具读取正文 |
| 当前机器 | Git 和 bundled Python 可用；PATH 上未发现 drawio、draw.io、dot，两个常见 Windows draw.io 安装路径也不存在。没有启动 GUI、安装依赖或执行上游测试 |

分析使用固定版本的文件及实现，不把 README 的宣传描述当作已经验收的能力。以下数量/限制只针对上述提交。

## 2. 阅读范围

路径均相对于上游仓库。参考文件是 `skills/drawio-skill/references/`，不是仓库根目录下的 references。

| 已阅读参考 | 有价值的机制 | 面向科研的缺口 |
|---|---|---|
| [SKILL.md](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/SKILL.md) | author/validate/export/visual-review 的分阶段流程；保留稳定身份与人工布局；记录原生导出限制 | 入口面向架构、代码/IaC、API、UML等，多种软件角色与任务路由不适合本项目；没有中文申请书科研理解层 |
| [style-extraction.md](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/references/style-extraction.md) | XML 样式分词、配色频率、标题/正文相对层级、连接样式剥离坐标、来源与置信度 | 按形状和英文关键词推断 database/service 等；中文普通节点易归为 service；缺少 layout_grammar，无法用这套规则推断科研语义 |
| [style-presets.md](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/references/style-presets.md) | 个人预设与内置预设分开；结构样式和视觉样式组合；提取候选不等于立刻设默认 | role/slot 仍是软件角色；一次图的视觉属性不等于个人长期偏好；配色之外需独立的版式语法 |
| [derasterize.md](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/references/derasterize.md) | Agent 看图后记录形状、坐标、线型，再写成可编辑图；承认无箭头/交叉线的歧义 | 不是自动 OCR/机器视觉程序；“可见连线”不能自动成为科学因果；参考学习和经授权的截图重建须分成两个模式 |
| [diagram-types.md](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/references/diagram-types.md) | 按图种定义形状、连接和方向，而非单一皮肤 | ERD、UML、C4、BPMN、ML网络图等不能直接充当中文科研图类型库 |
| [xml-authoring.md](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/references/xml-authoring.md) | 0/1 根单元、XML转义、行内换行、真正父子容器、相对几何、端口、waypoints、可编辑文字 | 图种色义仍是软件角色；“大图默认按拓扑排布”不能覆盖科研主次；实际字体/路径和科学真实性要另外核对 |
| [autolayout.md](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/references/autolayout.md) | Graphviz cluster、方向、网格、正交路径回放、容器相对坐标；说明布局不是纯边重路由 | 排布主要优化拓扑和几何，不理解研究内容与方法/任务/进度的从属；依赖 dot；导入器的传递约简不能默认用于混合科研关系 |
| [diagram-ir.md](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/references/diagram-ir.md) | 模型身份、来源 metadata、语义与几何分离、三方同步保留人工修改 | IR 和规则仍面向软件模型；没有科学问题/假设状态、来源精确定位、confidence/needs_review、内容/任务/方法/进度区分 |

同时检查了上述机制对应的脚本定义、调用与输出路径，具体取舍如下。

## 3. KEEP / ADAPT / REWRITE / DROP

四类是设计决策，不代表本轮已搬入代码。KEEP 为保留协议或原则；ADAPT 为未来只移植经过依赖切分的小块代码；REWRITE 为用本项目科研契约独立实现；DROP 为不进入本项目范围。

| 上游模块/文件 | 决策 | 未来处理与理由 | 阶段 |
|---|---|---|---|
| `references/xml-authoring.md` 的原生XML不变量 | KEEP | 保留转义、换行、容器父子、相对坐标、稳定ID、边几何；编写较短的科研渲染规范，不整份复制文档 | M1 |
| `scripts/validate.py`（406行）的结构/绝对坐标/部分几何函数 | ADAPT | 拆出结构几何内核，加入根节点、边mxGeometry、元数据保全检查；避免把通过结构检查叫作科学正确 | M1 |
| `scripts/edgeports.py`（211行）的 `assign`/端口分配 | ADAPT | 保留已锁定端口，处理多边端点；它直接加载同目录 validate.py，移植时显式注入/导入抽出的几何模块，不复制隐含依赖链 | M1 |
| `scripts/autolayout.py`（410行）的 cluster/waypoint/坐标转换 | ADAPT | 可选 Graphviz backend；科研层先给主次、分区和阅读约束，再做排布；关系键改为relation_id，不按端点对覆盖多种关系 | M2可选；M1用固定语法的确定性scene |
| `scripts/raster2drawio.py`（196行）的坐标到XML桥接 | ADAPT | 只在用户明确要求重建自己提供的图时复用基础机制；保留观察性连线和未知方向，不沿用 `arrow=true` 默认；不作为科学IR提取器 | 重建桥接M2；M1只做参考profile |
| `scripts/restyle.py`（161行）的样式键更新与布局保留 | ADAPT | 保留换肤不挪节点的原则；用科学role显式查表，避免仅按旧色相推断科研类型；人工锁定样式保留 | M1配置；自动换肤M2 |
| `scripts/repair_png.py`（37行） | ADAPT，条件启用 | 上游处理一种嵌入XML PNG尾部问题；先识别PNG签名和具体尾部缺损，另存修复，不能对任意文件盲目追加IEND。M1预览不使用嵌入XML PNG，无需默认调用 | 后续如支持editable PNG |
| `scripts/diagram_ir.py`（1458行） | REWRITE | 借鉴稳定身份和来源分离；不复制infer_kind、软件属性、架构检查、多视图/故障传播；创建独立Scientific IR与显示投影 | M1 |
| `scripts/diagramctl.py`（639行）总控入口 | DROP整份，REWRITE小入口 | 不保留大量导入器/命令/架构规则；只建立六个聚焦科研入口与共享scene；诊断和导出包装按本机需求重写 | M1 |
| `scripts/drawiohtml.py` 的 `export_svg` 与上游导出命令 | REWRITE | 本机导出wrapper解析并固定准确的draw.io二进制路径、超时、退出码及真实产物；此函数直接调用PATH上的drawio，没有科研完成状态 | M1 |
| 样式Schema、内置软件role样本、`style-extraction.md`提取流程 | REWRITE | 输出visual_style＋layout_grammar；保留来源、近似/测量属性及未知语义；个人规则候选汇总后再决定是否激活 | M1 |
| 软件图type库 | REWRITE | 设计12类科研图，单独定义总体研究思路图主骨架与辅助层 | M1指南；先实现其中3种布局 |
| PNG/JPG识别与提取 | REWRITE Agent工作流 | 视觉观察由有图像能力的Agent完成，脚本接收结构化观察，不伪称Python已理解图片或未提供的科学内容 | M1 |
| Terraform/K8s/compose/SQL/OpenAPI/AsyncAPI/Protobuf/GraphQL/代码导入 | DROP | 不是科研申报书理解，避免扩成架构Studio | 不规划 |
| 云厂商形状索引、AI品牌logo、C4/UML/ERD/BPMN网络库 | DROP | 不带入业务无关资产、字体或商标包；科研对象插图将来按需要逐项添加 | 不默认规划 |
| 架构owner/observability/trust boundary/故障模拟、五类软件视图、CI/PR bot、git timelapse | DROP | 不是Scientific QA或个人框架图的必要能力 | 不规划 |

拟复用的代码最小集合是结构几何函数和端口分配；尚未确定移植后的最终行范围。实现时在 `THIRD_PARTY_NOTICES.md` 和文件头记录实际范围，不能仅用本表替代代码溯源。

## 4. 从实现看到的具体边界

### 4.1 图片转换是两步，不是端到端识别

[raster2drawio.py](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/scripts/raster2drawio.py#L80) 直接读取 `nodes/edges` JSON 和坐标，生成XML。坐标缺失时调用兄弟 `autolayout.py`，需要Graphviz。它没有OCR或图片识别模型调用，也没有科学关系类型。默认有向箭头容易把未观察到方向的线变成箭头。

本项目应分开：参考学习只提取视觉语法；经授权的原图重建保留可见结构并标记未知；新科研图的科学关系只来自申请书Scientific IR。

### 4.2 验证范围有限，不能用一个“通过”覆盖三类验收

[validate.py](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/scripts/validate.py#L266) 检查重复/保留ID、引用端点、父引用和顶点几何。交叉/穿节点检查只在显式waypoints存在时有路径可计算；无waypoint的自动路由不等于零缺陷。该实现也不能证明中文文字实际溢出与否、A4打印可读性、科研箭头原文蕴含或核心科学问题完整。

本项目分别报告Scientific QA、draw.io结构QA、实际渲染Visual QA。未知路径、未安装渲染器、未看过图片必须是 `unknown`/`not_run`，不能评分为已通过。补上边mxGeometry、根0/1、科学元数据和布局投影一致性检查。

### 4.3 端口分配不等于避障路由

[edgeports.py](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/scripts/edgeports.py#L91) 按对端位置分配端口、跳过已锁定端口；它不修正边中段穿越无关节点。`autolayout.py` 回放dot正交路径，但科研布局需先定义留白通道与从属区域；拥挤时再添加waypoints或局部重排。

文档明确：draw.io的libavoid路由属于编辑器能力，不是可随意传给CLI的 `--layout` 值。未知layout可能打开模态框并挂住，不能作为自动修复方案。

### 4.4 上游IR不能直接承担科研保存契约

[diagram_ir.py 的 normalize_ir](https://github.com/Agents365-ai/drawio-skill/blob/88fd9236bc532aac4c25cb008a8bd59bc650b904/skills/drawio-skill/scripts/diagram_ir.py#L89) 重新组装字段；任意科研顶层扩展不会全部原样保留，需要塞入properties/provenance才能避免丢失。`infer_kind` 的默认值为service。写出路径把模型投影成graph后交给dot，捕获布局失败时使用网格fallback；保存过x/y不意味着实际写出沿用它们。

Scientific IR采用自己的Schema和显式版本迁移。科研模型不存坐标；layout_spec负责坐标、从属、端口与人工锁定；fallback必须进入render manifest，不能静默改变主要科研结构。

### 4.5 风格不是科学语义映射表

上游提取侧重色、字体、形状和线型；用圆柱推数据库、英文关键词推服务角色，甚至对图片中的色/字体给出规则化近似。本项目不从圆柱、蓝色或双向箭头推断科学类型/互作/反馈，也不把截图像素反推为原稿字号。

每条属性保留 `observed`/`estimated`/`unknown`；版式另外记录阅读方向、主骨架、层级、分区比例、辅助层、留白和密度。相同截图/构图变体不重复计为独立规律；样本以纵向图为主时，不宣称其适合所有科研逻辑。

### 4.6 原生导出和fallback必须可辨

上游PNG草稿不使用 `-e`；嵌入XML最终PNG有专门repair流程；SVG/PDF可原生导出。当前机器未发现CLI，因此M1必须能输出可编辑draw.io和 `preview.svg`，同时把SVG fallback的来源标明为同一layout_spec，而不是宣称已用draw.io渲染。只有找到并成功运行CLI才生成原生PNG和相应验收证据。

## 5. 许可与文件来源策略

本仓库原创部分采用自己的MIT LICENSE。上游也是MIT，但复用其代码需要保留 `Copyright (c) 2026 Agents365-ai` 和完整许可文字。

实现阶段拟采用：

- `skills/scientific-framework/vendor/upstream/LICENSE`：被复用代码的原始MIT许可。
- `THIRD_PARTY_NOTICES.md`：逐文件记录源仓库、固定提交、上游路径、copied/adapted状态、修改摘要；移植后文件哈希可用于复核。
- adapted文件保留上游Copyright，并追加修改者/说明，不用根LICENSE替代原始声明。
- 独立rewritten文件标为原创实现/概念借鉴；若实际复制了实质性代码，仍按adapted处理，不能以“重写”名称规避通知。
- 不复制上游整个仓库、全部tests、形状索引或品牌资产；只移植已证明需要的函数及其真实依赖。

本轮只有分析文档和初始化文件，未导入上游代码，因此尚未创建vendor或THIRD_PARTY_NOTICES。未来首次复用代码时同时建立通知。

## 6. 对本项目架构的结论

Scientific IR、来源核对、逻辑审查和科研图型选择必须独立开发；上游主要贡献是可编辑图件的工程约束。Agent负责科研理解和视觉观察，确定性脚本负责格式、来源可追溯性、几何及导出，不把任一环节伪称为另外一环节。

M1的设计、IR草案、目录与验收表见 [architecture-plan.md](architecture-plan.md)。本轮到此只完成设计分析，等待用户确认后再实现。
