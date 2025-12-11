"""
媒体服务

负责视频处理相关操作，如提取头帧、音频等。
"""

from pathlib import Path
from typing import Tuple, Optional


class MediaService:
    """媒体服务类

    处理视频、音频相关操作。
    """

    def extract_first_frame(
        self,
        video_path: Path,
        output_path: Path,
        time_offset: float = 0.0
    ) -> Tuple[bool, str]:
        """从视频提取头帧

        Args:
            video_path: 视频文件路径
            output_path: 输出图片路径
            time_offset: 时间偏移（秒），默认提取第一帧

        Returns:
            (是否成功, 消息)
        """
        if not video_path.exists():
            return False, f"视频文件不存在: {video_path}"

        try:
            from moviepy.editor import VideoFileClip

            clip = VideoFileClip(str(video_path))

            # 确保时间偏移在有效范围内
            if time_offset >= clip.duration:
                time_offset = 0

            # 获取指定时间的帧
            frame = clip.get_frame(time_offset)

            # 保存为图片
            from PIL import Image
            image = Image.fromarray(frame)
            image.save(str(output_path))

            clip.close()

            return True, f"头帧已保存到: {output_path}"
        except ImportError as e:
            return False, f"缺少依赖库: {e}"
        except Exception as e:
            return False, f"提取头帧失败: {e}"

    def extract_audio(
        self,
        video_path: Path,
        output_path: Path
    ) -> Tuple[bool, str]:
        """从视频提取音频

        Args:
            video_path: 视频文件路径
            output_path: 输出音频路径

        Returns:
            (是否成功, 消息)
        """
        if not video_path.exists():
            return False, f"视频文件不存在: {video_path}"

        try:
            from moviepy.editor import VideoFileClip

            clip = VideoFileClip(str(video_path))

            if clip.audio is None:
                clip.close()
                return False, "视频没有音频轨道"

            # 导出音频
            clip.audio.write_audiofile(str(output_path))

            clip.close()

            return True, f"音频已保存到: {output_path}"
        except ImportError as e:
            return False, f"缺少依赖库: {e}"
        except Exception as e:
            return False, f"提取音频失败: {e}"

    def get_video_duration(self, video_path: Path) -> Optional[float]:
        """获取视频时长

        Args:
            video_path: 视频文件路径

        Returns:
            视频时长（秒），失败返回 None
        """
        if not video_path.exists():
            return None

        try:
            from moviepy.editor import VideoFileClip

            clip = VideoFileClip(str(video_path))
            duration = clip.duration
            clip.close()

            return duration
        except Exception:
            return None

    def get_video_info(self, video_path: Path) -> Optional[dict]:
        """获取视频基本信息

        Args:
            video_path: 视频文件路径

        Returns:
            包含视频信息的字典，失败返回 None
        """
        if not video_path.exists():
            return None

        try:
            from moviepy.editor import VideoFileClip

            clip = VideoFileClip(str(video_path))

            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,  # (width, height)
                'has_audio': clip.audio is not None,
            }

            clip.close()

            return info
        except Exception:
            return None
