#!/usr/bin/env python3
"""
开发进度更新主脚本

自动从Git提交历史提取进度信息，更新进度时间表和README展示

使用方法:
    python scripts/update_progress.py [选项]

选项:
    --message, -m    自定义进度更新消息
    --progress, -p   手动指定进度百分比
    --no-push        不自动推送到GitHub
    --dry-run        试运行，不保存任何更改
    --verbose, -v    显示详细输出

示例:
    # 自动更新进度
    python scripts/update_progress.py
    
    # 手动指定进度并添加消息
    python scripts/update_progress.py -m "完成Notebook 02-05" -p 85
    
    # 本地测试，不推送
    python scripts/update_progress.py --no-push --dry-run
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from git_analyzer import GitAnalyzer
from progress_calculator import ProgressCalculator
from readme_updater import ReadmeUpdater
from timeline_generator import TimelineGenerator


class ProgressUpdater:
    """进度更新器主类"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.analyzer = GitAnalyzer()
        self.calculator = ProgressCalculator()
        self.readme_updater = ReadmeUpdater()
        self.timeline_generator = TimelineGenerator()
        
    def log(self, message: str):
        """输出日志"""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def run(self, message: str = None, progress: int = None, 
            no_push: bool = False, dry_run: bool = False) -> bool:
        """
        执行进度更新流程
        
        Returns:
            bool: 是否成功
        """
        print("🚀 开始更新开发进度...")
        print("")
        
        # 1. 获取Git提交历史
        print("📊 步骤 1/5: 分析Git提交历史...")
        last_updated = self.calculator.config.get('last_updated', '')
        
        if last_updated:
            commits = self.analyzer.get_last_update_commit(last_updated)
            self.log(f"获取上次更新({last_updated})后的 {len(commits)} 个提交")
        else:
            commits = self.analyzer.get_commits(limit=50)
            self.log(f"获取最近的 {len(commits)} 个提交")
        
        if not commits:
            print("⚠️  未找到新的提交记录")
            return False
        
        print(f"   ✅ 找到 {len(commits)} 个提交")
        
        # 2. 计算进度
        print("\n📈 步骤 2/5: 计算项目进度...")
        
        if progress is not None:
            # 使用手动指定的进度
            result = {
                'modules': self.calculator.calculate_all_progress(commits),
                'total': progress,
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            self.calculator.config['total_progress'] = progress
        else:
            # 自动计算进度
            result = self.calculator.update_progress_from_commits(commits)
        
        print(f"   ✅ 总体进度: {result['total']}%")
        
        for key, module in result['modules'].items():
            status = "✅" if module.percentage >= 90 else "🔄" if module.percentage >= 50 else "📋"
            print(f"      {module.name}: {module.percentage:.1f}% {status}")
        
        # 3. 生成时间表
        print("\n📅 步骤 3/5: 生成进度时间表...")
        
        if not dry_run:
            self.timeline_generator.update_timeline(
                commits, result['modules'], result['total']
            )
            print(f"   ✅ 时间表已更新: docs/PROGRESS_TIMELINE.md")
        else:
            print("   [试运行] 时间表未保存")
        
        # 4. 更新README
        print("\n📝 步骤 4/5: 更新README进度展示...")
        
        if not dry_run:
            self.readme_updater.update_progress_section(
                result['modules'], result['total']
            )
            self.readme_updater.save_readme()
            print(f"   ✅ README已更新")
        else:
            print("   [试运行] README未保存")
        
        # 5. Git提交和推送
        print("\n🔄 步骤 5/5: Git提交和推送...")
        
        if dry_run:
            print("   [试运行] 跳过Git操作")
        elif no_push:
            print("   ⏭️  跳过推送 (--no-push)")
            # 只提交，不推送
            self._git_commit(message, result['total'])
        else:
            # 提交并推送
            if self._git_commit(message, result['total']):
                if self._git_push():
                    print("   ✅ 已推送到GitHub")
                else:
                    print("   ⚠️  推送失败")
                    return False
        
        print("")
        print("=" * 50)
        print("✨ 开发进度更新完成!")
        print(f"   总体进度: {result['total']}%")
        print(f"   更新时间: {result['last_updated']}")
        print("=" * 50)
        
        return True
    
    def _git_commit(self, message: str = None, progress: float = None) -> bool:
        """执行Git提交"""
        try:
            # 检查是否有变更
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                print("   ℹ️  没有需要提交的变更")
                return True
            
            # 添加文件
            subprocess.run(["git", "add", "README.md"], check=True)
            subprocess.run(["git", "add", "docs/PROGRESS_TIMELINE.md"], check=True)
            subprocess.run(["git", "add", "config/progress_config.yaml"], check=True)
            
            # 构建提交信息
            if message:
                commit_msg = f"{message}\n\n进度更新: {progress}%"
            else:
                commit_msg = f"docs: 自动更新开发进度 - {datetime.now().strftime('%Y-%m-%d')}\n\n进度更新: {progress}%"
            
            # 提交
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=True,
                capture_output=True
            )
            
            print("   ✅ 已创建Git提交")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Git提交失败: {e}")
            return False
    
    def _git_push(self) -> bool:
        """执行Git推送"""
        try:
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"   ❌ Git推送失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="自动更新开发进度并推送到GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/update_progress.py
  python scripts/update_progress.py -m "完成Notebook 02-05" -p 85
  python scripts/update_progress.py --no-push --dry-run
        """
    )
    
    parser.add_argument(
        '-m', '--message',
        help='自定义进度更新消息'
    )
    parser.add_argument(
        '-p', '--progress',
        type=int,
        help='手动指定进度百分比 (0-100)'
    )
    parser.add_argument(
        '--no-push',
        action='store_true',
        help='不自动推送到GitHub'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行，不保存任何更改'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细输出'
    )
    
    args = parser.parse_args()
    
    # 创建更新器并运行
    updater = ProgressUpdater(verbose=args.verbose)
    success = updater.run(
        message=args.message,
        progress=args.progress,
        no_push=args.no_push,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
