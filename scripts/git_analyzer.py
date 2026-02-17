"""
Git提交分析模块
从Git提交历史中提取变更信息
"""

import subprocess
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CommitInfo:
    """提交信息数据类"""
    hash: str
    short_hash: str
    date: datetime
    author: str
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int
    

class GitAnalyzer:
    """Git提交分析器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        
    def _run_git_command(self, args: List[str]) -> str:
        """执行Git命令"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode != 0:
                print(f"Git命令错误: {result.stderr}")
                return ""
            return result.stdout
        except Exception as e:
            print(f"执行Git命令失败: {e}")
            return ""
    
    def get_commits(self, since: Optional[str] = None, limit: int = 100) -> List[CommitInfo]:
        """
        获取提交历史
        
        Args:
            since: 起始日期 (格式: YYYY-MM-DD)
            limit: 最大返回数量
        """
        format_str = '%H|%h|%ai|%an|%s'
        args = ["log", f"--pretty=format:{format_str}", "--numstat"]
        
        if since:
            args.extend(["--since", since])
        
        args.append(f"-{limit}")
        
        output = self._run_git_command(args)
        return self._parse_log(output)
    
    def _parse_log(self, log_output: str) -> List[CommitInfo]:
        """解析Git日志输出"""
        commits = []
        current_commit = None
        files = []
        insertions = 0
        deletions = 0
        
        for line in log_output.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # 提交信息行 (hash|short_hash|date|author|message)
            if '|' in line and not line[0].isdigit() and not line.startswith('-'):
                # 保存上一个提交
                if current_commit:
                    commits.append(CommitInfo(
                        hash=current_commit['hash'],
                        short_hash=current_commit['short_hash'],
                        date=current_commit['date'],
                        author=current_commit['author'],
                        message=current_commit['message'],
                        files_changed=files,
                        insertions=insertions,
                        deletions=deletions
                    ))
                
                parts = line.split('|', 4)
                if len(parts) >= 5:
                    current_commit = {
                        'hash': parts[0],
                        'short_hash': parts[1],
                        'date': datetime.strptime(parts[2], '%Y-%m-%d %H:%M:%S %z'),
                        'author': parts[3],
                        'message': parts[4]
                    }
                    files = []
                    insertions = 0
                    deletions = 0
                    
            # 文件统计行 (insertions\tdeletions\tfilepath)
            elif '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        ins = int(parts[0]) if parts[0] != '-' else 0
                        dels = int(parts[1]) if parts[1] != '-' else 0
                        insertions += ins
                        deletions += dels
                        files.append(parts[2])
                    except ValueError:
                        pass
        
        # 添加最后一个提交
        if current_commit:
            commits.append(CommitInfo(
                hash=current_commit['hash'],
                short_hash=current_commit['short_hash'],
                date=current_commit['date'],
                author=current_commit['author'],
                message=current_commit['message'],
                files_changed=files,
                insertions=insertions,
                deletions=deletions
            ))
        
        return commits
    
    def get_commits_by_date_range(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[CommitInfo]:
        """获取指定日期范围内的提交"""
        since = start_date.strftime('%Y-%m-%d')
        until = end_date.strftime('%Y-%m-%d') if end_date else None
        
        args = ["log", f"--since={since}"]
        if until:
            args.append(f"--until={until}")
        args.extend(["--pretty=format:%H|%h|%ai|%an|%s", "--numstat"])
        
        output = self._run_git_command(args)
        return self._parse_log(output)
    
    def get_last_update_commit(self, last_updated: str) -> List[CommitInfo]:
        """获取上次更新后的所有新提交"""
        # 解析日期
        try:
            date_obj = datetime.strptime(last_updated, '%Y-%m-%d')
            return self.get_commits_by_date_range(date_obj)
        except ValueError:
            return self.get_commits(limit=20)
    
    def analyze_commit_message(self, message: str) -> Dict[str, any]:
        """分析提交信息，提取关键词和进度信息"""
        result = {
            'type': 'other',
            'keywords': [],
            'progress_delta': 0,
            'modules_affected': []
        }
        
        # 关键词映射
        keyword_map = {
            'complete': ['完成', '✅', 'done', 'completed', 'finished'],
            'in_progress': ['进行中', '🔄', 'in progress', 'ongoing'],
            'planned': ['计划中', '📋', 'todo', 'planned'],
            'fix': ['修复', '🐛', 'fix', 'bugfix'],
            'feature': ['新增', '✨', 'feat', 'feature', 'add'],
            'docs': ['文档', '📝', 'docs', 'documentation'],
            'test': ['测试', '🧪', 'test', 'testing'],
            'refactor': ['重构', '♻️', 'refactor']
        }
        
        message_lower = message.lower()
        
        # 识别关键词
        for cat, keywords in keyword_map.items():
            for kw in keywords:
                if kw.lower() in message_lower:
                    result['keywords'].append(kw)
                    if cat in ['complete', 'feature']:
                        result['type'] = 'feature'
                    elif cat == 'fix':
                        result['type'] = 'fix'
                    elif cat == 'docs':
                        result['type'] = 'docs'
                    elif cat == 'test':
                        result['type'] = 'test'
                    break
        
        # 提取进度变化
        progress_pattern = r'(\d+)%|进度[:\s]*(\d+)|完成度[:\s]*(\d+)'
        matches = re.findall(progress_pattern, message)
        if matches:
            for match in matches:
                num = int(match[0] or match[1] or match[2])
                if 0 <= num <= 100:
                    result['progress_delta'] = num
                    break
        
        # 识别受影响的模块
        module_keywords = {
            'core': ['核心', '定价', '对冲', '信号', '回测', 'pricing', 'hedging', 'signal', 'backtest'],
            'docs': ['文档', 'readme', 'documentation', 'docs'],
            'examples': ['示例', 'notebook', 'example', '教学'],
            'tests': ['测试', 'test', 'tests', 'pytest'],
            'config': ['配置', 'setup', 'config']
        }
        
        for module, keywords in module_keywords.items():
            for kw in keywords:
                if kw.lower() in message_lower:
                    result['modules_affected'].append(module)
                    break
        
        return result
    
    def get_file_changes_summary(self, commits: List[CommitInfo]) -> Dict[str, List[str]]:
        """汇总文件变更"""
        summary = {
            'created': [],
            'modified': [],
            'deleted': []
        }
        
        all_files = set()
        for commit in commits:
            all_files.update(commit.files_changed)
        
        # 检查文件当前状态
        for filepath in all_files:
            if self._file_exists_in_head(filepath):
                # 文件在最新commit中存在，检查是否是新文件
                if self._is_new_file(filepath, commits):
                    summary['created'].append(filepath)
                else:
                    summary['modified'].append(filepath)
            else:
                summary['deleted'].append(filepath)
        
        return summary
    
    def _file_exists_in_head(self, filepath: str) -> bool:
        """检查文件是否在当前HEAD中存在"""
        result = self._run_git_command(["ls-tree", "-r", "HEAD", "--name-only"])
        return filepath in result.split('\n')
    
    def _is_new_file(self, filepath: str, commits: List[CommitInfo]) -> bool:
        """判断文件是否是本次新增"""
        # 简化处理：如果在commit历史中只出现过一次，视为新增
        count = sum(1 for c in commits if filepath in c.files_changed)
        return count == 1
    
    def get_current_branch(self) -> str:
        """获取当前分支"""
        output = self._run_git_command(["branch", "--show-current"])
        return output.strip()
    
    def get_remote_url(self) -> str:
        """获取远程仓库URL"""
        output = self._run_git_command(["remote", "get-url", "origin"])
        return output.strip()


if __name__ == "__main__":
    # 测试
    analyzer = GitAnalyzer()
    commits = analyzer.get_commits(limit=5)
    
    print(f"获取到 {len(commits)} 个提交:")
    for commit in commits:
        print(f"\n{commit.short_hash} - {commit.date.strftime('%Y-%m-%d')}")
        print(f"  作者: {commit.author}")
        print(f"  信息: {commit.message}")
        print(f"  文件: {len(commit.files_changed)} 个")
        print(f"  变更: +{commit.insertions}/-{commit.deletions}")
        
        analysis = analyzer.analyze_commit_message(commit.message)
        print(f"  分析: 类型={analysis['type']}, 进度={analysis['progress_delta']}%")
