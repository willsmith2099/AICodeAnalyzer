import git
from datetime import datetime

class GitAnalyzer:
    def __init__(self, repo_path):
        """
        Initialize Git Analyzer
        
        Args:
            repo_path: Path to the git repository
        """
        try:
            self.repo = git.Repo(repo_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Not a valid git repository: {repo_path}")
    
    def get_recent_changes(self, file_path=None, max_commits=5):
        """
        Get recent changes for a file or the entire repository
        
        Args:
            file_path: Optional specific file path to analyze
            max_commits: Maximum number of commits to retrieve
            
        Returns:
            List of commit information dictionaries
        """
        commits = []
        
        try:
            if file_path:
                # Get commits for specific file
                commit_iter = self.repo.iter_commits(paths=file_path, max_count=max_commits)
            else:
                # Get recent commits for entire repo
                commit_iter = self.repo.iter_commits(max_count=max_commits)
            
            for commit in commit_iter:
                commit_info = {
                    'hash': commit.hexsha[:8],
                    'author': str(commit.author),
                    'date': datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S'),
                    'message': commit.message.strip(),
                    'changes': []
                }
                
                # Get diff for this commit
                if commit.parents:
                    diffs = commit.parents[0].diff(commit)
                    for diff in diffs:
                        if file_path is None or diff.a_path == file_path or diff.b_path == file_path:
                            change_info = {
                                'file': diff.b_path or diff.a_path,
                                'change_type': diff.change_type,
                                'additions': 0,
                                'deletions': 0
                            }
                            
                            # Try to get diff stats
                            try:
                                if diff.diff:
                                    diff_text = diff.diff.decode('utf-8', errors='ignore')
                                    change_info['additions'] = diff_text.count('\n+')
                                    change_info['deletions'] = diff_text.count('\n-')
                            except:
                                pass
                            
                            commit_info['changes'].append(change_info)
                
                commits.append(commit_info)
        
        except Exception as e:
            print(f"Error getting git history: {e}")
        
        return commits
    
    def get_file_diff(self, file_path, commit_hash=None):
        """
        Get the diff for a specific file
        
        Args:
            file_path: Path to the file
            commit_hash: Optional commit hash to compare against (default: HEAD vs working tree)
            
        Returns:
            Diff text
        """
        try:
            if commit_hash:
                commit = self.repo.commit(commit_hash)
                if commit.parents:
                    diffs = commit.parents[0].diff(commit, paths=file_path, create_patch=True)
                else:
                    return "Initial commit - no diff available"
            else:
                # Compare HEAD with working tree
                diffs = self.repo.head.commit.diff(None, paths=file_path, create_patch=True)
            
            if diffs:
                diff_text = diffs[0].diff.decode('utf-8', errors='ignore')
                return diff_text
            else:
                return "No changes found"
        
        except Exception as e:
            return f"Error getting diff: {e}"
    
    def get_changed_files(self, since_commit=None):
        """
        Get list of changed files since a specific commit
        
        Args:
            since_commit: Commit hash to compare from (default: last commit)
            
        Returns:
            List of changed file paths
        """
        try:
            if since_commit:
                commit = self.repo.commit(since_commit)
            else:
                # Get last commit
                commit = self.repo.head.commit
            
            if commit.parents:
                diffs = commit.parents[0].diff(commit)
                return [diff.b_path or diff.a_path for diff in diffs]
            else:
                return []
        
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return []
