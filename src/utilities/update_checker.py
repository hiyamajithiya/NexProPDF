"""
Update Checker - checks GitHub Releases for new versions of NexPro PDF.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict
from src.version import __version__
from src.utilities.logger import get_logger


GITHUB_REPO = "hiyamajithiya/NexProPDF"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
TIMEOUT = 5  # seconds


class UpdateChecker:
    """Checks GitHub Releases for new versions."""

    def __init__(self):
        self.logger = get_logger()

    def check_for_updates(self) -> Optional[Dict]:
        """
        Query GitHub Releases API for the latest version.

        Returns:
            Dict with keys: available, latest_version, download_url, release_notes
            None if check failed (offline, API error, etc.)
        """
        try:
            req = urllib.request.Request(
                API_URL,
                headers={"Accept": "application/vnd.github.v3+json",
                         "User-Agent": "NexProPDF-UpdateChecker"}
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            tag = data.get("tag_name", "")
            latest = tag.lstrip("vV")  # "v1.1.0" → "1.1.0"

            download_url = ""
            for asset in data.get("assets", []):
                name = asset.get("name", "")
                if name.lower().endswith((".exe", ".zip")):
                    download_url = asset.get("browser_download_url", "")
                    break
            if not download_url:
                download_url = data.get("html_url", "")

            is_newer = self._version_newer(latest, __version__)

            return {
                "available": is_newer,
                "latest_version": latest,
                "current_version": __version__,
                "download_url": download_url,
                "release_notes": data.get("body", ""),
            }

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            self.logger.debug(f"Update check network error: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Update check error: {e}")
            return None

    @staticmethod
    def _version_newer(latest: str, current: str) -> bool:
        """Compare version strings (X.Y.Z). Returns True if latest > current."""
        try:
            def parts(v):
                return tuple(int(x) for x in v.split(".")[:3])
            return parts(latest) > parts(current)
        except (ValueError, IndexError):
            return False
