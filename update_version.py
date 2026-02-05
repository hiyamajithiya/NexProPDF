"""
Version Update Script for NexPro PDF
Run this script to update version across all files:
    python update_version.py 1.1.0

Files updated:
- src/version.py (source of truth)
- config/config.yaml
- installer.iss
"""

import sys
import re
from pathlib import Path


def update_version(new_version: str):
    """Update version in all relevant files"""

    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"Error: Invalid version format '{new_version}'. Use X.Y.Z format (e.g., 1.0.0)")
        return False

    base_path = Path(__file__).parent
    files_updated = []

    # 1. Update src/version.py
    version_file = base_path / 'src' / 'version.py'
    if version_file.exists():
        content = version_file.read_text(encoding='utf-8')

        # Update __version__
        content = re.sub(
            r'__version__ = "[^"]*"',
            f'__version__ = "{new_version}"',
            content
        )

        # Update __version_info__
        parts = new_version.split('.')
        version_tuple = f"({parts[0]}, {parts[1]}, {parts[2]})"
        content = re.sub(
            r'__version_info__ = \([^)]*\)',
            f'__version_info__ = {version_tuple}',
            content
        )

        version_file.write_text(content, encoding='utf-8')
        files_updated.append('src/version.py')

    # 2. Update config/config.yaml
    config_file = base_path / 'config' / 'config.yaml'
    if config_file.exists():
        content = config_file.read_text(encoding='utf-8')
        content = re.sub(
            r'version: "[^"]*"',
            f'version: "{new_version}"',
            content
        )
        config_file.write_text(content, encoding='utf-8')
        files_updated.append('config/config.yaml')

    # 3. Update installer.iss
    installer_file = base_path / 'installer.iss'
    if installer_file.exists():
        content = installer_file.read_text(encoding='utf-8')
        content = re.sub(
            r'#define MyAppVersion "[^"]*"',
            f'#define MyAppVersion "{new_version}"',
            content
        )
        installer_file.write_text(content, encoding='utf-8')
        files_updated.append('installer.iss')

    print(f"Version updated to {new_version}")
    print(f"Files updated: {', '.join(files_updated)}")
    print("\nNext steps:")
    print("1. Update version history in src/version.py")
    print("2. Rebuild: pyinstaller NexProPDF.spec")
    print("3. Create installer: ISCC.exe installer.iss")
    print("4. Create zip: Compress-Archive installer_output\\NexProPDF_Setup.exe NexProPDF_Installer.zip")

    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <version>")
        print("Example: python update_version.py 1.1.0")
        sys.exit(1)

    new_version = sys.argv[1]
    success = update_version(new_version)
    sys.exit(0 if success else 1)
