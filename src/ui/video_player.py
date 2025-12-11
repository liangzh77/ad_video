"""
视频播放器组件

支持视频播放、暂停、进度控制。
"""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QLabel,
    QStyle,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QMouseEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class ClickableSlider(QSlider):
    """可点击跳转的滑动条"""

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标点击事件，支持点击任意位置跳转"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 计算点击位置对应的值
            if self.orientation() == Qt.Orientation.Horizontal:
                value = self.minimum() + (self.maximum() - self.minimum()) * event.position().x() / self.width()
            else:
                value = self.minimum() + (self.maximum() - self.minimum()) * (self.height() - event.position().y()) / self.height()
            self.setValue(int(value))
            self.sliderMoved.emit(int(value))
        super().mousePressEvent(event)


class VideoPlayer(QWidget):
    """视频播放器

    支持视频播放、暂停、进度控制。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_path: Optional[Path] = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 视频显示区域
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget, 1)

        # 媒体播放器
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        # 控制栏
        control_layout = QHBoxLayout()

        # 播放/暂停按钮
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.setFixedWidth(40)
        control_layout.addWidget(self.play_btn)

        # 进度条（支持点击跳转）
        self.position_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        control_layout.addWidget(self.position_slider, 1)

        # 时间显示
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFixedWidth(100)
        control_layout.addWidget(self.time_label)

        # 音量控制
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(80)
        control_layout.addWidget(self.volume_slider)

        layout.addLayout(control_layout)

        # 设置初始音量
        self.audio_output.setVolume(0.7)

    def _connect_signals(self):
        """连接信号"""
        self.play_btn.clicked.connect(self._toggle_play)
        self.position_slider.sliderMoved.connect(self._set_position)
        self.volume_slider.valueChanged.connect(self._set_volume)

        self.media_player.positionChanged.connect(self._on_position_changed)
        self.media_player.durationChanged.connect(self._on_duration_changed)
        self.media_player.playbackStateChanged.connect(self._on_state_changed)

    def load_video(self, file_path: Path):
        """加载视频文件并自动播放

        Args:
            file_path: 视频文件路径
        """
        self._current_path = file_path
        self.media_player.setSource(QUrl.fromLocalFile(str(file_path)))
        # 自动播放
        self.media_player.play()

    def _toggle_play(self):
        """切换播放/暂停"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def _set_position(self, position: int):
        """设置播放位置"""
        self.media_player.setPosition(position)

    def _set_volume(self, value: int):
        """设置音量"""
        self.audio_output.setVolume(value / 100)

    def _on_position_changed(self, position: int):
        """处理播放位置变化"""
        self.position_slider.setValue(position)
        self._update_time_label()

    def _on_duration_changed(self, duration: int):
        """处理时长变化"""
        self.position_slider.setRange(0, duration)
        self._update_time_label()

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState):
        """处理播放状态变化"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def _update_time_label(self):
        """更新时间显示"""
        position = self.media_player.position()
        duration = self.media_player.duration()

        position_str = self._format_time(position)
        duration_str = self._format_time(duration)

        self.time_label.setText(f"{position_str} / {duration_str}")

    def _format_time(self, ms: int) -> str:
        """格式化时间

        Args:
            ms: 毫秒数

        Returns:
            格式化的时间字符串 (MM:SS)
        """
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def stop(self):
        """停止播放"""
        self.media_player.stop()

    def clear(self):
        """清除"""
        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self._current_path = None
        self.time_label.setText("00:00 / 00:00")
        self.position_slider.setRange(0, 0)
