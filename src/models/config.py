"""
应用配置相关数据类

包含 AppConfig 和 PromptTemplate 的定义。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class PromptTemplate:
    """Prompt 模板数据类

    Attributes:
        key: 类型标识，如 'subtitle', 'frame'
        name: 中文名称
        default_content: 默认 Prompt 内容
        user_content: 用户自定义内容（覆盖默认）
    """
    key: str
    name: str
    default_content: str
    user_content: Optional[str] = None

    def get_content(self) -> str:
        """获取当前使用的 Prompt 内容

        如果有用户自定义内容则返回自定义内容，否则返回默认内容。
        """
        return self.user_content if self.user_content else self.default_content

    def to_dict(self) -> dict:
        """转换为字典，用于 JSON 序列化"""
        return {
            'key': self.key,
            'name': self.name,
            'default_content': self.default_content,
            'user_content': self.user_content,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PromptTemplate':
        """从字典创建实例"""
        return cls(
            key=data['key'],
            name=data['name'],
            default_content=data['default_content'],
            user_content=data.get('user_content'),
        )


@dataclass
class AppConfig:
    """应用配置数据类

    Attributes:
        data_directory: 数据根目录
        prompts: Prompt 模板集合
        last_opened_template: 上次打开的模板名
        expanded_templates: 展开的模板名列表
        expanded_projects: 展开的项目列表 [(模板名, 项目编号), ...]
    """
    data_directory: Optional[Path] = None
    prompts: Dict[str, PromptTemplate] = field(default_factory=dict)
    last_opened_template: Optional[str] = None
    expanded_templates: List[str] = field(default_factory=list)
    expanded_projects: List[Tuple[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转换为字典，用于 JSON 序列化"""
        return {
            'data_directory': str(self.data_directory) if self.data_directory else None,
            'prompts': {k: v.to_dict() for k, v in self.prompts.items()},
            'last_opened_template': self.last_opened_template,
            'expanded_templates': self.expanded_templates,
            'expanded_projects': self.expanded_projects,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """从字典创建实例"""
        prompts = {}
        if 'prompts' in data:
            prompts = {k: PromptTemplate.from_dict(v) for k, v in data['prompts'].items()}

        data_dir = data.get('data_directory')

        # 解析展开的项目列表
        expanded_projects = []
        for item in data.get('expanded_projects', []):
            if isinstance(item, (list, tuple)) and len(item) == 2:
                expanded_projects.append((item[0], item[1]))

        return cls(
            data_directory=Path(data_dir) if data_dir else None,
            prompts=prompts,
            last_opened_template=data.get('last_opened_template'),
            expanded_templates=data.get('expanded_templates', []),
            expanded_projects=expanded_projects,
        )
