import sys
import os


def resource_path(relative_path: str) -> str:
    """Returns the absolute path to a resource, compatible with PyInstaller bundles."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, relative_path)
