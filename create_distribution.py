#!/usr/bin/env python3
"""
Script to create a distribution package for the XML to SQL Converter.
This creates a zip file with all necessary files for client installation.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Files and directories to exclude from distribution
EXCLUDE_PATTERNS = [
    # Python
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "*.egg-info",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
    ".tox",
    ".hypothesis",
    
    # Virtual environment
    "venv",
    "env",
    "ENV",
    ".venv",
    
    # IDE
    ".vscode",
    ".idea",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    
    # Node
    "node_modules",
    "npm-debug.log",
    "yarn-error.log",
    
    # Build artifacts (but keep web_frontend/dist)
    "build",
    "*.egg",
    
    # Database
    "*.db",
    "conversions.db",
    
    # Logs
    "*.log",
    "logs",
    
    # Temporary files
    "*.tmp",
    "*.bak",
    
    # Git
    ".git",
    ".gitignore",
    
    # Distribution itself
    "xml2sql-distribution.zip",
    "xml2sql-distribution",
    
    # Documentation that's not needed for client
    "docs/llm_handover.md",
    "*.md",
    "!README.md",
    "!INSTALLATION_GUIDE.md",
    "!START_HERE.md",
    "!CLIENT_DEPLOYMENT_GUIDE.md",
    "!WEB_GUI_DEPLOYMENT_GUIDE.md",
    
    # Test files
    "tests",
    "test_*.py",
    
    # Source XML files (examples only, not needed)
    "Source (XML Files)",
    "Target (SQL Scripts)",
    
    # Other
    "agent",
    "skywind-plugin-marketplace",
    ".dockerignore",
    "Dockerfile",
    "docker-compose.yml",
    "Procfile",
    "runtime.txt",
]

# Files that must be included
MUST_INCLUDE = [
    "README.md",
    "INSTALLATION_GUIDE.md",
    "START_HERE.md",
    "CLIENT_DEPLOYMENT_GUIDE.md",
    "WEB_GUI_DEPLOYMENT_GUIDE.md",
    "LICENSE",
    "pyproject.toml",
    "config.example.yaml",
    "run_server.py",
    "src",
    "web_frontend",
]

def should_exclude(path: Path, root: Path) -> bool:
    """Check if a path should be excluded from the distribution."""
    rel_path = path.relative_to(root)
    path_str = str(rel_path)
    
    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("!"):
            # Must include pattern
            continue
        if pattern in path_str or path.name == pattern:
            return True
        if "*" in pattern:
            import fnmatch
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
                return True
    
    return False

def create_distribution():
    """Create the distribution package."""
    root = Path(__file__).parent
    dist_name = "xml2sql-distribution"
    dist_dir = root / dist_name
    zip_name = f"{dist_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
    
    print(f"Creating distribution package...")
    print(f"Root directory: {root}")
    print(f"Distribution directory: {dist_dir}")
    print(f"Output file: {zip_name}")
    
    # Clean up old distribution directory
    if dist_dir.exists():
        print(f"Removing old distribution directory: {dist_dir}")
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir(exist_ok=True)
    
    # Copy files
    files_copied = 0
    dirs_copied = 0
    
    def copy_item(src: Path, dst: Path):
        nonlocal files_copied, dirs_copied
        if src.is_file():
            shutil.copy2(src, dst)
            files_copied += 1
        elif src.is_dir():
            dst.mkdir(exist_ok=True)
            dirs_copied += 1
            for item in src.iterdir():
                if not should_exclude(item, root):
                    copy_item(item, dst / item.name)
    
    # Copy must-include items
    for item_name in MUST_INCLUDE:
        item_path = root / item_name
        if item_path.exists():
            print(f"Copying: {item_name}")
            copy_item(item_path, dist_dir / item_name)
        else:
            print(f"Warning: {item_name} not found, skipping")
    
    # Copy other files (excluding patterns)
    for item in root.iterdir():
        if item.name == dist_name or item.name == zip_name:
            continue
        if item.name.startswith("."):
            continue
        if should_exclude(item, root):
            continue
        if item.name in [i.split("/")[0] for i in MUST_INCLUDE]:
            continue  # Already copied
        
        print(f"Copying: {item.name}")
        copy_item(item, dist_dir / item.name)
    
    # Ensure web_frontend/dist exists (built frontend)
    web_frontend_dist = root / "web_frontend" / "dist"
    if not web_frontend_dist.exists():
        print("\n⚠️  Warning: web_frontend/dist not found!")
        print("The frontend needs to be built before creating distribution.")
        print("Building frontend now...")
        import subprocess
        try:
            subprocess.run(["npm", "run", "build"], cwd=root / "web_frontend", check=True)
            print("✅ Frontend built successfully")
        except subprocess.CalledProcessError:
            print("❌ Frontend build failed. Please run manually:")
            print("   cd web_frontend && npm install && npm run build")
            shutil.rmtree(dist_dir)
            return
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js and run:")
            print("   cd web_frontend && npm install && npm run build")
            shutil.rmtree(dist_dir)
            return
    
    # Create zip file
    print(f"\nCreating zip file: {zip_name}")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root_dir, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root_dir) / file
                arc_name = file_path.relative_to(dist_dir)
                zipf.write(file_path, arc_name)
                print(f"  Added: {arc_name}")
    
    # Clean up distribution directory
    print(f"\nCleaning up temporary directory: {dist_dir}")
    shutil.rmtree(dist_dir)
    
    print(f"\n✅ Distribution package created: {zip_name}")
    print(f"   Files copied: {files_copied}")
    print(f"   Directories copied: {dirs_copied}")
    print(f"\nNext steps:")
    print(f"1. Test the package by extracting it and following INSTALLATION_GUIDE.md")
    print(f"2. Commit and push to Git:")
    print(f"   git add {zip_name}")
    print(f"   git commit -m 'Add distribution package'")
    print(f"   git push")

if __name__ == "__main__":
    create_distribution()

