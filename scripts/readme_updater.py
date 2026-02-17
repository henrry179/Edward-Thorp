"""
README更新模块
自动更新README.md中的开发进度展示
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from progress_calculator import ProgressCalculator, ModuleProgress


class ReadmeUpdater:
    """README更新器"""
    
    def __init__(self, readme_path: str = "README.md"):
        self.readme_path = Path(readme_path)
        self.content = self._load_readme()
        
    def _load_readme(self) -> str:
        """加载README内容"""
        if self.readme_path.exists():
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def save_readme(self):
        """保存README内容"""
        with open(self.readme_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
    
    def update_progress_section(self, module_progress: Dict[str, ModuleProgress], total_progress: float):
        """
        更新README中的开发进度章节
        """
        # 构建新的进度表格
        progress_table = self._build_progress_table(module_progress, total_progress)
        
        # 查找并替换开发进度章节
        pattern = r'(## 📊 开发进度\s*\n\s*项目当前完成度：)[^\n]*(\s*\n\s*\|[^|]+\|[^|]+\|[^\n]*\n\s*\|[-:|\s]+\|[-:|\s]+\|[^\n]*'
        
        if re.search(pattern, self.content):
            # 更新现有进度章节
            new_section = f"## 📊 开发进度\n\n项目当前完成度：**{total_progress}%**\n\n{progress_table}"
            
            # 替换整个进度章节
            section_pattern = r'## 📊 开发进度.*?(?=\n## |\Z)'
            self.content = re.sub(section_pattern, new_section, self.content, flags=re.DOTALL)
        else:
            # 在目录后添加新的进度章节
            toc_end = self.content.find('## 📖 项目简介')
            if toc_end > 0:
                progress_section = f"""## 📊 开发进度

项目当前完成度：**{total_progress}%**

{progress_table}

详细进度请查看 [开发进度文档](DEVELOPMENT_PROGRESS.md)

"""
                self.content = self.content[:toc_end] + progress_section + self.content[toc_end:]
        
        # 更新最后更新时间
        self._update_last_updated()
    
    def _build_progress_table(self, module_progress: Dict[str, ModuleProgress], total_progress: float) -> str:
        """构建进度表格"""
        lines = [
            "| 模块 | 完成度 |",
            "|------|--------|"
        ]
        
        # 模块映射（保持与README一致）
        module_order = ['core', 'docs', 'examples', 'tests']
        
        for key in module_order:
            if key in module_progress:
                module = module_progress[key]
                status = "✅" if module.percentage >= 90 else "🔄" if module.percentage >= 50 else "📋"
                lines.append(f"| {module.name} | {int(module.percentage)}% {status} |")
        
        return '\n'.join(lines)
    
    def _update_last_updated(self):
        """更新最后更新时间"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 查找最后更新时间
        pattern = r'\*最后更新：\d{4}-\d{2}-\d{2}\*'
        replacement = f'*最后更新：{today}*'
        
        if re.search(pattern, self.content):
            self.content = re.sub(pattern, replacement, self.content)
        else:
            # 在文件末尾添加
            if not self.content.endswith('\n'):
                self.content += '\n'
            self.content += f"\n---\n\n*最后更新：{today}*\n"
    
    def update_badge(self, badge_type: str, value: str):
        """
        更新徽章
        
        Args:
            badge_type: 徽章类型 (version, status, build, tests等)
            value: 徽章值
        """
        badge_patterns = {
            'version': r'(!\[Version\]\(https://img\.shields\.io/badge/version-)[^-\s]+',
            'status': r'(!\[Status\]\(https://img\.shields\.io/badge/status-)[^-]+',
            'build': r'(!\[Build\]\(https://img\.shields\.io/badge/build-)[^-]+',
            'tests': r'(!\[Tests\]\(https://img\.shields\.io/badge/tests-)[^-]+'
        }
        
        if badge_type in badge_patterns:
            pattern = badge_patterns[badge_type]
            replacement = r'\g<1>' + value
            self.content = re.sub(pattern, replacement, self.content)
    
    def update_progress_bar_in_readme(self, progress: float):
        """
        在README中添加进度条可视化
        """
        # 查找开发进度章节并添加进度条
        progress_bar = self._generate_progress_bar(progress)
        
        # 在总体完成度后添加进度条
        pattern = r'(项目当前完成度：\*\*\d+%\*\*)'
        if re.search(pattern, self.content):
            replacement = r'\1\n\n' + progress_bar
            self.content = re.sub(pattern, replacement, self.content)
    
    def _generate_progress_bar(self, progress: float, length: int = 30) -> str:
        """生成ASCII进度条"""
        filled = int(length * progress / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f"```\n{bar} {progress}%\n```"
    
    def sync_with_develoment_progress(self, dev_progress_path: str = "DEVELOPMENT_PROGRESS.md"):
        """
        与DEVELOPMENT_PROGRESS.md同步
        """
        dev_path = Path(dev_progress_path)
        if not dev_path.exists():
            return
        
        with open(dev_path, 'r', encoding='utf-8') as f:
            dev_content = f.read()
        
        # 提取总体进度
        total_match = re.search(r'\*\*总体完成度\*\*\s*\|\s*\*\*(\d+)%\*\*', dev_content)
        if total_match:
            total_progress = int(total_match.group(1))
            
            # 更新README中的总体进度
            pattern = r'(项目当前完成度：\*\*)\d+(%)'
            replacement = r'\g<1>' + str(total_progress) + r'\2'
            self.content = re.sub(pattern, replacement, self.content)
    
    def get_progress_summary_for_readme(self, module_progress: Dict[str, ModuleProgress]) -> str:
        """生成README用的进度摘要"""
        lines = []
        
        for key, module in module_progress.items():
            bar_length = 15
            filled = int(bar_length * module.percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            lines.append(f"- **{module.name}**: {bar} {module.percentage:.0f}%")
        
        return '\n'.join(lines)


if __name__ == "__main__":
    # 测试
    from progress_calculator import ProgressCalculator
    from git_analyzer import GitAnalyzer
    
    calculator = ProgressCalculator()
    analyzer = GitAnalyzer()
    
    commits = analyzer.get_commits(limit=10)
    
    if commits:
        result = calculator.update_progress_from_commits(commits)
        
        updater = ReadmeUpdater()
        updater.update_progress_section(result['modules'], result['total'])
        updater.save_readme()
        
        print(f"✅ README已更新")
        print(f"   总体进度: {result['total']}%")
    else:
        print("未找到提交记录")
