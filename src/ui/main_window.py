"""
主窗口

应用的主窗口，包含左右分栏布局和菜单栏。
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QLabel,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QPushButton,
    QInputDialog,
)
from PySide6.QtCore import Qt

from services.config_service import ConfigService
from services.file_service import FileService
from services.media_service import MediaService
from ui.file_tree import FileTreeWidget
from ui.preview_panel import PreviewPanel


class MainWindow(QMainWindow):
    """主窗口类

    包含左侧文件树和右侧预览区的双栏布局。
    """

    # 文件扩展名定义
    VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
    AUDIO_EXTENSIONS = ['.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac']
    SUBTITLE_EXTENSIONS = ['.srt', '.ass', '.vtt']

    def __init__(self):
        super().__init__()

        # 初始化服务
        self.config_service = ConfigService()
        self.file_service = FileService()
        self.media_service = MediaService()

        # 当前选中的模板
        self.current_template = None
        self.current_template_path = None
        self.current_project = None
        self.current_step = None

        # 设置窗口属性
        self._setup_window()

        # 创建菜单栏
        self._setup_menu_bar()

        # 创建主布局
        self._setup_main_layout()

        # 创建状态栏
        self._setup_status_bar()

        # 首次启动检查数据目录
        self._check_data_directory()

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("视频物料整理工具")
        self.setMinimumSize(1000, 600)
        # 默认最大化窗口
        self.showMaximized()

    def _setup_menu_bar(self):
        """设置菜单栏"""
        menu_bar = self.menuBar()

        # 文件菜单
        file_menu = menu_bar.addMenu("文件(&F)")

        # 新建模板
        new_template_action = file_menu.addAction("新建模板(&N)...")
        new_template_action.triggered.connect(self._on_new_template)

        # 刷新
        refresh_action = file_menu.addAction("刷新(&R)")
        refresh_action.triggered.connect(self._refresh_file_tree)

        file_menu.addSeparator()

        # 选择数据目录
        select_dir_action = file_menu.addAction("选择数据目录(&D)...")
        select_dir_action.triggered.connect(self._on_select_data_directory)

        file_menu.addSeparator()

        # 退出
        exit_action = file_menu.addAction("退出(&X)")
        exit_action.triggered.connect(self.close)

        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助(&H)")

        # 关于
        about_action = help_menu.addAction("关于(&A)")
        about_action.triggered.connect(self._on_about)

    def _setup_main_layout(self):
        """设置主布局"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建水平布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # 左侧面板（文件树区域）
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # 左侧标题和新建按钮
        left_header = QHBoxLayout()
        left_title = QLabel("模板列表")
        left_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_header.addWidget(left_title)
        left_header.addStretch()

        new_template_btn = QPushButton("+ 新建模板")
        new_template_btn.clicked.connect(self._on_new_template)
        left_header.addWidget(new_template_btn)

        new_project_btn = QPushButton("+ 新建生成")
        new_project_btn.clicked.connect(self._on_new_project)
        left_header.addWidget(new_project_btn)

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._refresh_file_tree)
        left_header.addWidget(refresh_btn)

        left_layout.addLayout(left_header)

        # 文件树组件
        self.file_tree = FileTreeWidget()
        self.file_tree.selection_changed.connect(self._on_tree_selection_changed)
        self.file_tree.file_dropped_on_node.connect(self._on_file_dropped_on_node)
        left_layout.addWidget(self.file_tree, 1)

        splitter.addWidget(self.left_panel)

        # 右侧面板（预览区域）
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)

        # 右侧标题
        right_title = QLabel("预览")
        right_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(right_title)

        # 预览面板
        self.preview_panel = PreviewPanel()
        self.preview_panel.set_config_service(self.config_service)
        right_layout.addWidget(self.preview_panel, 1)

        splitter.addWidget(self.right_panel)

        # 设置分割器初始比例（左:右 = 1:3）
        splitter.setSizes([300, 900])

    def _setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status("就绪")

    def _update_status(self, message: str):
        """更新状态栏消息"""
        self.status_bar.showMessage(message)

    def _check_data_directory(self):
        """检查数据目录"""
        config = self.config_service.get_config()

        # 加载展开状态
        expanded_templates, expanded_projects = self.config_service.get_expanded_state()
        self.file_tree.set_initial_expanded_state(expanded_templates, expanded_projects)

        if config.data_directory is None or not config.data_directory.exists():
            self._show_first_run_dialog()
        else:
            self.file_service.set_data_directory(config.data_directory)
            self._refresh_file_tree()

    def closeEvent(self, event):
        """窗口关闭事件，保存展开状态"""
        # 保存展开状态
        expanded_templates = self.file_tree._get_expanded_templates()
        expanded_projects = self.file_tree._get_expanded_projects()
        self.config_service.save_expanded_state(expanded_templates, expanded_projects)

        # 停止播放器
        self.preview_panel.show_empty()

        event.accept()

    def _show_first_run_dialog(self):
        """显示首次运行对话框"""
        QMessageBox.information(
            self,
            "欢迎使用",
            "这是您第一次运行本应用。\n\n请选择一个目录作为数据存储位置，"
            "所有模板和生成的视频都将保存在该目录中。",
            QMessageBox.StandardButton.Ok,
        )
        self._on_select_data_directory()

    def _refresh_file_tree(self):
        """刷新文件树"""
        templates = self.file_service.scan_data_directory()
        self.file_tree.refresh(templates)
        self._update_status(f"已加载 {len(templates)} 个模板")

    def _on_tree_selection_changed(self, node_type, template, project, step, file_path):
        """处理文件树选择变化"""
        # 更新当前选中状态
        self.current_template = template
        self.current_template_path = template.path if template else None
        self.current_project = project
        self.current_step = step

        # 预览文件或 Prompt
        if step is not None and step.has_prompt and step.prompt_key:
            # 如果步骤有 Prompt，显示 Prompt 编辑器
            self.preview_panel.show_prompt(step.prompt_key)
        elif file_path and Path(file_path).exists():
            self.preview_panel.preview_file(file_path)
        else:
            self.preview_panel.show_empty()

        # 更新状态栏
        if template:
            status = f"模板: {template.name}"
            if project:
                status += f" | 项目: {project.number}"
            if step:
                status += f" | 步骤: {step.name}"
            self._update_status(status)

    def _import_template_video(self, file_path: Path):
        """导入模板视频"""
        template_name = self.current_template_path.name
        new_name = f"模板，视频，{template_name}{file_path.suffix}"

        success, message, _ = self.file_service.copy_and_rename_file(
            file_path, self.current_template_path, new_name
        )

        if success:
            self._update_status(f"视频已设置: {new_name}")
            self._refresh_file_tree()
        else:
            QMessageBox.warning(self, "失败", message)

    def _import_template_frame(self, file_path: Path):
        """导入模板头帧"""
        template_name = self.current_template_path.name
        new_name = f"模板，头帧，{template_name}{file_path.suffix}"

        success, message, _ = self.file_service.copy_and_rename_file(
            file_path, self.current_template_path, new_name
        )

        if success:
            self._update_status(f"头帧已设置: {new_name}")
            self._refresh_file_tree()
        else:
            QMessageBox.warning(self, "失败", message)

    def _import_template_audio(self, file_path: Path):
        """导入模板音频"""
        template_name = self.current_template_path.name
        new_name = f"模板，声音，{template_name}{file_path.suffix}"

        success, message, _ = self.file_service.copy_and_rename_file(
            file_path, self.current_template_path, new_name
        )

        if success:
            self._update_status(f"音频已设置: {new_name}")
            self._refresh_file_tree()
        else:
            QMessageBox.warning(self, "失败", message)

    def _import_template_subtitle(self, file_path: Path):
        """导入模板字幕"""
        template_name = self.current_template_path.name
        new_name = f"模板，字幕，{template_name}{file_path.suffix}"

        success, message, _ = self.file_service.copy_and_rename_file(
            file_path, self.current_template_path, new_name
        )

        if success:
            self._update_status(f"字幕已设置: {new_name}")
            self._refresh_file_tree()
        else:
            QMessageBox.warning(self, "失败", message)

    def _on_file_dropped_on_node(
        self, file_path: Path, node_type: str, template, project, step, file_type: str
    ):
        """处理文件拖拽到树节点"""
        from ui.file_tree import FileTreeWidget

        # 先停止播放器，释放文件占用
        self.preview_panel.show_empty()

        suffix = file_path.suffix.lower()

        if node_type == FileTreeWidget.TYPE_TEMPLATE_FILE:
            # 拖拽到模板文件节点
            template_path = template.path

            if file_type == 'video':
                if suffix not in self.VIDEO_EXTENSIONS:
                    QMessageBox.warning(self, "提示", "模板视频需要视频文件")
                    return
                new_name = f"模板，视频，{template.name}{suffix}"

                # 复制视频文件
                success, message, new_path = self.file_service.copy_and_rename_file(
                    file_path, template_path, new_name
                )

                if success:
                    self._update_status(f"视频已设置: {new_name}")

                    # 自动提取头帧
                    frame_path = template_path / f"模板，头帧，{template.name}.jpg"
                    frame_success, frame_msg = self.media_service.extract_first_frame(
                        new_path, frame_path
                    )
                    if frame_success:
                        self._update_status("已自动提取头帧")

                    # 自动提取音频
                    audio_path = template_path / f"模板，声音，{template.name}.mp3"
                    audio_success, audio_msg = self.media_service.extract_audio(
                        new_path, audio_path
                    )
                    if audio_success:
                        self._update_status("已自动提取音频")

                    self._refresh_file_tree()
                    # 自动预览视频
                    if new_path:
                        self.preview_panel.preview_file(new_path)
                else:
                    QMessageBox.warning(self, "失败", message)
                return

            elif file_type == 'frame':
                if suffix not in self.IMAGE_EXTENSIONS:
                    QMessageBox.warning(self, "提示", "模板头帧需要图片文件")
                    return
                new_name = f"模板，头帧，{template.name}{suffix}"
            elif file_type == 'audio':
                if suffix not in self.AUDIO_EXTENSIONS:
                    QMessageBox.warning(self, "提示", "模板音频需要音频文件")
                    return
                new_name = f"模板，声音，{template.name}{suffix}"
            elif file_type == 'subtitle':
                if suffix not in self.SUBTITLE_EXTENSIONS:
                    QMessageBox.warning(self, "提示", "模板字幕需要字幕文件")
                    return
                new_name = f"模板，字幕，{template.name}{suffix}"
            else:
                return

            success, message, new_path = self.file_service.copy_and_rename_file(
                file_path, template_path, new_name
            )

            if success:
                self._update_status(f"文件已设置: {new_name}")
                self._refresh_file_tree()
                # 自动预览
                if new_path:
                    self.preview_panel.preview_file(new_path)
            else:
                QMessageBox.warning(self, "失败", message)

        elif node_type == FileTreeWidget.TYPE_STEP:
            # 拖拽到步骤节点
            text_extensions = ['.txt', '.md']
            valid_extensions = {
                'subtitle_prompt': text_extensions,
                'subtitle': self.SUBTITLE_EXTENSIONS,
                'voice': self.AUDIO_EXTENSIONS,
                'frame_prompt': text_extensions,
                'frame': self.IMAGE_EXTENSIONS,
                'kling': self.VIDEO_EXTENSIONS,
                'final': self.VIDEO_EXTENSIONS,
            }

            expected = valid_extensions.get(step.id, [])
            if expected and suffix not in expected:
                QMessageBox.warning(
                    self, "提示",
                    f"{step.name}需要的文件类型: {', '.join(expected)}"
                )
                return

            # 如果步骤已有文件，先删除旧文件
            if step.file_path and step.file_path.exists():
                self.file_service.delete_file(step.file_path)

            # 构建目标文件名
            new_name = step.expected_filename.replace('*', file_path.stem)
            if '*' not in step.expected_filename:
                new_name = step.expected_filename.rsplit('.', 1)[0] + suffix

            success, message, new_path = self.file_service.copy_and_rename_file(
                file_path, project.path, new_name
            )

            if success:
                self._update_status(f"文件已添加: {new_name}")
                self._refresh_file_tree()
                # 自动预览
                if new_path:
                    self.preview_panel.preview_file(new_path)
            else:
                QMessageBox.warning(self, "失败", message)

    def _on_select_data_directory(self):
        """处理选择数据目录"""
        config = self.config_service.get_config()
        initial_dir = str(config.data_directory) if config.data_directory else ""

        directory = QFileDialog.getExistingDirectory(
            self,
            "选择数据目录",
            initial_dir,
            QFileDialog.Option.ShowDirsOnly,
        )

        if directory:
            dir_path = Path(directory)
            if self.config_service.set_data_directory(dir_path):
                self.file_service.set_data_directory(dir_path)
                self._refresh_file_tree()
                self._update_status(f"数据目录已设置为: {directory}")
            else:
                QMessageBox.warning(
                    self,
                    "设置失败",
                    "无法保存数据目录设置，请重试。",
                )

    def _on_new_template(self):
        """处理新建模板"""
        config = self.config_service.get_config()

        if config.data_directory is None:
            QMessageBox.warning(self, "提示", "请先设置数据目录。")
            self._on_select_data_directory()
            return

        name, ok = QInputDialog.getText(self, "新建模板", "请输入模板名称:")

        if ok and name:
            success, message, path = self.file_service.create_template_folder(name)

            if success:
                self._update_status(message)
                self._refresh_file_tree()
                self.file_tree.select_template(name)
            else:
                QMessageBox.warning(self, "失败", message)

    def _on_new_project(self):
        """处理新建生成视频"""
        if self.current_template_path is None:
            QMessageBox.warning(self, "提示", "请先选择一个模板。")
            return

        success, message, project = self.file_service.create_project_folder(
            self.current_template_path
        )

        if success:
            self._update_status(message)
            self._refresh_file_tree()
        else:
            QMessageBox.warning(self, "失败", message)

    def _on_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            "视频物料整理工具\n\n"
            "版本: 1.0.0\n\n"
            "用于管理视频制作物料的本地桌面应用。",
        )
