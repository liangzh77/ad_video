# 任务列表：视频物料整理工具

**输入**: 设计文档来自 `/specs/001-video-material-organizer/`
**前置条件**: plan.md (必需), spec.md (必需), data-model.md, research.md, quickstart.md

**测试**: 根据宪法"简单优先"原则，本项目以手动验证为主，不包含自动化测试任务。

**组织方式**: 任务按用户故事分组，支持独立实现和测试。

## 格式说明: `[ID] [P?] [Story?] 描述`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 所属用户故事（如 [US1], [US2], [US3], [US4]）
- 描述中包含确切的文件路径

## 路径约定

- **单一项目**: `src/`, 位于仓库根目录
- 所有路径相对于仓库根目录

---

## Phase 1: 项目初始化

**目的**: 创建项目结构和基础配置

- [ ] T001 创建项目目录结构：src/models/, src/services/, src/ui/, src/resources/prompts/
- [ ] T002 创建 requirements.txt 包含依赖：PySide6, moviepy, Pillow
- [ ] T003 [P] 创建应用入口文件 src/main.py（空框架）
- [ ] T004 [P] 创建默认 Prompt 模板文件 src/resources/prompts/subtitle.txt 和 src/resources/prompts/frame.txt

---

## Phase 2: 基础设施（阻塞性前置任务）

**目的**: 所有用户故事都依赖的核心基础设施

**⚠️ 关键**: 此阶段必须完成后才能开始任何用户故事

- [ ] T005 实现 AppConfig 数据类 in src/models/config.py（数据目录、Prompt模板配置）
- [ ] T006 [P] 实现 Template 数据类 in src/models/template.py（模板名称、文件路径）
- [ ] T007 [P] 实现 GeneratedProject 数据类 in src/models/project.py（编号、流程步骤）
- [ ] T008 [P] 实现 WorkflowStep 数据类 in src/models/project.py（步骤ID、状态、Prompt关联）
- [ ] T009 [P] 实现 PromptTemplate 数据类 in src/models/config.py（默认内容、用户自定义）
- [ ] T010 实现 ConfigService in src/services/config_service.py（加载/保存 JSON 配置）
- [ ] T011 实现主窗口框架 in src/ui/main_window.py（左右分栏布局、菜单栏）
- [ ] T012 实现数据目录选择对话框 in src/ui/main_window.py（首次启动时选择）

**检查点**: 基础设施就绪，可以开始用户故事实现

---

## Phase 3: 用户故事 1 - 模板管理与文件准备 (P1) 🎯 MVP

**目标**: 创建模板文件夹，支持多种方式准备模板文件（视频、头帧、音频、字幕）

**独立测试**: 创建一个新模板，添加视频文件，提取头帧和音频，保存字幕，验证文件正确生成

### 实现任务

- [ ] T013 [US1] 实现 FileService.create_template_folder() in src/services/file_service.py
- [ ] T014 [US1] 实现 FileService.copy_and_rename_file() in src/services/file_service.py（通用文件复制重命名）
- [ ] T015 [US1] 实现 FileService.get_next_project_number() in src/services/file_service.py（查找下一个可用编号）
- [ ] T016 [P] [US1] 实现 MediaService.extract_first_frame() in src/services/media_service.py（使用 moviepy）
- [ ] T017 [P] [US1] 实现 MediaService.extract_audio() in src/services/media_service.py（使用 moviepy）
- [ ] T018 [US1] 实现 FileService.save_text_file() in src/services/file_service.py（保存字幕文本）
- [ ] T019 [US1] 实现 FileService.scan_template_folder() in src/services/file_service.py（扫描模板文件夹，检测已有文件）
- [ ] T020 [US1] 实现新建模板对话框 in src/ui/main_window.py（输入模板名称）
- [ ] T021 [US1] 实现模板操作按钮区域 in src/ui/main_window.py（设为视频/提取头帧/提取音频等）
- [ ] T022 [US1] 连接模板操作按钮与 FileService/MediaService in src/ui/main_window.py
- [ ] T023 [US1] 添加操作结果提示（成功/失败消息框）in src/ui/main_window.py

