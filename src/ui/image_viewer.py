"""
图片查看器组件

用于预览图片文件。
"""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap


class ImageViewer(QWidget):
    """图片查看器

    显示图片文件，支持缩放适应窗口。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_path: Optional[Path] = None
        self._original_pixmap: Optional[QPixmap] = None
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.scroll_area)

        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0;")
        self.scroll_area.setWidget(self.image_label)

    def load_image(self, file_path: Path):
        """加载并显示图片

        Args:
            file_path: 图片文件路径
        """
        self._current_path = file_path
        self._original_pixmap = None

        if not file_path.exists():
            self.image_label.setText("图片文件不存在")
            return

        pixmap = QPixmap(str(file_path))

        if pixmap.isNull():
            self.image_label.setText("无法加载图片")
            return

        # 保存原始图片
        self._original_pixmap = pixmap

        # 延迟缩放，等待布局完成后再执行
        QTimer.singleShot(0, self._scale_image)

    def _scale_image(self):
        """根据视口大小缩放图片"""
        if self._original_pixmap is None:
            return

        # 使用滚动区域视口大小
        viewport_size = self.scroll_area.viewport().size()

        # 缩放图片以适应视口
        scaled_pixmap = self._original_pixmap.scaled(
            viewport_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.image_label.setPixmap(scaled_pixmap)

    def clear(self):
        """清除显示"""
        self._current_path = None
        self._original_pixmap = None
        self.image_label.clear()
        self.image_label.setText("")

    def resizeEvent(self, event):
        """窗口大小变化时重新缩放图片"""
        super().resizeEvent(event)
        if self._original_pixmap is not None:
            self._scale_image()
