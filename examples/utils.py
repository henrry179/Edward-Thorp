"""
工具函数：获取项目路径和输出目录
"""
import os
from pathlib import Path


def get_project_root():
    """
    获取项目根目录（D:\Gitstars\Edward Thorp）
    
    Returns:
        Path: 项目根目录路径
    """
    # 获取当前文件的目录（examples/）
    current_file = Path(__file__).resolve()
    # 项目根目录是 examples/ 的父目录
    project_root = current_file.parent.parent
    return project_root


def get_output_dir(subdir: str = ""):
    """
    获取输出目录路径
    
    Args:
        subdir: 子目录名称，如 'figures', 'data', 'reports'
    
    Returns:
        Path: 输出目录路径
    """
    project_root = get_project_root()
    output_dir = project_root / "output"
    if subdir:
        output_dir = output_dir / subdir
    # 确保目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_figures_dir():
    """获取图片输出目录"""
    return get_output_dir("figures")


def get_data_dir():
    """获取数据输出目录"""
    return get_output_dir("data")


def get_reports_dir():
    """获取报告输出目录"""
    return get_output_dir("reports")
