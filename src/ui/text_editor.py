"""
文本编辑器组件

用于编辑文案等文本文件。
"""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QMessageBox,
)
from PySide6.QtCore import Signal


class TextEditor(QWidget):
    """文本编辑器

    用于编辑和保存文本文件。
    """

    # 信号：内容已修改
    content_modified = Signal()

    # 信号：文件已保存
    file_saved = Signal(Path)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_path: Optional[Path] = None
        self._is_modified = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 文件名标签
        self.file_label = QLabel()
        layout.addWidget(self.file_label)

        # 文本编辑区
        self.text_edit = QPlainTextEdit()
        self.text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.text_edit, 1)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _connect_signals(self):
        """连接信号"""
        self.text_edit.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        """处理文本变化"""
        self._is_modified = True
        self.content_modified.emit()
        self._update_title()

    def _update_title(self):
        """更新标题显示"""
        if self._current_path:
            title = self._current_path.name
            if self._is_modified:
                title += " *"
            self.file_label.setText(title)

    def load_file(self, file_path: Path):
        """加载文件内容

        Args:
            file_path: 文件路径
        """
        # 如果有未保存的修改，提示用户
        if self._is_modified and self._current_path:
            result = QMessageBox.question(
                self,
                "未保存的修改",
                "当前文件有未保存的修改，是否保存？",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel,
            )

            if result == QMessageBox.StandardButton.Yes:
                self.save_file()
            elif result == QMessageBox.StandardButton.Cancel:
                return

        self._current_path = file_path

        if not file_path.exists():
            self.text_edit.setPlainText("")
            self.file_label.setText("文件不存在")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_edit.setPlainText(content)
            self._is_modified = False
            self._update_title()
        except Exception as e:
            self.text_edit.setPlainText("")
            self.file_label.setText(f"加载失败: {e}")

    def save_file(self) -> bool:
        """保存文件

        Returns:
            是否保存成功
        """
        if self._current_path is None:
            return False

        try:
            with open(self._current_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            self._is_modified = False
            self._update_title()
            self.file_saved.emit(self._current_path)
            return True
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"无法保存文件: {e}")
            return False

    def _on_save(self):
        """处理保存按钮点击"""
        self.save_file()

    def get_content(self) -> str:
        """获取当前文本内容

        Returns:
            文本内容
        """
        return self.text_edit.toPlainText()

    def set_content(self, content: str):
        """设置文本内容

        Args:
            content: 文本内容
        """
        self.text_edit.setPlainText(content)

    def clear(self):
        """清除内容"""
        self._current_path = None
        self._is_modified = False
        self.text_edit.clear()
        self.file_label.setText("")

    def is_modified(self) -> bool:
        """检查是否有未保存的修改

        Returns:
            是否有修改
        """
        return self._is_modified
