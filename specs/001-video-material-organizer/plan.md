# 实现计划：视频物料整理工具

**分支**: `001-video-material-organizer` | **日期**: 2025-12-11 | **规格**: [spec.md](./spec.md)
**输入**: 功能规格说明 `/specs/001-video-material-organizer/spec.md`

## 摘要

构建一个本地桌面应用，用于管理视频制作物料。应用提供左侧文件树浏览、右侧预览区的界面布局，支持模板视频的预处理（提取头帧、音频）、生成视频的流程管理、以及大模型 Prompt 的管理。采用 Python + PySide6 实现，所有数据以文件形式存储在本地。

## 技术上下文

**语言/版本**: Python 3.11+
**主要依赖**:
- PySide6（GUI 框架，Qt 的官方 Python 绑定，简单易用）
- moviepy（视频处理：提取头帧、音频）
- Pillow（图片处理）

**存储**: 文件系统（用户指定的数据目录 + JSON 配置文件）
**测试**: 手动验证为主（符合宪法"简单优先"原则）
**目标平台**: Windows 桌面
**项目类型**: 单一项目（single）
**性能目标**: 无特定要求（宪法明确不追求性能优化）
**约束**: 纯本地运行，无网络依赖
**规模**: 支持 50+ 模板及其生成视频

## 宪法检查

*门禁：必须在 Phase 0 研究前通过。Phase 1 设计后重新检查。*

| 原则 | 检查项 | 状态 |
|------|--------|------|
| I. 简单优先 | 选择最简单方案（PySide6 直接开发） | ✅ 通过 |
| I. 简单优先 | 无过度设计（无复杂架构模式） | ✅ 通过 |
| I. 简单优先 | 使用简单、文档完善的库 | ✅ 通过 |
| II. 单机运行 | 无网络服务依赖 | ✅ 通过 |
| II. 单机运行 | 使用文件系统存储 | ✅ 通过 |
| II. 单机运行 | 支持本地文件路径 | ✅ 通过 |
| III. 用户友好 | 中文界面 | ✅ 通过 |
| III. 用户友好 | 清晰的文件组织结构 | ✅ 通过 |
| III. 用户友好 | 明确的操作反馈 | ✅ 通过 |

**结论**: 所有宪法原则检查通过，无需记录违规理由。

## 项目结构

### 文档（本功能）

```text
specs/001-video-material-organizer/
├── plan.md              # 本文件
├── research.md          # Phase 0 输出
├── data-model.md        # Phase 1 输出
├── quickstart.md        # Phase 1 输出
└── checklists/          # 检查清单
```

### 源代码（仓库根目录）

```text
src/
├── main.py              # 应用入口
├── models/              # 数据模型
│   ├── template.py      # 模板类
│   ├── project.py       # 生成项目类
│   └── config.py        # 配置类
├── services/            # 业务逻辑
│   ├── file_service.py  # 文件操作服务
│   ├── media_service.py # 媒体处理服务（提取头帧、音频）
│   └── config_service.py # 配置管理服务
├── ui/                  # 界面组件
│   ├── main_window.py   # 主窗口
│   ├── file_tree.py     # 左侧文件树
│   ├── preview_panel.py # 右侧预览区
│   ├── video_player.py  # 视频播放器
│   ├── audio_player.py  # 音频播放器
│   └── text_editor.py   # 文本编辑器
└── resources/           # 资源文件
    └── prompts/         # 默认 Prompt 模板
```

**结构决策**: 采用单一项目结构，按职责分层（models/services/ui），符合简单优先原则，易于理解和维护。

## 复杂度追踪

> 无宪法违规，无需填写。
