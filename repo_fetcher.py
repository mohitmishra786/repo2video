"""
GitHub Repository Fetcher Module

This module handles fetching repository contents from GitHub using the GitHub API,
analyzing repository structure, and extracting relevant information for video generation.
"""

import re
import ast
import markdown
from typing import Dict, List, Optional, Tuple, Union
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile
import requests
import logging
from urllib.parse import urlparse

# Set up logging
logger = logging.getLogger(__name__)


class RepoFetcher:
    """Handles fetching and analyzing repositories from GitHub, GitLab, and Bitbucket."""
    
    def __init__(self, github_token: Optional[str] = None, gitlab_token: Optional[str] = None, bitbucket_token: Optional[str] = None):
        """
        Initialize the RepoFetcher.
        
        Args:
            github_token: Optional GitHub token for authentication
            gitlab_token: Optional GitLab token for authentication
            bitbucket_token: Optional Bitbucket token for authentication
        """
        self.github = Github(github_token) if github_token else Github()
        self.gitlab_token = gitlab_token
        self.bitbucket_token = bitbucket_token
        self.rate_limit = self.github.get_rate_limit()
        
        # Initialize GitLab and Bitbucket clients only when needed
        self._gitlab_client = None
        self._bitbucket_client = None
    
    def validate_repo_url(self, url: str) -> Tuple[bool, str, str, str]:
        """
        Validate if the URL is a valid repository URL and identify the platform.
        
        Args:
            url: The repository URL
            
        Returns:
            Tuple of (is_valid, platform, owner, repo_name)
        """
        # GitHub pattern
        github_pattern = r'https://github\.com/([^/]+)/([^/]+)'
        gitlab_pattern = r'https://gitlab\.com/([^/]+)/([^/]+)'
        bitbucket_pattern = r'https://bitbucket\.org/([^/]+)/([^/]+)'
        
        for pattern, platform in [(github_pattern, 'github'), (gitlab_pattern, 'gitlab'), (bitbucket_pattern, 'bitbucket')]:
            match = re.match(pattern, url)
            if match:
                owner, repo_name = match.groups()
                # Remove .git suffix if present
                repo_name = repo_name.replace('.git', '')
                return True, platform, owner, repo_name
        
        return False, "", "", ""
    
    def fetch_repo(self, url: str) -> Optional[Union[Repository, dict]]:
        """
        Fetch repository information from GitHub, GitLab, or Bitbucket.
        
        Args:
            url: Repository URL
            
        Returns:
            Repository object (GitHub) or dict (GitLab/Bitbucket) or None if failed
        """
        is_valid, platform, owner, repo_name = self.validate_repo_url(url)
        
        if not is_valid:
            raise ValueError("Invalid repository URL")
        
        try:
            if platform == 'github':
                repo = self.github.get_repo(f"{owner}/{repo_name}")
                return repo
            elif platform == 'gitlab':
                if not self.gitlab_token:
                    raise ValueError("GitLab token not provided")
                # Lazy import and initialization
                import gitlab
                if not self._gitlab_client:
                    self._gitlab_client = gitlab.Gitlab('https://gitlab.com', private_token=self.gitlab_token)
                project = self._gitlab_client.projects.get(f"{owner}/{repo_name}")
                return {
                    'platform': 'gitlab',
                    'project': project,
                    'owner': owner,
                    'repo_name': repo_name
                }
            elif platform == 'bitbucket':
                if not self.bitbucket_token:
                    raise ValueError("Bitbucket token not provided")
                # Lazy import and initialization
                import bitbucket
                if not self._bitbucket_client:
                    self._bitbucket_client = bitbucket.Bitbucket(self.bitbucket_token)
                repo_data = self._bitbucket_client.repositories.get(f"{owner}/{repo_name}")
                return {
                    'platform': 'bitbucket',
                    'repo_data': repo_data,
                    'owner': owner,
                    'repo_name': repo_name
                }
            else:
                raise ValueError(f"Unsupported platform: {platform}")
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise ValueError("Repository not found or is private")
            elif "403" in str(e) or "rate limit" in str(e).lower():
                raise ValueError(f"Rate limit exceeded for {platform}. Please provide a token.")
            else:
                raise ValueError(f"Error fetching repository: {str(e)}")
    
    def get_repo_contents(self, repo: Union[Repository, dict], path: str = "") -> List[Dict]:
        """
        Recursively fetch repository contents from GitHub, GitLab, or Bitbucket.
        
        Args:
            repo: GitHub repository object or dict with platform info
            path: Path within the repository
            
        Returns:
            List of file information dictionaries
        """
        contents = []
        
        try:
            if isinstance(repo, Repository):
                # GitHub repository
                items = repo.get_contents(path)
                
                for item in items:
                    if item.type == "dir":
                        # Recursively get contents of subdirectories
                        sub_contents = self.get_repo_contents(repo, item.path)
                        contents.extend(sub_contents)
                    else:
                        # Only include code files and documentation
                        if self._is_relevant_file(item.name):
                            contents.append({
                                'name': item.name,
                                'path': item.path,
                                'type': item.type,
                                'size': item.size,
                                'content': item.decoded_content.decode('utf-8') if item.size < 1024 * 1024 else None
                            })
            elif isinstance(repo, dict):
                # GitLab or Bitbucket repository
                platform = repo.get('platform')
                
                if platform == 'gitlab':
                    project = repo.get('project')
                    # Use GitLab API to get repository tree
                    tree = project.repository_tree(recursive=True, path=path)
                    
                    for item in tree:
                        if item['type'] == 'blob':
                            if self._is_relevant_file(item['name']):
                                # Get file content
                                file_content = None
                                if item['size'] < 1024 * 1024:  # Only fetch small files
                                    file = project.files.get(file_path=item['path'], ref='master')
                                    file_content = file.decode()
                                
                                contents.append({
                                    'name': item['name'],
                                    'path': item['path'],
                                    'type': 'file',
                                    'size': item['size'],
                                    'content': file_content
                                })
                elif platform == 'bitbucket':
                    # Use Bitbucket API to get repository contents
                    repo_data = repo.get('repo_data')
                    owner = repo.get('owner')
                    repo_name = repo.get('repo_name')
                    
                    # Construct API URL for contents
                    api_url = f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo_name}/src/master/{path}"
                    
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'values' in data:  # Directory listing
                            for item in data['values']:
                                if item['type'] == 'commit_file':
                                    if self._is_relevant_file(item['path'].split('/')[-1]):
                                        # Get file content
                                        file_content = None
                                        if item.get('size', 0) < 1024 * 1024:
                                            file_url = f"https://api.bitbucket.org/2.0/repositories/{owner}/{repo_name}/src/master/{item['path']}"
                                            file_response = requests.get(file_url)
                                            if file_response.status_code == 200:
                                                file_content = file_response.text
                                        
                                        contents.append({
                                            'name': item['path'].split('/')[-1],
                                            'path': item['path'],
                                            'type': 'file',
                                            'size': item.get('size', 0),
                                            'content': file_content
                                        })
        except Exception as e:
            logger.warning(f"Error fetching repository contents: {e}")
        
        return contents
    
    def _is_relevant_file(self, filename: str) -> bool:
        """
        Check if a file is relevant for analysis.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file should be included in analysis
        """
        relevant_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.md', '.txt', '.rst', '.yml', '.yaml', '.json', '.xml',
            '.html', '.css', '.scss', '.sass', '.rb', '.go', '.rs',
            '.php', '.swift', '.kt', '.scala', '.r', '.m', '.sh'
        }
        
        return any(filename.endswith(ext) for ext in relevant_extensions) or filename in ['README', 'LICENSE']
    
    def analyze_repo(self, repo: Repository) -> Dict:
        """
        Analyze repository structure and content.
        
        Args:
            repo: GitHub repository object
            
        Returns:
            Dictionary containing analysis results
        """
        # Get repository metadata
        analysis = {
            'name': repo.name,
            'owner': repo.owner.login,
            'description': repo.description or '',
            'language': repo.language,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'files': [],
            'readme': None,
            'main_files': [],
            'structure': {}
        }
        
        # Fetch repository contents
        contents = self.get_repo_contents(repo)
        analysis['files'] = contents
        
        # Find README
        for file_info in contents:
            if file_info['name'].lower() in ['readme.md', 'readme.txt', 'readme.rst']:
                analysis['readme'] = file_info
                break
        
        # Identify main code files (limit to top 10)
        code_files = [f for f in contents if f['content'] and self._is_code_file(f['name'])]
        analysis['main_files'] = code_files[:10]
        
        # Analyze repository structure
        analysis['structure'] = self._analyze_structure(contents)
        
        return analysis
    
    def _is_code_file(self, filename: str) -> bool:
        """
        Check if a file is a code file.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file is a code file
        """
        code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.scala',
            '.r', '.m', '.sh', '.pl', '.lua', '.dart'
        }
        
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def _analyze_structure(self, contents: List[Dict]) -> Dict:
        """
        Analyze the structure of repository contents.
        
        Args:
            contents: List of file information dictionaries
            
        Returns:
            Dictionary containing structure analysis
        """
        structure = {
            'total_files': len(contents),
            'code_files': 0,
            'doc_files': 0,
            'config_files': 0,
            'languages': {},
            'directories': set()
        }
        
        for file_info in contents:
            filename = file_info['name']
            path = file_info['path']
            
            # Count file types
            if self._is_code_file(filename):
                structure['code_files'] += 1
                ext = '.' + filename.split('.')[-1] if '.' in filename else 'unknown'
                structure['languages'][ext] = structure['languages'].get(ext, 0) + 1
            elif filename.endswith(('.md', '.txt', '.rst')):
                structure['doc_files'] += 1
            elif filename.endswith(('.yml', '.yaml', '.json', '.xml', '.toml')):
                structure['config_files'] += 1
            
            # Track directories
            if '/' in path:
                dir_path = '/'.join(path.split('/')[:-1])
                structure['directories'].add(dir_path)
        
        structure['directories'] = list(structure['directories'])
        return structure
    
    def parse_readme(self, readme_content: str) -> Dict:
        """
        Parse README content to extract tutorial-like sections.
        
        Args:
            readme_content: Content of the README file
            
        Returns:
            Dictionary containing parsed README sections
        """
        # Convert markdown to HTML for easier parsing
        html = markdown.markdown(readme_content)
        
        # Extract sections (this is a simplified approach)
        sections = {
            'title': '',
            'description': '',
            'installation': '',
            'usage': '',
            'examples': '',
            'code_blocks': []
        }
        
        # Extract code blocks
        code_block_pattern = r'```[\w]*\n(.*?)\n```'
        code_blocks = re.findall(code_block_pattern, readme_content, re.DOTALL)
        sections['code_blocks'] = code_blocks
        
        # Extract title (first heading)
        title_pattern = r'^#\s+(.+)$'
        title_match = re.search(title_pattern, readme_content, re.MULTILINE)
        if title_match:
            sections['title'] = title_match.group(1)
        
        # Extract description (text after title, before first section)
        lines = readme_content.split('\n')
        description_lines = []
        in_description = False
        
        for line in lines:
            if line.startswith('#') and not in_description:
                in_description = True
                continue
            elif line.startswith('#') and in_description:
                break
            elif in_description and line.strip():
                description_lines.append(line)
        
        sections['description'] = '\n'.join(description_lines)
        
        return sections
    
    def analyze_python_code(self, code_content: str) -> Dict:
        """
        Analyze Python code using AST.
        
        Args:
            code_content: Python code content
            
        Returns:
            Dictionary containing code analysis
        """
        try:
            tree = ast.parse(code_content)
            analysis = {
                'imports': [],
                'functions': [],
                'classes': [],
                'variables': [],
                'errors': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        analysis['imports'].append(f"{module}.{alias.name}")
                elif isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'lineno': node.lineno
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'lineno': node.lineno
                    })
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            analysis['variables'].append(target.id)
            
            return analysis
        except SyntaxError as e:
            return {
                'imports': [],
                'functions': [],
                'classes': [],
                'variables': [],
                'errors': [f"Syntax error at line {e.lineno}: {e.text}"]
            }
    
    def get_rate_limit_info(self) -> Dict:
        """
        Get current GitHub API rate limit information.
        
        Returns:
            Dictionary containing rate limit info
        """
        return {
            'limit': self.rate_limit.rate.limit,
            'remaining': self.rate_limit.rate.remaining,
            'reset_time': self.rate_limit.rate.reset
        } 