**检查点**: 用户故事 1 完成，可以独立测试模板创建和文件准备功能

---

## Phase 4: 用户故事 2 - 文件浏览与预览 (P2)

**目标**: 左侧显示文件树，右侧预览视频/音频/文本

**独立测试**: 打开应用，查看左侧模板列表，点击视频文件播放，点击音频文件播放，点击字幕文件编辑

### 实现任务

- [ ] T024 [US2] 实现 FileService.scan_data_directory() in src/services/file_service.py（扫描所有模板）
- [ ] T025 [US2] 实现左侧文件树组件 in src/ui/file_tree.py（使用 QTreeView）
- [ ] T026 [US2] 实现文件树数据模型 in src/ui/file_tree.py（显示模板、预设文件位置、生成项目）
- [ ] T027 [US2] 实现"未设置"状态显示 in src/ui/file_tree.py（缺失文件灰色显示）
- [ ] T028 [P] [US2] 实现视频播放器组件 in src/ui/video_player.py（使用 QMediaPlayer）
- [ ] T029 [P] [US2] 实现音频播放器组件 in src/ui/audio_player.py（使用 QMediaPlayer）
- [ ] T030 [P] [US2] 实现文本编辑器组件 in src/ui/text_editor.py（使用 QPlainTextEdit）
- [ ] T031 [US2] 实现预览面板容器 in src/ui/preview_panel.py（根据文件类型切换显示）
- [ ] T032 [US2] 连接文件树点击事件与预览面板 in src/ui/main_window.py
- [ ] T033 [US2] 实现文本编辑器保存功能 in src/ui/text_editor.py

**检查点**: 用户故事 2 完成，可以浏览和预览所有类型的文件

---

## Phase 5: 用户故事 3 - 生成视频流程管理 (P3)

**目标**: 创建生成视频子项目，显示流程步骤和状态，支持文件增删改

**独立测试**: 在模板下新建生成视频，查看流程步骤列表，添加/删除步骤文件，验证状态更新

### 实现任务

- [ ] T034 [US3] 实现 FileService.create_project_folder() in src/services/file_service.py（创建编号子文件夹）
- [ ] T035 [US3] 实现 FileService.scan_project_folder() in src/services/file_service.py（扫描项目文件夹，检测步骤文件）
- [ ] T036 [US3] 实现固定流程步骤定义 in src/models/project.py（5个步骤的元数据）
- [ ] T037 [US3] 扩展文件树显示生成项目 in src/ui/file_tree.py（显示流程步骤列表）
- [ ] T038 [US3] 实现步骤状态图标显示 in src/ui/file_tree.py（待处理/已完成）
- [ ] T039 [US3] 实现新建生成视频按钮 in src/ui/main_window.py
- [ ] T040 [US3] 实现步骤文件传入功能 in src/ui/main_window.py（选择文件并复制到正确位置）
- [ ] T041 [US3] 实现步骤文件删除功能 in src/ui/main_window.py（删除文件并更新状态）
- [ ] T042 [US3] 实现文件树自动刷新 in src/ui/file_tree.py（文件变化后更新显示）

**检查点**: 用户故事 3 完成，可以完整管理生成视频流程

---

## Phase 6: 用户故事 4 - 大模型 Prompt 管理 (P4)

**目标**: 显示默认 Prompt，支持编辑、复制、保存为默认

**独立测试**: 查看字幕生成步骤，修改 Prompt，复制到剪贴板，保存为默认值

### 实现任务

