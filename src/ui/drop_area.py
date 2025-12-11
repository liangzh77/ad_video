"""
拖拽区域组件

支持拖拽文件的区域组件。
"""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent


class DropArea(QLabel):
    """拖拽区域

    支持拖拽文件到此区域。
    """

    # 信号：文件被拖入
    file_dropped = Signal(Path)

    def __init__(
        self,
        text: str = "拖拽文件到此处",
        file_extensions: Optional[List[str]] = None,
        parent: Optional[QWidget] = None
    ):
        """初始化拖拽区域

        Args:
            text: 显示文本
            file_extensions: 允许的文件扩展名列表（如 ['.mp4', '.avi']），None 表示接受所有
            parent: 父组件
        """
        super().__init__(text, parent)

        self._file_extensions = file_extensions
        self._default_text = text

        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self._set_normal_style()

    def _set_normal_style(self):
        """设置正常样式"""
        self.setStyleSheet(
            "border: 2px dashed #aaa; "
            "border-radius: 5px; "
            "color: #666; "
            "padding: 20px; "
            "background-color: #fafafa;"
        )

    def _set_hover_style(self):
        """设置悬停样式"""
        self.setStyleSheet(
            "border: 2px dashed #4a90d9; "
            "border-radius: 5px; "
            "color: #4a90d9; "
            "padding: 20px; "
            "background-color: #e8f4fc;"
        )

    def _set_invalid_style(self):
        """设置无效文件样式"""
        self.setStyleSheet(
            "border: 2px dashed #d94a4a; "
            "border-radius: 5px; "
            "color: #d94a4a; "
            "padding: 20px; "
            "background-color: #fce8e8;"
        )

    def set_file_extensions(self, extensions: Optional[List[str]]):
        """设置允许的文件扩展名

        Args:
            extensions: 扩展名列表
        """
        self._file_extensions = extensions

    def _is_valid_file(self, file_path: Path) -> bool:
        """检查文件是否有效

        Args:
            file_path: 文件路径

        Returns:
            是否有效
        """
        if self._file_extensions is None:
            return True

        return file_path.suffix.lower() in [ext.lower() for ext in self._file_extensions]

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = Path(urls[0].toLocalFile())
                if self._is_valid_file(file_path):
                    event.acceptProposedAction()
                    self._set_hover_style()
                    self.setText("松开以添加文件")
                else:
                    self._set_invalid_style()
                    self.setText("不支持的文件类型")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """拖离事件"""
        self._set_normal_style()
        self.setText(self._default_text)

    def dropEvent(self, event: QDropEvent):
        """放下事件"""
        self._set_normal_style()
        self.setText(self._default_text)

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = Path(urls[0].toLocalFile())
                if self._is_valid_file(file_path):
                    event.acceptProposedAction()
                    self.file_dropped.emit(file_path)
