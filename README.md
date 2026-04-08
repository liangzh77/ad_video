# ad_video

视频物料整理工具，一个基于 PySide6 的本地桌面应用，用于管理视频制作过程中的模板视频、项目素材、Prompt 文本和预览内容。

## 技术栈

- Python 3.11+
- PySide6
- moviepy
- Pillow

## 项目定位

根据现有代码和文档，这个项目主要面向本地视频制作流程管理，重点包括：

- 模板视频预处理
- 生成项目管理
- 文件与媒体资源整理
- Prompt 文本管理
- 图片、音频、视频预览

## 项目结构

```text
ad_video/
├── src/
│   ├── main.py                # 应用入口
│   ├── models/                # 数据模型
│   ├── services/              # 文件、媒体、配置服务
│   ├── ui/                    # 界面组件
│   └── resources/prompts/     # Prompt 模板
├── data/                      # 本地数据目录
├── specs/                     # 需求、计划、研究文档
├── requirements.txt           # Python 依赖
└── CLAUDE.md                  # 开发说明
```

## 主要模块

### 数据模型

- `src/models/template.py`
- `src/models/project.py`
- `src/models/config.py`

### 服务层

- `src/services/file_service.py`
- `src/services/media_service.py`
- `src/services/config_service.py`

### UI 组件

- `src/ui/main_window.py`
- `src/ui/file_tree.py`
- `src/ui/preview_panel.py`
- `src/ui/prompt_editor.py`
- `src/ui/video_player.py`
- `src/ui/audio_player.py`
- `src/ui/image_viewer.py`
- `src/ui/text_editor.py`

## 安装依赖

建议先创建虚拟环境，再安装：

```bash
pip install -r requirements.txt
```

当前依赖包括：

- `PySide6`
- `moviepy`
- `Pillow`

## 启动方式

直接运行主入口：

```bash
python src/main.py
```

## 功能说明

从现有目录与命名来看，应用已具备这些核心能力：

- 文件树浏览与拖拽导入
- 视频、音频、图片、文本预览
- Prompt 模板查看与编辑
- 本地配置管理
- 媒体文件处理服务封装

## Prompt 资源

项目内置了 Prompt 模板：

- `src/resources/prompts/frame.txt`
- `src/resources/prompts/subtitle.txt`

适合用于视频生成、镜头说明或字幕相关工作流。

## 文档索引

- [CLAUDE.md](./CLAUDE.md): 开发指南
- [specs/001-video-material-organizer/spec.md](./specs/001-video-material-organizer/spec.md): 功能规格
- [specs/001-video-material-organizer/plan.md](./specs/001-video-material-organizer/plan.md): 实现计划
- [specs/001-video-material-organizer/quickstart.md](./specs/001-video-material-organizer/quickstart.md): 快速开始
- [specs/001-video-material-organizer/data-model.md](./specs/001-video-material-organizer/data-model.md): 数据模型
- [specs/001-video-material-organizer/research.md](./specs/001-video-material-organizer/research.md): 技术研究

## 开发说明

- 项目是纯本地桌面应用，核心数据存储依赖文件系统与 JSON 配置
- 文档、注释和交流以中文为主
- 代码命名遵循 Python 常规风格，优先保持简单直接

## 说明

- 根目录原来没有 `README.md`，这份文件基于现有源码结构和开发文档补充而成
- `src` 下存在 `__pycache__` 产物，这些不是文档关注重点
