"""
文件服务

负责文件和文件夹的创建、复制、扫描等操作。
"""

import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from models.template import Template
from models.project import GeneratedProject, WorkflowStep, create_workflow_steps


class FileService:
    """文件服务类

    处理所有文件系统相关操作。
    """

    # 模板文件前缀
    TEMPLATE_VIDEO_PREFIX = "模板，视频，"
    TEMPLATE_FRAME_PREFIX = "模板，头帧，"
    TEMPLATE_AUDIO_PREFIX = "模板，声音，"
    TEMPLATE_SUBTITLE_PREFIX = "模板，字幕，"

    def __init__(self, data_directory: Optional[Path] = None):
        """初始化文件服务

        Args:
            data_directory: 数据根目录
        """
        self.data_directory = data_directory

    def set_data_directory(self, directory: Path):
        """设置数据目录

        Args:
            directory: 数据目录路径
        """
        self.data_directory = directory

    def create_template_folder(self, name: str) -> Tuple[bool, str, Optional[Path]]:
        """创建模板文件夹

        Args:
            name: 模板名称

        Returns:
            (是否成功, 消息, 文件夹路径)
        """
        if self.data_directory is None:
            return False, "未设置数据目录", None

        # 检查名称是否合法
        if not name or not name.strip():
            return False, "模板名称不能为空", None

        # 检查是否包含非法字符
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                return False, f"模板名称不能包含字符: {char}", None

        template_path = self.data_directory / name

        # 检查是否已存在
        if template_path.exists():
            return False, f"模板 '{name}' 已存在", None

        try:
            template_path.mkdir(parents=True)
            return True, f"模板 '{name}' 创建成功", template_path
        except Exception as e:
            return False, f"创建失败: {e}", None

    def copy_and_rename_file(
        self,
        source_path: Path,
        target_dir: Path,
        new_name: str
    ) -> Tuple[bool, str, Optional[Path]]:
        """复制文件并重命名

        Args:
            source_path: 源文件路径
            target_dir: 目标目录
            new_name: 新文件名（包含扩展名）

        Returns:
            (是否成功, 消息, 目标文件路径)
        """
        if not source_path.exists():
            return False, f"源文件不存在: {source_path}", None

        if not target_dir.exists():
            return False, f"目标目录不存在: {target_dir}", None

        target_path = target_dir / new_name

        try:
            # 如果目标文件已存在，先删除
            if target_path.exists():
                target_path.unlink()
            shutil.copy2(source_path, target_path)
            return True, "文件复制成功", target_path
        except Exception as e:
            return False, f"复制失败: {e}", None

    def get_next_project_number(self, template_path: Path) -> str:
        """获取下一个可用的项目编号

        Args:
            template_path: 模板文件夹路径

        Returns:
            两位数字字符串，如 "01", "02"
        """
        existing_numbers = []

        for item in template_path.iterdir():
            if item.is_dir() and item.name.isdigit():
                existing_numbers.append(int(item.name))

        if not existing_numbers:
            return "01"

        next_num = max(existing_numbers) + 1
        return f"{next_num:02d}"

    def save_text_file(
        self,
        content: str,
        file_path: Path
    ) -> Tuple[bool, str]:
        """保存文本文件

        Args:
            content: 文本内容
            file_path: 目标文件路径

        Returns:
            (是否成功, 消息)
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "保存成功"
        except Exception as e:
            return False, f"保存失败: {e}"

    def scan_template_folder(self, template_path: Path) -> Template:
        """扫描模板文件夹，检测已有文件

        Args:
            template_path: 模板文件夹路径

        Returns:
            Template 对象
        """
        name = template_path.name
        template = Template(name=name, path=template_path)

        if not template_path.exists():
            return template

        # 扫描模板文件
        for file_path in template_path.iterdir():
            if file_path.is_file():
                filename = file_path.name

                if filename.startswith(self.TEMPLATE_VIDEO_PREFIX):
                    template.video_path = file_path
                elif filename.startswith(self.TEMPLATE_FRAME_PREFIX):
                    template.frame_path = file_path
                elif filename.startswith(self.TEMPLATE_AUDIO_PREFIX):
                    template.audio_path = file_path
                elif filename.startswith(self.TEMPLATE_SUBTITLE_PREFIX):
                    template.subtitle_path = file_path

        # 扫描生成项目
        template.projects = self._scan_projects(template_path, template)

        return template

    def scan_data_directory(self) -> List[Template]:
        """扫描数据目录，获取所有模板

        Returns:
            模板列表
        """
        templates = []

        if self.data_directory is None or not self.data_directory.exists():
            return templates

        for item in self.data_directory.iterdir():
            if item.is_dir():
                template = self.scan_template_folder(item)
                templates.append(template)

        # 按名称排序
        templates.sort(key=lambda t: t.name)
        return templates

    def _scan_projects(
        self,
        template_path: Path,
        template: Template
    ) -> List[GeneratedProject]:
        """扫描模板下的生成项目

        Args:
            template_path: 模板文件夹路径
            template: 所属模板

        Returns:
            生成项目列表
        """
        projects = []

        for item in template_path.iterdir():
            if item.is_dir() and item.name.isdigit():
                project = self.scan_project_folder(item, template)
                projects.append(project)

        # 按编号排序
        projects.sort(key=lambda p: p.number)
        return projects

    def scan_project_folder(
        self,
        project_path: Path,
        template: Optional[Template] = None
    ) -> GeneratedProject:
        """扫描项目文件夹，检测步骤文件

        Args:
            project_path: 项目文件夹路径
            template: 所属模板

        Returns:
            GeneratedProject 对象
        """
        number = project_path.name
        template_name = template.name if template else ""
        project = GeneratedProject(
            number=number,
            path=project_path,
            template=template,
            template_name=template_name,
        )

        if not project_path.exists():
            return project

        # 扫描步骤文件
        for file_path in project_path.iterdir():
            if file_path.is_file():
                filename = file_path.name
                self._match_step_file(project, filename, file_path)

        return project

    def _match_step_file(
        self,
        project: GeneratedProject,
        filename: str,
        file_path: Path
    ):
        """匹配文件到步骤

        Args:
            project: 生成项目
            filename: 文件名
            file_path: 文件路径
        """
        number = project.number

        # 匹配规则（按顺序匹配，注意 subtitle_prompt 要在 subtitle 之前）
        patterns = [
            ('subtitle_prompt', f"{number}，字幕prompt"),
            ('subtitle', f"{number}，字幕"),
            ('voice', f"{number}，语音"),
            ('frame_prompt', f"{number}，头帧prompt"),
            ('frame', f"{number}，头帧"),
            ('kling', f"{number}，可灵"),
            ('final', f"{number}，成片"),
        ]

        for step_id, pattern in patterns:
            if filename.startswith(pattern):
                step = project.get_step(step_id)
                if step:
                    step.file_path = file_path
                break

    def create_project_folder(
        self,
        template_path: Path
    ) -> Tuple[bool, str, Optional[GeneratedProject]]:
        """创建生成项目文件夹

        Args:
            template_path: 模板文件夹路径

        Returns:
            (是否成功, 消息, 项目对象)
        """
        if not template_path.exists():
            return False, "模板文件夹不存在", None

        number = self.get_next_project_number(template_path)
        project_path = template_path / number
        template_name = template_path.name

        try:
            project_path.mkdir()
            project = GeneratedProject(
                number=number,
                path=project_path,
                template_name=template_name,
            )
            return True, f"项目 '{number}' 创建成功", project
        except Exception as e:
            return False, f"创建失败: {e}", None

    def delete_file(self, file_path: Path) -> Tuple[bool, str]:
        """删除文件

        Args:
            file_path: 文件路径

        Returns:
            (是否成功, 消息)
        """
        if not file_path.exists():
            return False, "文件不存在"

        try:
            file_path.unlink()
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {e}"
