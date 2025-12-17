"""Update checker module for Don't Touch application."""
import threading
import webbrowser
from typing import Optional, Callable, Tuple
from dataclasses import dataclass
import urllib.request
import json
import ssl

# App version - should match about_window.py
APP_VERSION = "1.0.0"
GITHUB_API_URL = "https://api.github.com/repos/writingdeveloper/dont-touch/releases/latest"
GITHUB_RELEASES_URL = "https://github.com/writingdeveloper/dont-touch/releases"


@dataclass
class UpdateInfo:
    """Information about an available update."""
    current_version: str
    latest_version: str
    release_url: str
    release_notes: str
    is_update_available: bool


def parse_version(version: str) -> Tuple[int, ...]:
    """Parse version string to tuple for comparison.

    Args:
        version: Version string like "1.0.0" or "v1.0.0"

    Returns:
        Tuple of integers for comparison
    """
    # Remove 'v' prefix if present
    version = version.lstrip('v').strip()

    # Split by dots and convert to integers
    try:
        parts = []
        for part in version.split('.'):
            # Handle versions like "1.0.0-beta"
            num_part = part.split('-')[0]
            parts.append(int(num_part))
        return tuple(parts)
    except (ValueError, AttributeError):
        return (0, 0, 0)


def compare_versions(current: str, latest: str) -> int:
    """Compare two version strings.

    Args:
        current: Current version string
        latest: Latest version string

    Returns:
        -1 if current < latest (update available)
         0 if current == latest (up to date)
         1 if current > latest (ahead of release)
    """
    current_tuple = parse_version(current)
    latest_tuple = parse_version(latest)

    if current_tuple < latest_tuple:
        return -1
    elif current_tuple > latest_tuple:
        return 1
    else:
        return 0


def check_for_updates() -> Optional[UpdateInfo]:
    """Check GitHub for the latest release.

    Returns:
        UpdateInfo object with update details, or None if check failed
    """
    try:
        # Create SSL context (required for HTTPS)
        context = ssl.create_default_context()

        # Create request with User-Agent (required by GitHub API)
        request = urllib.request.Request(
            GITHUB_API_URL,
            headers={
                'User-Agent': 'DontTouch-UpdateChecker',
                'Accept': 'application/vnd.github.v3+json'
            }
        )

        # Make request with timeout
        with urllib.request.urlopen(request, timeout=10, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))

        # Extract version from tag_name (usually "v1.0.0" or "1.0.0")
        latest_version = data.get('tag_name', '0.0.0')
        release_url = data.get('html_url', GITHUB_RELEASES_URL)
        release_notes = data.get('body', '')

        # Compare versions
        comparison = compare_versions(APP_VERSION, latest_version)

        return UpdateInfo(
            current_version=APP_VERSION,
            latest_version=latest_version.lstrip('v'),
            release_url=release_url,
            release_notes=release_notes,
            is_update_available=(comparison < 0)
        )

    except Exception as e:
        # Silently fail - update check is not critical
        print(f"Update check failed: {e}")
        return None


def check_for_updates_async(callback: Callable[[Optional[UpdateInfo]], None]) -> None:
    """Check for updates in a background thread.

    Args:
        callback: Function to call with UpdateInfo when check completes
    """
    def _check():
        result = check_for_updates()
        callback(result)

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()


def open_download_page() -> None:
    """Open the GitHub releases page in the default browser."""
    webbrowser.open(GITHUB_RELEASES_URL)


def get_current_version() -> str:
    """Get the current application version."""
    return APP_VERSION
