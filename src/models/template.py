"""
模板数据类

代表一个模板视频及其预处理文件集合。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .project import GeneratedProject


@dataclass
class Template:
    """模板数据类

    Attributes:
        name: 模板名称（即文件夹名）
        path: 模板文件夹完整路径
        video_path: 模板视频路径（可选）
        frame_path: 模板图片路径（可选）
        audio_path: 模板音频路径（可选）
        subtitle_path: 模板文案路径（可选）
        projects: 该模板下的生成项目列表
    """
    name: str
    path: Path
    video_path: Optional[Path] = None
    frame_path: Optional[Path] = None
    audio_path: Optional[Path] = None
    subtitle_path: Optional[Path] = None
    projects: List['GeneratedProject'] = field(default_factory=list)

    def has_video(self) -> bool:
        """检查是否有模板视频"""
        return self.video_path is not None and self.video_path.exists()

    def has_frame(self) -> bool:
        """检查是否有图片"""
        return self.frame_path is not None and self.frame_path.exists()

    def has_audio(self) -> bool:
        """检查是否有音频文件"""
        return self.audio_path is not None and self.audio_path.exists()

    def has_subtitle(self) -> bool:
        """检查是否有文案文件"""
        return self.subtitle_path is not None and self.subtitle_path.exists()

    def get_file_status(self) -> dict:
        """获取各文件的存在状态

        Returns:
            包含各文件类型存在状态的字典
        """
        return {
            'video': self.has_video(),
            'frame': self.has_frame(),
            'audio': self.has_audio(),
            'subtitle': self.has_subtitle(),
        }
