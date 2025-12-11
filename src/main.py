"""
视频物料整理工具 - 应用入口

用于管理视频制作物料的本地桌面应用。
"""

import sys
import os

# 添加 src 目录到 Python 路径
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow


# 应用版本号
APP_VERSION = "1.0.0"
APP_NAME = "视频物料整理工具"


def main():
    """应用入口函数"""
    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("VideoMaterialTool")

    # 设置应用样式
    app.setStyle("Fusion")

    # 创建并显示主窗口
    window = MainWindow()
    window.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
    window.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
