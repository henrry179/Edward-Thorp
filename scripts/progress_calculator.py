"""
进度计算模块
根据Git提交和文件变更计算项目进度
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from git_analyzer import CommitInfo, GitAnalyzer


@dataclass
class ModuleProgress:
    """模块进度数据类"""
    name: str
    completed: int
    total: int
    percentage: float
    weight: float
    files_completed: List[str]
    files_pending: List[str]


class ProgressCalculator:
    """进度计算器"""
    
    def __init__(self, config_path: str = "config/progress_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.analyzer = GitAnalyzer()
        
    def _load_config(self) -> Dict:
        """加载进度配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """创建默认配置"""
        return {
            'modules': {
                'core': {'completed': 0, 'total': 5, 'weight': 0.35},
                'docs': {'completed': 0, 'total': 100, 'weight': 0.20},
                'examples': {'completed': 0, 'total': 100, 'weight': 0.20},
                'tests': {'completed': 0, 'total': 100, 'weight': 0.15},
                'config': {'completed': 0, 'total': 100, 'weight': 0.10}
            }
        }
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)
    
    def calculate_module_progress(self, module_key: str, commits: List[CommitInfo]) -> ModuleProgress:
        """
        计算单个模块的进度
        
        Args:
            module_key: 模块键名
            commits: Git提交列表
        """
        module_config = self.config.get('modules', {}).get(module_key, {})
        
        name = module_config.get('name', module_key)
        weight = module_config.get('weight', 0.2)
        target_files = module_config.get('target_files', [])
        notebook_files = module_config.get('notebooks', [])
        
        all_target_files = target_files + notebook_files
        
        # 计算当前进度
        current_completed = module_config.get('completed', 0)
        total = module_config.get('total', 100)
        
        # 分析提交对进度的影响
        progress_delta = 0
        files_completed = []
        files_pending = []
        
        for commit in commits:
            analysis = self.analyzer.analyze_commit_message(commit.message)
            
            # 检查是否影响当前模块
            if module_key in analysis.get('modules_affected', []):
                # 根据关键词调整进度
                if analysis['type'] == 'feature' or 'complete' in analysis['keywords']:
                    progress_delta += analysis.get('progress_delta', 5)
                elif analysis['type'] == 'fix':
                    progress_delta += 1
                elif analysis['type'] == 'docs':
                    progress_delta += 2
                elif analysis['type'] == 'test':
                    progress_delta += 3
            
            # 检查完成的文件
            for file in commit.files_changed:
                if any(target in file for target in all_target_files):
                    if file not in files_completed:
                        files_completed.append(file)
        
        # 计算文件完成度
        if all_target_files:
            file_completion_rate = len(files_completed) / len(all_target_files)
            file_based_progress = file_completion_rate * total
        else:
            file_based_progress = current_completed
        
        # 综合进度 = 当前进度 + 增量 + 文件完成度加权
        new_completed = min(current_completed + progress_delta, total)
        final_percentage = (new_completed / total) * 100 if total > 0 else 0
        
        # 确定待完成文件
        for target in all_target_files:
            if target not in files_completed:
                files_pending.append(target)
        
        return ModuleProgress(
            name=name,
            completed=int(new_completed),
            total=total,
            percentage=final_percentage,
            weight=weight,
            files_completed=files_completed,
            files_pending=files_pending
        )
    
    def calculate_all_progress(self, commits: List[CommitInfo]) -> Dict[str, ModuleProgress]:
        """计算所有模块的进度"""
        results = {}
        modules = self.config.get('modules', {})
        
        for module_key in modules.keys():
            progress = self.calculate_module_progress(module_key, commits)
            results[module_key] = progress
            
            # 更新配置
            self.config['modules'][module_key]['completed'] = progress.completed
        
        return results
    
    def calculate_total_progress(self, module_progress: Dict[str, ModuleProgress]) -> float:
        """计算总体进度（加权平均）"""
        total_weighted = 0
        total_weight = 0
        
        for module in module_progress.values():
            total_weighted += module.percentage * module.weight
            total_weight += module.weight
        
        return round(total_weighted / total_weight, 1) if total_weight > 0 else 0
    
    def update_progress_from_commits(self, commits: List[CommitInfo]) -> Dict:
        """
        根据提交更新进度
        
        Returns:
            包含各模块进度和总体进度的字典
        """
        # 计算各模块进度
        module_progress = self.calculate_all_progress(commits)
        
        # 计算总体进度
        total_progress = self.calculate_total_progress(module_progress)
        
        # 更新配置
        self.config['total_progress'] = total_progress
        self.config['last_updated'] = commits[0].date.strftime('%Y-%m-%d') if commits else ''
        
        # 保存配置
        self.save_config()
        
        return {
            'modules': module_progress,
            'total': total_progress,
            'last_updated': self.config['last_updated']
        }
    
    def get_progress_summary(self) -> str:
        """获取进度摘要文本"""
        modules = self.config.get('modules', {})
        total = self.config.get('total_progress', 0)
        
        lines = ["📊 项目进度概览", ""]
        lines.append(f"总体进度: {total}%")
        lines.append("")
        
        for key, module in modules.items():
            name = module.get('name', key)
            completed = module.get('completed', 0)
            total_items = module.get('total', 100)
            percentage = (completed / total_items * 100) if total_items > 0 else 0
            
            # 进度条
            bar_length = 20
            filled = int(bar_length * percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            lines.append(f"{name}: {bar} {percentage:.1f}%")
        
        return '\n'.join(lines)


if __name__ == "__main__":
    # 测试
    calculator = ProgressCalculator()
    
    # 模拟一些提交
    analyzer = GitAnalyzer()
    commits = analyzer.get_commits(limit=10)
    
    if commits:
        result = calculator.update_progress_from_commits(commits)
        
        print(f"\n总体进度: {result['total']}%")
        print(f"最后更新: {result['last_updated']}")
        print("\n各模块进度:")
        
        for key, module in result['modules'].items():
            print(f"  {module.name}: {module.percentage:.1f}% ({module.completed}/{module.total})")
    else:
        print("未找到提交记录")
