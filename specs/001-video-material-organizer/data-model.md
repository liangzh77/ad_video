# 数据模型：视频物料整理工具

**日期**: 2025-12-11
**分支**: `001-video-material-organizer`

## 概述

本应用采用文件系统作为数据存储，不使用数据库。数据模型主要用于内存中的对象表示。

---

## 实体定义

### 1. Template（模板）

代表一个模板视频及其预处理文件集合。

```python
@dataclass
class Template:
    name: str                    # 模板名称（即文件夹名）
    path: Path                   # 模板文件夹完整路径

    # 以下文件均为可选
    video_path: Optional[Path]   # 模板，视频，[name].mp4
    frame_path: Optional[Path]   # 模板，头帧，[name].jpg
    audio_path: Optional[Path]   # 模板，声音，[name].mp3
    subtitle_path: Optional[Path] # 模板，字幕，[name].srt

    projects: List[GeneratedProject]  # 该模板下的生成项目列表
```

**文件检测规则**:
- 根据文件命名规则自动检测文件是否存在
- 文件路径为 `None` 表示该文件未设置

---

### 2. GeneratedProject（生成项目）

代表一次视频生成任务。

```python
@dataclass
class GeneratedProject:
    number: str                  # 编号，如 "01", "02"
    path: Path                   # 子文件夹完整路径
    template: Template           # 所属模板
    steps: List[WorkflowStep]    # 流程步骤列表（固定5个）
```

**编号规则**:
- 两位数字字符串：01, 02, ..., 99
- 新建时自动查找下一个可用编号

---

### 3. WorkflowStep（流程步骤）

代表生成视频流程中的一个步骤。

```python
@dataclass
class WorkflowStep:
    id: str                      # 步骤标识：subtitle, voice, frame, kling, final
    name: str                    # 步骤中文名称
    description: str             # 步骤描述
    expected_filename: str       # 预期输出文件名模式
    file_path: Optional[Path]    # 实际文件路径（None 表示未完成）
    has_prompt: bool             # 是否需要大模型 Prompt
    prompt_key: Optional[str]    # Prompt 类型标识
```

**固定步骤定义**:

| id | name | expected_filename | has_prompt |
|----|------|-------------------|------------|
| subtitle | 字幕生成 | {编号}，字幕.srt | ✅ |
| voice | 语音生成 | {编号}，语音，*.mp3 | ❌ |
| frame | 头帧生成 | {编号}，头帧.jpg | ✅ |
| kling | 可灵视频 | {编号}，可灵.mp4 | ❌ |
| final | 成片导出 | {编号}，成片.mp4 | ❌ |

---

### 4. PromptTemplate（Prompt 模板）

代表大模型使用的提示词模板。

```python
@dataclass
class PromptTemplate:
    key: str                     # 类型标识：subtitle, frame
    name: str                    # 中文名称
    default_content: str         # 默认 Prompt 内容
    user_content: Optional[str]  # 用户自定义内容（覆盖默认）
```

---

### 5. AppConfig（应用配置）

代表应用的全局配置。

```python
@dataclass
class AppConfig:
    data_directory: Path         # 数据根目录
    prompts: Dict[str, PromptTemplate]  # Prompt 模板集合
    last_opened_template: Optional[str]  # 上次打开的模板名
```

---

## 文件系统映射

### 目录结构 → 对象关系

```text
[data_directory]/           → AppConfig.data_directory
├── [模板名1]/              → Template(name="模板名1")
│   ├── 模板，视频，*.mp4   → Template.video_path
│   ├── 模板，头帧，*.jpg   → Template.frame_path
│   ├── 模板，声音，*.mp3   → Template.audio_path
│   ├── 模板，字幕，*.srt   → Template.subtitle_path
│   ├── 01/                 → GeneratedProject(number="01")
│   │   ├── 01，字幕.srt    → WorkflowStep(id="subtitle")
│   │   ├── 01，语音，*.mp3 → WorkflowStep(id="voice")
│   │   ├── 01，头帧.jpg    → WorkflowStep(id="frame")
│   │   ├── 01，可灵.mp4    → WorkflowStep(id="kling")
│   │   └── 01，成片.mp4    → WorkflowStep(id="final")
│   └── 02/                 → GeneratedProject(number="02")
└── [模板名2]/              → Template(name="模板名2")
```

---

## 状态转换

### 流程步骤状态

```
未设置 (file_path=None)
    │
    ├── 用户传入文件 ──→ 已完成 (file_path=实际路径)
    │                        │
    │                        ├── 用户删除文件 ──→ 未设置
    │                        │
    │                        └── 用户覆盖文件 ──→ 已完成（新路径）
    │
    └── 检测到文件已存在 ──→ 已完成
```

---

## 验证规则

| 实体 | 字段 | 规则 |
|------|------|------|
| Template | name | 非空，不含非法文件名字符 |
| Template | path | 目录必须存在 |
| GeneratedProject | number | 两位数字，01-99 |
| WorkflowStep | file_path | 如非空，文件必须存在 |
| AppConfig | data_directory | 目录必须存在且可写 |