- [ ] T043 [US4] 实现 Prompt 显示区域 in src/ui/preview_panel.py（在步骤详情中显示）
- [ ] T044 [US4] 实现 Prompt 编辑功能 in src/ui/preview_panel.py（可编辑文本框）
- [ ] T045 [US4] 实现一键复制按钮 in src/ui/preview_panel.py（复制到系统剪贴板）
- [ ] T046 [US4] 实现保存为默认按钮 in src/ui/preview_panel.py
- [ ] T047 [US4] 连接保存功能与 ConfigService in src/ui/preview_panel.py（更新配置并保存）
- [ ] T048 [US4] 加载默认 Prompt 文件 in src/services/config_service.py（从 resources/prompts/ 读取）

**检查点**: 用户故事 4 完成，Prompt 管理功能完整可用

---

## Phase 7: 收尾与优化

**目的**: 跨用户故事的改进和完善

- [ ] T049 添加应用图标和窗口标题 in src/main.py
- [ ] T050 添加菜单栏（文件-选择数据目录、帮助-关于）in src/ui/main_window.py
- [ ] T051 添加状态栏显示当前操作状态 in src/ui/main_window.py
- [ ] T052 完善错误处理和用户提示 in src/services/*.py
- [ ] T053 按 quickstart.md 验证完整功能流程

---

## 依赖关系与执行顺序

### 阶段依赖

- **Phase 1 (初始化)**: 无依赖，可立即开始
- **Phase 2 (基础设施)**: 依赖 Phase 1 完成，阻塞所有用户故事
- **Phase 3-6 (用户故事)**: 依赖 Phase 2 完成
  - 可按 P1 → P2 → P3 → P4 顺序执行
  - 或在有多人时并行开发
- **Phase 7 (收尾)**: 依赖所有用户故事完成

### 用户故事依赖

- **US1 (P1)**: Phase 2 完成后可开始，无其他故事依赖
- **US2 (P2)**: Phase 2 完成后可开始，使用 US1 创建的模板进行测试
- **US3 (P3)**: Phase 2 完成后可开始，依赖 US2 的文件树组件
- **US4 (P4)**: Phase 2 完成后可开始，依赖 US3 的流程步骤显示

### 并行机会

- Phase 1: T003, T004 可并行
- Phase 2: T006, T007, T008, T009 可并行（模型类）
- Phase 3: T016, T017 可并行（媒体处理）
- Phase 4: T028, T029, T030 可并行（播放器组件）

---

## 并行执行示例

```bash
# Phase 2 模型类可并行创建:
Task: "实现 Template 数据类 in src/models/template.py"
Task: "实现 GeneratedProject 数据类 in src/models/project.py"
Task: "实现 WorkflowStep 数据类 in src/models/project.py"

# Phase 4 播放器组件可并行创建:
Task: "实现视频播放器组件 in src/ui/video_player.py"
Task: "实现音频播放器组件 in src/ui/audio_player.py"
Task: "实现文本编辑器组件 in src/ui/text_editor.py"
```

---

## 实现策略

### MVP 优先（仅用户故事 1）

1. 完成 Phase 1: 初始化
2. 完成 Phase 2: 基础设施（关键阻塞）
3. 完成 Phase 3: 用户故事 1
4. **停止并验证**: 独立测试模板管理功能
5. 可用于演示的最小可用版本

### 增量交付

1. 完成初始化 + 基础设施 → 基础就绪
2. 添加 US1 → 独立测试 → 可用版本 (MVP!)
3. 添加 US2 → 独立测试 → 增强版本（浏览预览）
4. 添加 US3 → 独立测试 → 增强版本（流程管理）
5. 添加 US4 → 独立测试 → 完整版本（Prompt管理）
6. 每个故事增加价值但不破坏之前的功能

---

## 备注

- [P] 标记 = 不同文件，无依赖，可并行
- [Story] 标签将任务映射到特定用户故事
- 每个用户故事应可独立完成和测试
- 每个任务或逻辑分组后提交
- 在任何检查点可停止并独立验证故事
- 避免：模糊任务、同文件冲突、破坏独立性的跨故事依赖
