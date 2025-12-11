"""
文件树组件

显示模板列表、预设文件位置和生成项目的树形结构。
"""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QBrush, QDragEnterEvent, QDragMoveEvent, QDropEvent

from models.template import Template
from models.project import GeneratedProject, WorkflowStep


class FileTreeWidget(QTreeWidget):
    """文件树组件

    显示模板、预设文件和生成项目的树形结构。
    """

    # 信号：选择项发生变化
    # 参数: (类型, 模板, 项目, 步骤, 文件路径)
    selection_changed = Signal(str, object, object, object, object)

    # 信号：文件被拖拽到节点
    # 参数: (文件路径, 节点类型, 模板, 项目, 步骤, file_type)
    file_dropped_on_node = Signal(Path, str, object, object, object, str)

    # 节点类型常量
    TYPE_TEMPLATE = "template"
    TYPE_TEMPLATE_FILE = "template_file"
    TYPE_PROJECT = "project"
    TYPE_STEP = "step"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._setup_ui()
        self._connect_signals()

        # 存储模板数据
        self.templates: List[Template] = []

        # 初始展开状态（从配置加载）
        self._initial_expanded_templates: set = set()
        self._initial_expanded_projects: set = set()

    def _setup_ui(self):
        """设置 UI"""
        self.setHeaderHidden(True)
        self.setIndentation(20)
        self.setAnimated(True)
        self.setAcceptDrops(True)
        # 放大字体
        font = self.font()
        font.setPointSize(11)
        self.setFont(font)

    def _connect_signals(self):
        """连接信号"""
        self.itemClicked.connect(self._on_item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)

    def set_initial_expanded_state(self, templates: set, projects: set):
        """设置初始展开状态（从配置加载）

        Args:
            templates: 展开的模板名集合
            projects: 展开的项目集合 (模板名, 项目编号)
        """
        self._initial_expanded_templates = templates
        self._initial_expanded_projects = projects

    def refresh(self, templates: List[Template]):
        """刷新文件树

        Args:
            templates: 模板列表
        """
        # 保存当前展开状态（如果树不为空）
        if self.topLevelItemCount() > 0:
            expanded_templates = self._get_expanded_templates()
            expanded_projects = self._get_expanded_projects()
        else:
            # 首次加载，使用初始状态
            expanded_templates = self._initial_expanded_templates
            expanded_projects = self._initial_expanded_projects

        self.clear()
        self.templates = templates

        for template in templates:
            template_item = self._add_template_node(template)

            # 恢复模板展开状态
            if template.name in expanded_templates:
                template_item.setExpanded(True)

            # 恢复项目展开状态
            for i in range(template_item.childCount()):
                child = template_item.child(i)
                data = child.data(0, Qt.ItemDataRole.UserRole)
                if data and data.get('type') == self.TYPE_PROJECT:
                    project = data.get('project')
                    if project and (template.name, project.number) in expanded_projects:
                        child.setExpanded(True)

    def _get_expanded_templates(self) -> set:
        """获取当前展开的模板名称集合"""
        expanded = set()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.isExpanded():
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data and data.get('template'):
                    expanded.add(data['template'].name)
        return expanded

    def _get_expanded_projects(self) -> set:
        """获取当前展开的项目 (模板名, 项目编号) 集合"""
        expanded = set()
        for i in range(self.topLevelItemCount()):
            template_item = self.topLevelItem(i)
            template_data = template_item.data(0, Qt.ItemDataRole.UserRole)
            if not template_data:
                continue
            template = template_data.get('template')
            if not template:
                continue

            for j in range(template_item.childCount()):
                child = template_item.child(j)
                if child.isExpanded():
                    data = child.data(0, Qt.ItemDataRole.UserRole)
                    if data and data.get('type') == self.TYPE_PROJECT:
                        project = data.get('project')
                        if project:
                            expanded.add((template.name, project.number))
        return expanded

    def _add_template_node(self, template: Template) -> QTreeWidgetItem:
        """添加模板节点

        Args:
            template: 模板对象

        Returns:
            创建的树节点
        """
        # 创建模板节点
        template_item = QTreeWidgetItem([template.name])
        template_item.setData(0, Qt.ItemDataRole.UserRole, {
            'type': self.TYPE_TEMPLATE,
            'template': template,
        })
        self.addTopLevelItem(template_item)

        # 添加模板文件节点
        file_types = [
            ('video', '模板视频', template.video_path),
            ('frame', '模板头帧', template.frame_path),
            ('audio', '模板音频', template.audio_path),
            ('subtitle', '模板字幕', template.subtitle_path),
        ]

        for file_type, label, file_path in file_types:
            file_item = self._create_file_item(label, file_path)
            file_item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': self.TYPE_TEMPLATE_FILE,
                'template': template,
                'file_type': file_type,
                'file_path': file_path,
            })
            template_item.addChild(file_item)

        # 添加生成项目节点
        for project in template.projects:
            self._add_project_node(template_item, template, project)

        return template_item

    def _add_project_node(
        self,
        parent_item: QTreeWidgetItem,
        template: Template,
        project: GeneratedProject
    ) -> QTreeWidgetItem:
        """添加生成项目节点

        Args:
            parent_item: 父节点
            template: 所属模板
            project: 生成项目

        Returns:
            创建的树节点
        """
        # 创建项目节点
        status = project.get_completion_status()
        project_label = f"[{project.number}] ({status['completed']}/{status['total']})"

        project_item = QTreeWidgetItem([project_label])
        project_item.setData(0, Qt.ItemDataRole.UserRole, {
            'type': self.TYPE_PROJECT,
            'template': template,
            'project': project,
        })
        parent_item.addChild(project_item)

        # 添加步骤节点
        for step in project.steps:
            step_item = self._create_step_item(step)
            step_item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': self.TYPE_STEP,
                'template': template,
                'project': project,
                'step': step,
                'file_path': step.file_path,
            })
            project_item.addChild(step_item)

        return project_item

    def _create_file_item(
        self,
        label: str,
        file_path: Optional[Path]
    ) -> QTreeWidgetItem:
        """创建文件节点

        Args:
            label: 显示文本
            file_path: 文件路径（None 表示未设置）

        Returns:
            创建的树节点
        """
        if file_path and file_path.exists():
            display_text = f"{label} ({file_path.name})"
            item = QTreeWidgetItem([display_text])
        else:
            display_text = f"{label} (未设置)"
            item = QTreeWidgetItem([display_text])
            # 未设置的文件显示灰色
            item.setForeground(0, QBrush(QColor(153, 153, 153)))

        return item

    def _create_step_item(self, step: WorkflowStep) -> QTreeWidgetItem:
        """创建步骤节点

        Args:
            step: 流程步骤

        Returns:
            创建的树节点
        """
        # prompt 类型的步骤直接标记为完成
        is_prompt_step = step.id.endswith('_prompt')
        is_done = step.is_completed() or is_prompt_step

        status_icon = "✓" if is_done else "○"
        display_text = f"{status_icon} {step.name}"

        if step.is_completed() and step.file_path:
            display_text += f" ({step.file_path.name})"

        item = QTreeWidgetItem([display_text])

        # 未完成的步骤显示灰色（prompt 步骤不显示灰色）
        if not is_done:
            item.setForeground(0, QBrush(QColor(153, 153, 153)))

        return item

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """处理节点点击

        Args:
            item: 被点击的节点
            column: 列索引
        """
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        node_type = data.get('type')
        template = data.get('template')
        project = data.get('project')
        step = data.get('step')
        file_path = data.get('file_path')

        self.selection_changed.emit(node_type, template, project, step, file_path)

    def _on_item_expanded(self, item: QTreeWidgetItem):
        """处理节点展开事件

        当模板节点展开时，自动展开其下所有生成项目节点。

        Args:
            item: 被展开的节点
        """
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        node_type = data.get('type')

        # 只有模板节点展开时才自动展开子项目
        if node_type == self.TYPE_TEMPLATE:
            for i in range(item.childCount()):
                child = item.child(i)
                child_data = child.data(0, Qt.ItemDataRole.UserRole)
                if child_data and child_data.get('type') == self.TYPE_PROJECT:
                    child.setExpanded(True)

    def select_template(self, template_name: str):
        """选择指定模板

        Args:
            template_name: 模板名称
        """
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.get('template') and data['template'].name == template_name:
                self.setCurrentItem(item)
                item.setExpanded(True)
                break

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        """拖动中事件"""
        if event.mimeData().hasUrls():
            item = self.itemAt(event.position().toPoint())
            if item:
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data:
                    node_type = data.get('type')
                    # 只接受模板文件节点和步骤节点
                    if node_type in (self.TYPE_TEMPLATE_FILE, self.TYPE_STEP):
                        event.acceptProposedAction()
                        return
            event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """放下事件"""
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        item = self.itemAt(event.position().toPoint())
        if not item:
            event.ignore()
            return

        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            event.ignore()
            return

        node_type = data.get('type')
        if node_type not in (self.TYPE_TEMPLATE_FILE, self.TYPE_STEP):
            event.ignore()
            return

        urls = event.mimeData().urls()
        if not urls:
            event.ignore()
            return

        file_path = Path(urls[0].toLocalFile())
        template = data.get('template')
        project = data.get('project')
        step = data.get('step')
        file_type = data.get('file_type', '')

        event.acceptProposedAction()
        self.file_dropped_on_node.emit(
            file_path, node_type, template, project, step, file_type
        )
