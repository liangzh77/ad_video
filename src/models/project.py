"""
生成项目和流程步骤数据类

包含 GeneratedProject 和 WorkflowStep 的定义。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .template import Template


@dataclass
class WorkflowStep:
    """流程步骤数据类

    Attributes:
        id: 步骤标识
        name: 步骤中文名称
        description: 步骤描述
        expected_filename: 预期输出文件名模式
        file_path: 实际文件路径（None 表示未完成）
        has_prompt: 是否需要大模型 Prompt
        prompt_key: Prompt 类型标识
    """
    id: str
    name: str
    description: str
    expected_filename: str
    file_path: Optional[Path] = None
    has_prompt: bool = False
    prompt_key: Optional[str] = None

    def is_completed(self) -> bool:
        """检查步骤是否已完成"""
        return self.file_path is not None and self.file_path.exists()

    def get_status(self) -> str:
        """获取步骤状态描述"""
        return "已完成" if self.is_completed() else "待处理"


# 固定的5个流程步骤定义（prompt 类型放在模板级别）
WORKFLOW_STEPS = [
    {
        'id': 'subtitle',
        'name': '文案',
        'description': '视频文案文件',
        'expected_filename': '{number}，文案，{template_name}.srt',
        'has_prompt': False,
        'prompt_key': None,
    },
    {
        'id': 'voice',
        'name': '语音',
        'description': '配音音频',
        'expected_filename': '{number}，语音，*.mp3',
        'has_prompt': False,
        'prompt_key': None,
    },
    {
        'id': 'frame',
        'name': '图片',
        'description': '视频图片',
        'expected_filename': '{number}，图片，{template_name}.jpg',
        'has_prompt': False,
        'prompt_key': None,
    },
    {
        'id': 'kling',
        'name': '可灵视频',
        'description': '生成可灵视频',
        'expected_filename': '{number}，可灵，{template_name}.mp4',
        'has_prompt': False,
        'prompt_key': None,
    },
    {
        'id': 'final',
        'name': '成片导出',
        'description': '导出最终成片',
        'expected_filename': '{number}，成片，{template_name}.mp4',
        'has_prompt': False,
        'prompt_key': None,
    },
]


def create_workflow_steps(number: str, template_name: str = "") -> List[WorkflowStep]:
    """根据编号创建流程步骤列表

    Args:
        number: 项目编号，如 "01"
        template_name: 模板名称

    Returns:
        流程步骤列表
    """
    steps = []
    for step_def in WORKFLOW_STEPS:
        step = WorkflowStep(
            id=step_def['id'],
            name=step_def['name'],
            description=step_def['description'],
            expected_filename=step_def['expected_filename'].format(
                number=number, template_name=template_name
            ),
            has_prompt=step_def['has_prompt'],
            prompt_key=step_def['prompt_key'],
        )
        steps.append(step)
    return steps


@dataclass
class GeneratedProject:
    """生成项目数据类

    Attributes:
        number: 编号，如 "01", "02"
        path: 子文件夹完整路径
        template: 所属模板（可选，避免循环引用）
        template_name: 模板名称
        steps: 流程步骤列表（固定7个）
    """
    number: str
    path: Path
    template: Optional['Template'] = None
    template_name: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理：如果没有步骤则创建默认步骤"""
        if not self.steps:
            self.steps = create_workflow_steps(self.number, self.template_name)

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """根据步骤ID获取步骤

        Args:
            step_id: 步骤标识

        Returns:
            匹配的步骤，如果不存在返回 None
        """
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_completion_status(self) -> dict:
        """获取完成状态统计

        Returns:
            包含完成数和总数的字典
        """
        completed = sum(1 for step in self.steps if step.is_completed())
        return {
            'completed': completed,
            'total': len(self.steps),
            'percentage': completed / len(self.steps) * 100 if self.steps else 0,
        }
