import requests
import json
import os
import zipfile
import shutil
import tempfile
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from packaging import version
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('sGVC')

class sgvc:
    """
    Simple GitHub Version Control library
    Developer: Kozosvyst Stas
    """
    
    def __init__(self, git_username: str, git_reponame: str, token: Optional[str] = None):
        """
        Initialize sGVC with GitHub repository information
        
        Args:
            git_username: GitHub username
            git_reponame: GitHub repository name
            token: GitHub personal access token for private repos
        """
        self.git_username = git_username
        self.git_reponame = git_reponame
        self.token = token
        self.github_api_url = f"https://api.github.com/repos/{git_username}/{git_reponame}/releases/latest"
        self.history_file = "version_history.json"
        self.repositories = []
        
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        
        logger.info(f"Initialized sGVC for {git_username}/{git_reponame}")
    
    def _validate_version(self, version_str: str) -> bool:
        """
        Validate version string format
        
        Args:
            version_str: Version string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not version_str or not isinstance(version_str, str):
            return False
        
        if not version_str.strip():
            return False
        
        version_pattern = r'^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9\-\.]+)?(\+[a-zA-Z0-9\-\.]+)?$'
        return bool(re.match(version_pattern, version_str.strip()))
    
    def _parse_version_difference(self, local_ver: str, latest_ver: str) -> Dict[str, Any]:
        """
        Calculate version difference using semantic versioning
        
        Args:
            local_ver: Local version string
            latest_ver: Latest version string
            
        Returns:
            Dict with comparison details
        """
        try:
            if not self._validate_version(local_ver):
                logger.warning(f"Invalid local version format: {local_ver}")
                return {"status": "unknown", "difference": "Invalid local version format", "behind": 0}
            
            if not self._validate_version(latest_ver):
                logger.warning(f"Invalid latest version format: {latest_ver}")
                return {"status": "unknown", "difference": "Invalid latest version format", "behind": 0}
            
            local_v = version.parse(local_ver)
            latest_v = version.parse(latest_ver)
            
            if local_v == latest_v:
                return {"status": "active", "difference": "none", "behind": 0}
            elif local_v > latest_v:
                return {"status": "ahead", "difference": "ahead", "behind": 0}
            else:
                local_parts = str(local_v).split('.')
                latest_parts = str(latest_v).split('.')
                
                max_len = max(len(local_parts), len(latest_parts))
                local_parts += ['0'] * (max_len - len(local_parts))
                latest_parts += ['0'] * (max_len - len(latest_parts))
                
                major_diff = int(latest_parts[0]) - int(local_parts[0])
                minor_diff = int(latest_parts[1]) - int(local_parts[1]) if len(latest_parts) > 1 else 0
                patch_diff = int(latest_parts[2]) - int(local_parts[2]) if len(latest_parts) > 2 else 0
                
                if major_diff > 0:
                    return {"status": "old", "difference": f"{major_diff} major version(s) behind", "behind": major_diff}
                elif minor_diff > 0:
                    return {"status": "old", "difference": f"{minor_diff} minor version(s) behind", "behind": minor_diff}
                else:
                    return {"status": "old", "difference": f"{patch_diff} patch(es) behind", "behind": patch_diff}
                    
        except Exception as e:
            logger.error(f"Error parsing version difference: {str(e)}")
            return {"status": "unknown", "difference": f"Version parsing error: {str(e)}", "behind": 0}
    
    def check(self, local_version: str) -> Dict[str, Any]:
        """
        Check version status against GitHub releases with semantic versioning
        
        Args:
            local_version: Current local version
            
        Returns:
            Dict with detailed version comparison
        """
        logger.info(f"Checking version for {self.git_username}/{self.git_reponame}, local: {local_version}")
        
        try:
            response = requests.get(self.github_api_url, headers=self.headers)
            
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').lstrip('v')
                
                if not latest_version:
                    logger.warning(f"No tag_name found in release data for {self.git_username}/{self.git_reponame}")
                    latest_version = "unknown"
            elif response.status_code == 404:
                logger.warning(f"Repository not found or no releases: {self.git_username}/{self.git_reponame}")
                latest_version = "no_releases"
            else:
                logger.error(f"GitHub API error {response.status_code}: {response.text}")
                latest_version = "unknown"
            
            version_diff = self._parse_version_difference(local_version, latest_version)
            
            result = {
                "last": latest_version,
                "local": local_version,
                "status": version_diff["status"],
                "difference": version_diff["difference"],
                "behind_by": version_diff["behind"]
            }
            
            self._save_to_history(result)
            
            logger.info(f"Version check completed: {result['status']}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Network error during version check: {str(e)}")
            return {
                "last": "unknown",
                "local": local_version,
                "status": "error",
                "difference": f"Network error: {str(e)}",
                "behind_by": 0
            }
        except Exception as e:
            logger.error(f"Unexpected error during version check: {str(e)}")
            return {
                "last": "unknown",
                "local": local_version,
                "status": "error",
                "difference": f"Unexpected error: {str(e)}",
                "behind_by": 0
            }
    
    def update(self, interactive: bool = True, extract_path: str = ".", check_current: bool = True) -> Dict[str, Any]:
        """
        Automatically update to the latest version from GitHub
        
        Args:
            interactive: Whether to ask for confirmation
            extract_path: Path to extract the update
            check_current: Whether to check if already up to date
            
        Returns:
            Dict with update status
        """
        logger.info(f"Starting update process for {self.git_username}/{self.git_reponame}")
        
        try:
            response = requests.get(self.github_api_url, headers=self.headers)
            
            if response.status_code != 200:
                error_msg = f"Failed to fetch release information: HTTP {response.status_code}"
                logger.error(error_msg)
                return {"success": False, "message": error_msg}
            
            release_data = response.json()
            download_url = release_data.get('zipball_url')
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            if not download_url:
                error_msg = "No download URL found in release data"
                logger.error(error_msg)
                return {"success": False, "message": error_msg}
            
            if not latest_version:
                error_msg = "No version tag found in release data"
                logger.error(error_msg)
                return {"success": False, "message": error_msg}
            
            if check_current and os.path.exists("v.json"):
                try:
                    with open("v.json", 'r', encoding='utf-8') as f:
                        current_data = json.load(f)
                        current_version = current_data.get('version', '')
                        
                    if current_version and self._validate_version(current_version):
                        version_diff = self._parse_version_difference(current_version, latest_version)
                        if version_diff["status"] == "active":
                            logger.info(f"Already up to date (v{current_version})")
                            return {"success": True, "message": f"Already up to date (v{current_version})"}
                except Exception as e:
                    logger.warning(f"Could not read current version from v.json: {str(e)}")
            
            if interactive:
                confirm = input(f"Update to version {latest_version}? (y/N): ").lower().strip()
                if confirm != 'y':
                    logger.info("Update cancelled by user")
                    return {"success": False, "message": "Update cancelled by user"}
            
            logger.info(f"Downloading version {latest_version}...")
            download_response = requests.get(download_url, headers=self.headers)
            
            if download_response.status_code == 200:
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_path = os.path.join(temp_dir, "update.zip")
                    
                    with open(zip_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    extracted_folders = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                    if extracted_folders:
                        source_path = os.path.join(temp_dir, extracted_folders[0])
                        
                        for item in os.listdir(source_path):
                            src = os.path.join(source_path, item)
                            dst = os.path.join(extract_path, item)
                            
                            try:
                                if os.path.isdir(src):
                                    if os.path.exists(dst):
                                        shutil.rmtree(dst)
                                    shutil.copytree(src, dst)
                                else:
                                    shutil.copy2(src, dst)
                            except Exception as e:
                                logger.warning(f"Failed to copy {item}: {str(e)}")
                
                success_msg = f"Successfully updated to version {latest_version}"
                logger.info(success_msg)
                return {"success": True, "message": success_msg}
            else:
                error_msg = f"Failed to download update: HTTP {download_response.status_code}"
                logger.error(error_msg)
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            error_msg = f"Update failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    def add_repository(self, username: str, reponame: str, token: Optional[str] = None) -> None:
        """
        Add a repository to multi-repo tracking
        
        Args:
            username: GitHub username
            reponame: Repository name
            token: Optional token for private repos
        """
        repo_info = {
            "username": username,
            "reponame": reponame,
            "token": token
        }
        self.repositories.append(repo_info)
        logger.info(f"Added repository {username}/{reponame} to tracking")
    
    def check_all_repositories(self, local_versions: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Check versions for all registered repositories
        
        Args:
            local_versions: Dict mapping repo names to their local versions
            
        Returns:
            Dict with results for each repository
        """
        results = {}
        
        current_repo_key = f"{self.git_username}/{self.git_reponame}"
        if current_repo_key in local_versions:
            results[current_repo_key] = self.check(local_versions[current_repo_key])
        
        for repo in self.repositories:
            repo_key = f"{repo['username']}/{repo['reponame']}"
            if repo_key in local_versions:
                temp_sgvc = sgvc(repo['username'], repo['reponame'], repo['token'])
                results[repo_key] = temp_sgvc.check(local_versions[repo_key])
        
        return results
    
    def _save_to_history(self, check_result: Dict[str, Any]) -> None:
        """
        Save version check result to history
        
        Args:
            check_result: Result from version check
        """
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "repository": f"{self.git_username}/{self.git_reponame}",
                **check_result
            }
            
            history = []
            if os.path.exists(self.history_file):
                try:
                    with open(self.history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to read history file {self.history_file}: {str(e)}")
                    history = []
                except Exception as e:
                    logger.error(f"Unexpected error reading history: {str(e)}")
                    history = []
            
            history.append(history_entry)
            
            history = history[-100:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save to history: {str(e)}")
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get version check history
        
        Args:
            limit: Number of recent entries to return
            
        Returns:
            List of history entries
        """
        if not os.path.exists(self.history_file):
            logger.info("No history file found")
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history[-limit:]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse history file: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error reading history: {str(e)}")
            return []
    
    def gen(self, app_name: str, version_str: str, filename: str = "v.json") -> None:
        """
        Generate version file with project information
        
        Args:
            app_name: Name of the application
            version_str: Current version of the application
            filename: Name of the version file to create (default: v.json)
        """
        try:
            if not self._validate_version(version_str):
                logger.warning(f"Version format may be invalid: {version_str}")
            
            version_data = {
                "app_name": app_name,
                "version": version_str,
                "repository": f"{self.git_username}/{self.git_reponame}",
                "created_at": datetime.now().isoformat()
            }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(version_data, f, indent=4, ensure_ascii=False)
            
            success_msg = f"{filename} created successfully for {app_name} v{version_str}"
            print(success_msg)
            logger.info(success_msg)
            
        except Exception as e:
            error_msg = f"Failed to create {filename}: {str(e)}"
            logger.error(error_msg)
            print(f"Error: {error_msg}")
