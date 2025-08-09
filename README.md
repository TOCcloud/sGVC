# sGVC - Simple GitHub Version Control

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)

A powerful and lightweight Python library for application version control using GitHub releases. Streamline your deployment process with semantic versioning, automatic updates, and comprehensive version tracking.

**Developer:** Kozosvyst Stas

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Advanced Usage](#-advanced-usage)
- [API Reference](#-api-reference)
- [Examples](#-examples)
- [FAQ](#-faq)
- [Support](#-support)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- 🔍 **Semantic Version Comparison** - Intelligent version parsing with detailed difference analysis
- 🚀 **Automatic Updates** - Download and install latest releases automatically
- 📊 **Multi-Repository Support** - Track multiple projects simultaneously
- 🔐 **Private Repository Access** - Full support for private repos with GitHub tokens
- 📈 **Version History Tracking** - Local history of all version checks
- 🛡️ **Error Handling & Logging** - Comprehensive error handling with detailed logging
- ⚡ **Optimized Performance** - Smart caching and update optimization
- 📁 **Flexible File Management** - Configurable version file names and locations

---

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Internet connection for GitHub API access

### Install Dependencies

```bash
pip install requests packaging
```

### Download sGVC

```bash
# Clone the repository
git clone https://github.com/StasX-Official/sGVC.git
cd sGVC

# Or download directly
wget https://github.com/StasX-Official/sGVC/archive/main.zip
```

---

## 🎯 Quick Start

### Basic Initialization

```python
from sgvc import sgvc

# Initialize for public repository
svc = sgvc(git_username="StasX-Official", git_reponame="test")

# Initialize for private repository
svc = sgvc(git_username="YourUsername", git_reponame="private-repo", 
           token="ghp_your_github_token_here")
```

### Check Version Status

```python
result = svc.check(local_version="1.0.0")
print(result)
```

**Output:**
```json
{
    "last": "1.2.0",
    "local": "1.0.0", 
    "status": "old",
    "difference": "2 minor version(s) behind",
    "behind_by": 2
}
```

### Generate Version File

```python
# Create default v.json
svc.gen("MyApp", "1.0.0")

# Create custom filename
svc.gen("MyApp", "1.0.0", filename="version.json")
```

---

## 🔧 Advanced Usage

### Automatic Updates

```python
# Interactive update with confirmation
update_result = svc.update(interactive=True)

# Silent update to specific directory
update_result = svc.update(interactive=False, extract_path="./app_updates")

# Check if update needed before downloading
update_result = svc.update(check_current=True)

print(update_result)
# {"success": True, "message": "Successfully updated to version 1.2.0"}
```

### Multi-Repository Tracking

```python
# Add multiple repositories
svc.add_repository("microsoft", "vscode")
svc.add_repository("facebook", "react", token="optional_token")

# Check all repositories at once
local_versions = {
    "StasX-Official/test": "1.0.0",
    "microsoft/vscode": "1.75.0",
    "facebook/react": "18.2.0"
}

results = svc.check_all_repositories(local_versions)
for repo, status in results.items():
    print(f"{repo}: {status['status']} - {status['difference']}")
```

### Version History

```python
# Get recent version checks
history = svc.get_history(limit=5)
for entry in history:
    print(f"{entry['timestamp']}: {entry['repository']} - {entry['status']}")

# Get full history
full_history = svc.get_history(limit=100)
```

### Error Handling

```python
try:
    result = svc.check("1.0.0")
    if result['status'] == 'error':
        print(f"Error: {result['difference']}")
    elif result['status'] == 'old':
        print(f"Update available: {result['difference']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 📚 API Reference

### Class: `sgvc(git_username, git_reponame, token=None)`

#### Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `check(local_version)` | Compare local version with latest release | `local_version` (str) | Dict with comparison results |
| `update(interactive=True, extract_path=".", check_current=True)` | Download and install latest version | `interactive` (bool), `extract_path` (str), `check_current` (bool) | Dict with update status |
| `gen(app_name, version, filename="v.json")` | Generate version file | `app_name` (str), `version` (str), `filename` (str) | None |
| `add_repository(username, reponame, token=None)` | Add repository to tracking | `username` (str), `reponame` (str), `token` (str, optional) | None |
| `check_all_repositories(local_versions)` | Check multiple repositories | `local_versions` (Dict[str, str]) | Dict with all results |
| `get_history(limit=10)` | Get version check history | `limit` (int) | List of history entries |

---

## 💡 Examples

### Example 1: Complete Version Management Workflow

```python
from sgvc import sgvc
import json

# Initialize
svc = sgvc("StasX-Official", "my-project")

# Check current status
status = svc.check("1.0.0")
print(f"Status: {status['status']}")
print(f"Current: {status['local']}, Latest: {status['last']}")

if status['status'] == 'old':
    print(f"You are {status['difference']}")
    
    # Ask user if they want to update
    update_result = svc.update(interactive=True)
    if update_result['success']:
        # Generate new version file
        svc.gen("MyProject", status['last'])
        print("Update completed successfully!")
```

### Example 2: Automated CI/CD Integration

```python
import os
from sgvc import sgvc

def check_and_update_dependencies():
    """Automated dependency checking for CI/CD"""
    
    dependencies = [
        {"user": "StasX-Official", "repo": "core-lib", "current": "2.1.0"},
        {"user": "StasX-Official", "repo": "utils", "current": "1.5.2"},
    ]
    
    updates_available = []
    
    for dep in dependencies:
        svc = sgvc(dep["user"], dep["repo"], token=os.getenv("GITHUB_TOKEN"))
        result = svc.check(dep["current"])
        
        if result['status'] == 'old':
            updates_available.append({
                "repo": f"{dep['user']}/{dep['repo']}",
                "current": result['local'],
                "latest": result['last'],
                "difference": result['difference']
            })
    
    return updates_available

# Usage in CI/CD
updates = check_and_update_dependencies()
if updates:
    print("⚠️ Updates available:")
    for update in updates:
        print(f"  {update['repo']}: {update['current']} → {update['latest']}")
```

### Example 3: Version Monitoring Dashboard

```python
from sgvc import sgvc
import time
from datetime import datetime

class VersionMonitor:
    def __init__(self):
        self.projects = []
    
    def add_project(self, username, reponame, current_version, token=None):
        self.projects.append({
            "svc": sgvc(username, reponame, token),
            "name": f"{username}/{reponame}",
            "current": current_version
        })
    
    def generate_report(self):
        report = {
            "timestamp": datetime.now().isoformat(),
            "projects": []
        }
        
        for project in self.projects:
            result = project["svc"].check(project["current"])
            report["projects"].append({
                "name": project["name"],
                "status": result["status"],
                "current": result["local"],
                "latest": result["last"],
                "needs_update": result["status"] == "old"
            })
        
        return report

# Usage
monitor = VersionMonitor()
monitor.add_project("StasX-Official", "project1", "1.0.0")
monitor.add_project("StasX-Official", "project2", "2.1.0")

report = monitor.generate_report()
print(f"Generated report with {len(report['projects'])} projects")
```

---

## ❓ FAQ

### General Questions

**Q: What version formats are supported?**
A: sGVC supports semantic versioning (SemVer) format: `MAJOR.MINOR.PATCH` (e.g., 1.0.0, 2.1.3). Pre-release and build metadata are also supported (e.g., 1.0.0-alpha.1+build.123).

**Q: Can I use sGVC with private repositories?**
A: Yes! Use a GitHub Personal Access Token when initializing sGVC for private repositories.

**Q: Does sGVC work with GitHub Enterprise?**
A: Currently, sGVC is designed for GitHub.com. GitHub Enterprise support may be added in future versions.

### Technical Questions

**Q: How does version comparison work?**
A: sGVC uses semantic versioning rules. It compares major, minor, and patch versions in order, providing detailed information about the difference.

**Q: What happens if a repository has no releases?**
A: sGVC will return `status: "unknown"` and `last: "no_releases"` when no releases are found.

**Q: Can I customize the update process?**
A: Yes! You can specify the extraction path, disable interactive confirmation, and control whether to check current version before updating.

### Troubleshooting

**Q: I'm getting authentication errors with private repos**
A: Ensure your GitHub token has the necessary permissions (`repo` scope for private repositories).

**Q: Version checking is slow**
A: This may be due to GitHub API rate limiting. Consider using authentication tokens to increase rate limits.

**Q: The update feature isn't working**
A: Check that the repository has releases with downloadable assets and that you have write permissions to the target directory.

---

## 🆘 Support

We're here to help! Choose the appropriate channel for your needs:

### 📧 Contact Information

- **General Support & Questions**: [support@sxscli.com](mailto:support@sxscli.com)
- **Bug Reports & Issues**: [report@sxscli.com](mailto:report@sxscli.com)
- **Legal & Licensing**: [legal@sxscli.com](mailto:legal@sxscli.com)

### 📝 When Reporting Issues

Please include the following information:

1. **sGVC version** you're using
2. **Python version** and operating system
3. **Repository details** (username/repo) if applicable
4. **Error messages** or unexpected behavior
5. **Steps to reproduce** the issue
6. **Expected vs actual behavior**

### 🔍 Self-Help Resources

1. Check this README for common solutions
2. Review the examples section for usage patterns
3. Enable logging to see detailed error information:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### ⚡ Response Times

- **General Support**: 24-48 hours
- **Bug Reports**: 12-24 hours
- **Critical Issues**: 2-8 hours

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/StasX-Official/sGVC.git
cd sGVC
pip install -r requirements.txt
```

---

## 📄 License

Created by **Kozosvyst Stas**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgments

- Thanks to the GitHub API for making version tracking possible
- Special thanks to all contributors and users

---

**2025 sGVC. All rights reserved.**
