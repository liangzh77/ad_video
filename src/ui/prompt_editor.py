"""
Prompt 编辑器组件

用于显示和编辑大模型 Prompt。
"""

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import Signal

from models.config import PromptTemplate
from services.config_service import ConfigService


class PromptEditor(QWidget):
    """Prompt 编辑器

    显示和编辑大模型 Prompt，支持复制和保存为默认。
    """

    # 信号：Prompt 已更新
    prompt_updated = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_prompt: Optional[PromptTemplate] = None
        self._config_service: Optional[ConfigService] = None

        self._setup_ui()
        self._connect_signals()

    def set_config_service(self, config_service: ConfigService):
        """设置配置服务

        Args:
            config_service: 配置服务实例
        """
        self._config_service = config_service

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题区域
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Prompt")
        self.title_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # 复制按钮
        self.copy_btn = QPushButton("复制")
        self.copy_btn.setToolTip("复制 Prompt 到剪贴板")
        header_layout.addWidget(self.copy_btn)

        # 重置按钮
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setToolTip("重置为默认 Prompt")
        header_layout.addWidget(self.reset_btn)

        # 保存为默认按钮
        self.save_default_btn = QPushButton("保存为默认")
        self.save_default_btn.setToolTip("将当前内容保存为默认 Prompt")
        header_layout.addWidget(self.save_default_btn)

        layout.addLayout(header_layout)

        # 编辑区域
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("在此编辑 Prompt...")
        # 放大字体
        font = self.text_edit.font()
        font.setPointSize(14)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit, 1)

        # 提示信息
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.info_label)

    def _connect_signals(self):
        """连接信号"""
        self.copy_btn.clicked.connect(self._on_copy)
        self.reset_btn.clicked.connect(self._on_reset)
        self.save_default_btn.clicked.connect(self._on_save_default)

    def load_prompt(self, prompt_key: str):
        """加载指定的 Prompt

        Args:
            prompt_key: Prompt 标识
        """
        if self._config_service is None:
            return

        prompt = self._config_service.get_prompt(prompt_key)

        if prompt is None:
            self.clear()
            return

        self._current_prompt = prompt
        self.title_label.setText(f"Prompt: {prompt.name}")
        self.text_edit.setPlainText(prompt.get_content())

        # 更新提示信息
        if prompt.user_content:
            self.info_label.setText("使用自定义 Prompt")
        else:
            self.info_label.setText("使用默认 Prompt")

    def clear(self):
        """清除内容"""
        self._current_prompt = None
        self.title_label.setText("Prompt")
        self.text_edit.clear()
        self.info_label.setText("")

    def _on_copy(self):
        """复制到剪贴板"""
        content = self.text_edit.toPlainText()

        if content:
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            self.info_label.setText("已复制到剪贴板")
        else:
            QMessageBox.warning(self, "提示", "没有内容可复制")

    def _on_reset(self):
        """重置为默认"""
        if self._current_prompt is None or self._config_service is None:
            return

        result = QMessageBox.question(
            self,
            "确认重置",
            "确定要重置为默认 Prompt 吗？\n\n这将清除您的自定义修改。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            if self._config_service.reset_prompt(self._current_prompt.key):
                self.text_edit.setPlainText(self._current_prompt.default_content)
                self.info_label.setText("已重置为默认 Prompt")
                self.prompt_updated.emit(self._current_prompt.key)
            else:
                QMessageBox.warning(self, "失败", "重置失败")

    def _on_save_default(self):
        """保存为默认"""
        if self._current_prompt is None or self._config_service is None:
            return

        content = self.text_edit.toPlainText()

        if not content.strip():
            QMessageBox.warning(self, "提示", "Prompt 内容不能为空")
            return

        result = QMessageBox.question(
            self,
            "确认保存",
            "确定要将当前内容保存为默认 Prompt 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            if self._config_service.update_prompt(self._current_prompt.key, content):
                self.info_label.setText("已保存为默认 Prompt")
                self.prompt_updated.emit(self._current_prompt.key)
            else:
                QMessageBox.warning(self, "失败", "保存失败")

    def get_content(self) -> str:
        """获取当前内容

        Returns:
            Prompt 内容
        """
        return self.text_edit.toPlainText()
