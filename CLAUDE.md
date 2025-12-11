# 视频物料整理工具 开发指南

自动生成于功能计划。最后更新: 2025-12-11

## 项目概述

本地桌面应用，用于管理视频制作物料。支持模板视频预处理、生成视频流程管理、大模型 Prompt 管理。

## 核心原则

1. **简单优先**: 选择最简单可行的方案，禁止过度设计
2. **单机运行**: 纯本地应用，无网络依赖（大模型API除外）
3. **用户友好**: 中文界面，操作直观

## 技术栈

- **语言**: Python 3.11+
- **GUI**: PySide6
- **视频处理**: moviepy
- **图片处理**: Pillow
- **存储**: 文件系统 + JSON 配置

## 项目结构

```text
src/
├── main.py              # 应用入口
├── models/              # 数据模型
│   ├── template.py      # 模板类
│   ├── project.py       # 生成项目类
│   └── config.py        # 配置类
├── services/            # 业务逻辑
│   ├── file_service.py  # 文件操作
│   ├── media_service.py # 媒体处理
│   └── config_service.py # 配置管理
├── ui/                  # 界面组件
│   ├── main_window.py   # 主窗口
│   ├── file_tree.py     # 文件树
│   ├── preview_panel.py # 预览区
│   └── ...
└── resources/           # 资源文件
    └── prompts/         # Prompt 模板
```

## 常用命令

```bash
# 安装依赖
pip install PySide6 moviepy Pillow

# 运行应用
python src/main.py
```

## 代码风格

- 文档、注释、提交信息使用中文
- 变量名和函数名使用英文（遵循 Python PEP8）
- 优先使用简单直接的代码，可读性优先

## 相关文档

- [功能规格](specs/001-video-material-organizer/spec.md)
- [实现计划](specs/001-video-material-organizer/plan.md)
- [数据模型](specs/001-video-material-organizer/data-model.md)
- [快速开始](specs/001-video-material-organizer/quickstart.md)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
