# 第三方来源与复用记录

M1没有复制、移植或改编上游的实质性代码。所有本仓库脚本为独立实现；没有vendor目录，也没有宣称集成edge_ports、Graphviz或上游geometry模块。

概念与格式参考：Agents365-ai/drawio-skill，固定提交88fd9236bc532aac4c25cb008a8bd59bc650b904，MIT Copyright (c) 2026 Agents365-ai。参考内容包括原生XML不变量、语义与展示分离、来源标识及导出/校验边界，详见docs/upstream-analysis.md。本次状态为conceptual reference / independently rewritten，不是copied/adapted。

运行时依赖：jsonschema（MIT）、Pillow（HPND；其包含组件各有许可）。通过包管理器安装，不把依赖代码打包进仓库；准确许可可查看安装包各自dist-info/licenses。项目MIT许可不替代依赖许可。

未来如果确实移植上游代码，必须同时加入原始完整MIT许可证、copyright、逐文件copied/adapted状态、源路径、提交、修改摘要及哈希；不能用本文概念借鉴声明替代。
