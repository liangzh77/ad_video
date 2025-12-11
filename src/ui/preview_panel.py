"""
预览面板

根据文件类型显示不同的预览组件。
"""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QLabel,
)
from PySide6.QtCore import Qt

from services.config_service import ConfigService


class PreviewPanel(QWidget):
    """预览面板

    根据文件类型切换显示不同的预览组件。
    """

    # 预览类型常量
    PREVIEW_NONE = 0
    PREVIEW_VIDEO = 1
    PREVIEW_AUDIO = 2
    PREVIEW_IMAGE = 3
    PREVIEW_TEXT = 4
    PREVIEW_PROMPT = 5

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._config_service: Optional[ConfigService] = None
        self._setup_ui()

    def set_config_service(self, config_service: ConfigService):
        """设置配置服务

        Args:
            config_service: 配置服务实例
        """
        self._config_service = config_service
        self.prompt_editor.set_config_service(config_service)

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 使用 QStackedWidget 切换不同预览组件
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # 空白占位符
        self.empty_label = QLabel("选择文件以预览")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "border: 1px dashed #ccc; color: #999; padding: 20px;"
        )
        self.stack.addWidget(self.empty_label)

        # 视频播放器
        from .video_player import VideoPlayer
        self.video_player = VideoPlayer()
        self.stack.addWidget(self.video_player)

        # 音频播放器
        from .audio_player import AudioPlayer
        self.audio_player = AudioPlayer()
        self.stack.addWidget(self.audio_player)

        # 图片预览组件
        from .image_viewer import ImageViewer
        self.image_viewer = ImageViewer()
        self.stack.addWidget(self.image_viewer)

        # 文本编辑器组件
        from .text_editor import TextEditor
        self.text_editor = TextEditor()
        self.stack.addWidget(self.text_editor)

        # Prompt 编辑器组件
        from .prompt_editor import PromptEditor
        self.prompt_editor = PromptEditor()
        self.stack.addWidget(self.prompt_editor)

    def show_empty(self):
        """显示空白状态"""
        # 清除媒体播放器（释放文件占用）
        self.video_player.clear()
        self.audio_player.clear()
        self.stack.setCurrentIndex(self.PREVIEW_NONE)

    def show_video(self, file_path: Path):
        """显示视频预览

        Args:
            file_path: 视频文件路径
        """
        # 清除音频播放器（释放文件占用）
        self.audio_player.clear()
        self.video_player.load_video(file_path)
        self.stack.setCurrentIndex(self.PREVIEW_VIDEO)

    def show_audio(self, file_path: Path):
        """显示音频预览

        Args:
            file_path: 音频文件路径
        """
        # 清除视频播放器（释放文件占用）
        self.video_player.clear()
        self.audio_player.load_audio(file_path)
        self.stack.setCurrentIndex(self.PREVIEW_AUDIO)

    def show_image(self, file_path: Path):
        """显示图片预览

        Args:
            file_path: 图片文件路径
        """
        self._stop_media_players()
        self.image_viewer.load_image(file_path)
        self.stack.setCurrentIndex(self.PREVIEW_IMAGE)

    def show_text(self, file_path: Path):
        """显示文本预览

        Args:
            file_path: 文本文件路径
        """
        self._stop_media_players()
        self.text_editor.load_file(file_path)
        self.stack.setCurrentIndex(self.PREVIEW_TEXT)

    def show_prompt(self, prompt_key: str):
        """显示 Prompt 编辑器

        Args:
            prompt_key: Prompt 标识
        """
        self._stop_media_players()
        self.prompt_editor.load_prompt(prompt_key)
        self.stack.setCurrentIndex(self.PREVIEW_PROMPT)

    def _stop_media_players(self):
        """停止所有媒体播放器（释放文件占用）"""
        self.video_player.clear()
        self.audio_player.clear()

    def preview_file(self, file_path: Optional[Path]):
        """根据文件类型自动选择预览方式

        Args:
            file_path: 文件路径
        """
        if file_path is None or not file_path.exists():
            self.show_empty()
            return

        suffix = file_path.suffix.lower()

        # 视频文件
        if suffix in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']:
            self.show_video(file_path)
        # 音频文件
        elif suffix in ['.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac']:
            self.show_audio(file_path)
        # 图片文件
        elif suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
            self.show_image(file_path)
        # 文本文件
        elif suffix in ['.txt', '.srt', '.ass', '.vtt', '.json', '.md']:
            self.show_text(file_path)
        else:
            self.show_empty()

    def get_text_content(self) -> str:
        """获取文本编辑器内容

        Returns:
            当前文本内容
        """
        return self.text_editor.get_content()

    def save_text(self) -> bool:
        """保存文本内容

        Returns:
            是否保存成功
        """
        return self.text_editor.save_file()

    def get_prompt_content(self) -> str:
        """获取 Prompt 编辑器内容

        Returns:
            当前 Prompt 内容
        """
        return self.prompt_editor.get_content()
