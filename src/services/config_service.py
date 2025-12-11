"""
配置服务

负责加载和保存应用配置，管理 Prompt 模板。
"""

import json
from pathlib import Path
from typing import List, Optional, Set, Tuple

from models.config import AppConfig, PromptTemplate


class ConfigService:
    """配置服务类

    负责应用配置的加载、保存和管理。
    """

    # 配置文件名
    CONFIG_FILENAME = 'app_config.json'

    # 默认 Prompt 资源目录（相对于 src）
    DEFAULT_PROMPTS_DIR = 'resources/prompts'

    def __init__(self, config_dir: Optional[Path] = None):
        """初始化配置服务

        Args:
            config_dir: 配置文件目录，默认使用用户目录
        """
        if config_dir is None:
            # 默认保存在用户目录下
            config_dir = Path.home() / '.video_material_tool'

        self.config_dir = config_dir
        self.config_path = config_dir / self.CONFIG_FILENAME
        self._config: Optional[AppConfig] = None

    def get_config(self) -> AppConfig:
        """获取当前配置

        如果配置未加载，先加载配置。

        Returns:
            当前应用配置
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def load_config(self) -> AppConfig:
        """加载配置文件

        如果配置文件不存在，创建默认配置。

        Returns:
            加载的配置对象
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                config = AppConfig.from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"配置文件加载失败，使用默认配置: {e}")
                config = self._create_default_config()
        else:
            config = self._create_default_config()

        # 确保 Prompt 模板存在
        self._ensure_prompts(config)

        self._config = config
        return config

    def save_config(self, config: Optional[AppConfig] = None) -> bool:
        """保存配置到文件

        Args:
            config: 要保存的配置，如果为 None 则保存当前配置

        Returns:
            是否保存成功
        """
        if config is None:
            config = self._config

        if config is None:
            return False

        try:
            # 确保目录存在
            self.config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, ensure_ascii=False, indent=2)

            self._config = config
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def set_data_directory(self, directory: Path) -> bool:
        """设置数据目录

        Args:
            directory: 新的数据目录

        Returns:
            是否设置成功
        """
        config = self.get_config()
        config.data_directory = directory
        return self.save_config(config)

    def get_prompt(self, key: str) -> Optional[PromptTemplate]:
        """获取指定的 Prompt 模板

        Args:
            key: Prompt 标识

        Returns:
            Prompt 模板对象，如果不存在返回 None
        """
        config = self.get_config()
        return config.prompts.get(key)

    def update_prompt(self, key: str, content: str) -> bool:
        """更新 Prompt 的用户自定义内容

        Args:
            key: Prompt 标识
            content: 新的内容

        Returns:
            是否更新成功
        """
        config = self.get_config()
        if key in config.prompts:
            config.prompts[key].user_content = content
            return self.save_config(config)
        return False

    def reset_prompt(self, key: str) -> bool:
        """重置 Prompt 为默认内容

        Args:
            key: Prompt 标识

        Returns:
            是否重置成功
        """
        config = self.get_config()
        if key in config.prompts:
            config.prompts[key].user_content = None
            return self.save_config(config)
        return False

    def _create_default_config(self) -> AppConfig:
        """创建默认配置

        Returns:
            默认配置对象
        """
        return AppConfig()

    def _ensure_prompts(self, config: AppConfig) -> None:
        """确保 Prompt 模板存在

        如果配置中没有 Prompt 模板，从资源文件加载默认内容。

        Args:
            config: 配置对象
        """
        # 定义需要的 Prompt 模板
        prompt_definitions = [
            {
                'key': 'subtitle',
                'name': '字幕生成 Prompt',
                'filename': 'subtitle.txt',
            },
            {
                'key': 'frame',
                'name': '头帧生成 Prompt',
                'filename': 'frame.txt',
            },
        ]

        # 获取资源目录
        src_dir = Path(__file__).parent.parent
        prompts_dir = src_dir / self.DEFAULT_PROMPTS_DIR

        for prompt_def in prompt_definitions:
            key = prompt_def['key']
            if key not in config.prompts:
                # 从文件加载默认内容
                default_content = self._load_default_prompt(
                    prompts_dir / prompt_def['filename']
                )
                config.prompts[key] = PromptTemplate(
                    key=key,
                    name=prompt_def['name'],
                    default_content=default_content,
                )

    def _load_default_prompt(self, file_path: Path) -> str:
        """从文件加载默认 Prompt 内容

        Args:
            file_path: Prompt 文件路径

        Returns:
            文件内容，如果文件不存在返回空字符串
        """
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"加载 Prompt 文件失败: {e}")
        return ""

    def get_expanded_state(self) -> Tuple[Set[str], Set[Tuple[str, str]]]:
        """获取展开状态

        Returns:
            (展开的模板名集合, 展开的项目集合)
        """
        config = self.get_config()
        expanded_templates = set(config.expanded_templates)
        expanded_projects = set(config.expanded_projects)
        return expanded_templates, expanded_projects

    def save_expanded_state(
        self,
        expanded_templates: Set[str],
        expanded_projects: Set[Tuple[str, str]]
    ) -> bool:
        """保存展开状态

        Args:
            expanded_templates: 展开的模板名集合
            expanded_projects: 展开的项目集合

        Returns:
            是否保存成功
        """
        config = self.get_config()
        config.expanded_templates = list(expanded_templates)
        config.expanded_projects = list(expanded_projects)
        return self.save_config(config)
