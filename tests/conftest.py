"""
pytest 配置文件
"""
import sys
import os

# 添加 src 目录到 Python 路径，使 cb_arb 可被导入
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_root = os.path.join(project_root, 'src')
if src_root not in sys.path:
    sys.path.insert(0, src_root)
