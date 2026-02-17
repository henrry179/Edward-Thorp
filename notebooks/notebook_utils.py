"""
Notebook 工具函数：获取项目路径和输出目录
"""
import os
from pathlib import Path
from datetime import datetime


def get_project_root():
    """
    获取项目根目录（D:\Gitstars\Edward Thorp）
    支持从项目根目录或 notebooks 目录运行
    
    Returns:
        Path: 项目根目录路径
    """
    cwd = Path.cwd()
    # 如果当前目录有 src 文件夹，说明是项目根目录
    if (cwd / 'src').exists():
        return cwd
    # 否则是 notebooks 目录，返回父目录
    return cwd.parent


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


def save_figure(fig, filename_prefix: str, dpi: int = 300):
    """
    保存图片到 output/figures 目录
    
    Args:
        fig: matplotlib figure 对象
        filename_prefix: 文件名前缀（不含扩展名）
        dpi: 图片分辨率，默认 300
    """
    figures_dir = get_figures_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig_path = figures_dir / f"{filename_prefix}_{timestamp}.png"
    fig.savefig(fig_path, dpi=dpi, bbox_inches='tight')
    print(f"图片已保存到: {fig_path}")
    return fig_path
