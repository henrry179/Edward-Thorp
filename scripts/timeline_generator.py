"""
时间表生成模块
生成按时间排序的开发进度时间表
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from git_analyzer import CommitInfo, GitAnalyzer
from progress_calculator import ProgressCalculator, ModuleProgress


class TimelineGenerator:
    """时间表生成器"""
    
    def __init__(self, config_path: str = "config/progress_config.yaml", 
                 timeline_path: str = "docs/PROGRESS_TIMELINE.md"):
        self.config_path = Path(config_path)
        self.timeline_path = Path(timeline_path)
        self.config = self._load_config()
        self.analyzer = GitAnalyzer()
        
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def generate_timeline(self, commits: List[CommitInfo], 
                         module_progress: Dict[str, ModuleProgress],
                         total_progress: float) -> str:
        """
        生成时间表Markdown内容
        
        Args:
            commits: Git提交列表
            module_progress: 各模块进度
            total_progress: 总体进度
        """
        lines = []
        
        # 标题
        lines.extend([
            "# 📅 开发进度时间表",
            "",
            "> 本文档由系统自动生成，记录项目的开发进度历史",
            "",
            "## 📊 当前进度概览",
            "",
            f"**总体完成度：{total_progress}%**",
            "",
            "| 模块 | 完成度 | 状态 |",
            "|------|--------|------|"
        ])
        
        # 模块进度表
        for key, module in module_progress.items():
            status = "✅ 已完成" if module.percentage >= 90 else "🔄 进行中" if module.percentage >= 50 else "📋 计划中"
            lines.append(f"| {module.name} | {module.percentage:.0f}% | {status} |")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 时间线
        lines.extend([
            "## 🕐 开发时间线",
            "",
            "### 按日期排序的进度更新",
            ""
        ])
        
        # 按日期分组提交
        commits_by_date = self._group_commits_by_date(commits)
        
        for date_str, day_commits in sorted(commits_by_date.items(), reverse=True):
            lines.extend(self._generate_day_entry(date_str, day_commits, module_progress))
        
        # 如果没有提交，显示提示
        if not commits_by_date:
            lines.extend([
                "> ⚠️ 暂无提交记录",
                "",
                "系统将自动从Git提交历史中提取进度更新。",
                ""
            ])
        
        # 页脚
        lines.extend([
            "---",
            "",
            f"*最后生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "*本文档由 `scripts/update_progress.py` 自动生成*"
        ])
        
        return '\n'.join(lines)
    
    def _group_commits_by_date(self, commits: List[CommitInfo]) -> Dict[str, List[CommitInfo]]:
        """按日期分组提交"""
        grouped = {}
        for commit in commits:
            date_str = commit.date.strftime('%Y-%m-%d')
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(commit)
        return grouped
    
    def _generate_day_entry(self, date_str: str, commits: List[CommitInfo],
                           module_progress: Dict[str, ModuleProgress]) -> List[str]:
        """生成单日时间线条目"""
        lines = []
        
        # 日期标题
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
        lines.append(f"#### 📌 {date_str} ({weekday})")
        lines.append("")
        
        # 汇总信息
        total_commits = len(commits)
        total_files = sum(len(c.files_changed) for c in commits)
        total_insertions = sum(c.insertions for c in commits)
        total_deletions = sum(c.deletions for c in commits)
        
        lines.append(f"**提交数量**: {total_commits} | **文件变更**: {total_files} | **代码变更**: +{total_insertions}/-{total_deletions}")
        lines.append("")
        
        # 详细提交列表
        lines.append("<details>")
        lines.append("<summary>查看详细提交</summary>")
        lines.append("")
        
        for commit in commits:
            # 分析提交
            analysis = self.analyzer.analyze_commit_message(commit.message)
            
            # 提交标题
            icon = self._get_commit_icon(analysis['type'])
            lines.append(f"- {icon} **{commit.short_hash}** - {commit.message}")
            
            # 影响的模块
            if analysis['modules_affected']:
                module_names = [module_progress.get(m, ModuleProgress(m, 0, 0, 0, 0, [], [])).name 
                               for m in analysis['modules_affected']]
                lines.append(f"  - 📦 模块: {', '.join(module_names)}")
            
            # 文件变更
            if commit.files_changed:
                files_str = ', '.commit.files_changed[:5]  # 最多显示5个
                if len(commit.files_changed) > 5:
                    files_str += f" 等{len(commit.files_changed)}个文件"
                lines.append(f"  - 📝 文件: {files_str}")
            
            lines.append("")
        
        lines.append("</details>")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return lines
    
    def _get_commit_icon(self, commit_type: str) -> str:
        """获取提交类型图标"""
        icons = {
            'feature': '✨',
            'fix': '🐛',
            'docs': '📝',
            'test': '🧪',
            'refactor': '♻️',
            'other': '🔹'
        }
        return icons.get(commit_type, '🔹')
    
    def save_timeline(self, content: str):
        """保存时间表到文件"""
        # 确保目录存在
        self.timeline_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.timeline_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def update_timeline(self, commits: List[CommitInfo],
                       module_progress: Dict[str, ModuleProgress],
                       total_progress: float):
        """
        更新时间表文档
        """
        content = self.generate_timeline(commits, module_progress, total_progress)
        self.save_timeline(content)
    
    def append_to_timeline(self, new_commits: List[CommitInfo]):
        """
        向现有时间表追加新条目
        """
        if not self.timeline_path.exists():
            # 生成新的时间表
            calculator = ProgressCalculator()
            result = calculator.update_progress_from_commits(new_commits)
            self.update_timeline(new_commits, result['modules'], result['total'])
            return
        
        # 读取现有内容
        with open(self.timeline_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # 在"开发时间线"章节后插入新条目
        commits_by_date = self._group_commits_by_date(new_commits)
        
        if commits_by_date:
            # 获取模块进度信息
            calculator = ProgressCalculator()
            result = calculator.update_progress_from_commits(new_commits)
            
            new_entries = []
            for date_str in sorted(commits_by_date.keys(), reverse=True):
                day_commits = commits_by_date[date_str]
                new_entries.extend(self._generate_day_entry(
                    date_str, day_commits, result['modules']
                ))
            
            # 找到插入位置（在"### 按日期排序的进度更新"之后）
            insert_marker = "### 按日期排序的进度更新\n"
            insert_pos = existing_content.find(insert_marker)
            
            if insert_pos > 0:
                insert_pos += len(insert_marker)
                new_content = (
                    existing_content[:insert_pos] + 
                    "\n" + '\n'.join(new_entries) +
                    existing_content[insert_pos:]
                )
                
                # 更新最后生成时间
                time_pattern = r'\*最后生成时间：[^*]+\*'
                new_time = f"*最后生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
                new_content = __import__('re').sub(time_pattern, new_time, new_content)
                
                self.save_timeline(new_content)


if __name__ == "__main__":
    # 测试
    from progress_calculator import ProgressCalculator
    
    calculator = ProgressCalculator()
    analyzer = GitAnalyzer()
    
    commits = analyzer.get_commits(limit=10)
    
    if commits:
        result = calculator.update_progress_from_commits(commits)
        
        generator = TimelineGenerator()
        generator.update_timeline(commits, result['modules'], result['total'])
        
        print(f"✅ 时间表已生成: {generator.timeline_path}")
        print(f"   总体进度: {result['total']}%")
    else:
        print("未找到提交记录")
