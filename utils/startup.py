"""Windows startup management utility."""
import sys
import os
import winreg
from pathlib import Path


class StartupManager:
    """Manages Windows startup registration."""

    APP_NAME = "DontTouch"
    REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @classmethod
    def get_executable_path(cls) -> str:
        """Get the path to the executable or script."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable (PyInstaller)
            return sys.executable
        else:
            # Running as Python script
            main_script = Path(__file__).parent.parent / "main.py"
            python_exe = sys.executable
            return f'"{python_exe}" "{main_script}"'

    @classmethod
    def is_registered(cls) -> bool:
        """Check if application is registered in startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, cls.APP_NAME)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
        except WindowsError:
            return False

    @classmethod
    def register(cls) -> bool:
        """Register application to run at startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            try:
                exe_path = cls.get_executable_path()
                winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, exe_path)
                return True
            finally:
                winreg.CloseKey(key)
        except WindowsError as e:
            print(f"Failed to register startup: {e}")
            return False

    @classmethod
    def unregister(cls) -> bool:
        """Remove application from startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            try:
                winreg.DeleteValue(key, cls.APP_NAME)
                return True
            except FileNotFoundError:
                # Already not registered
                return True
            finally:
                winreg.CloseKey(key)
        except WindowsError as e:
            print(f"Failed to unregister startup: {e}")
            return False

    @classmethod
    def set_startup(cls, enabled: bool) -> bool:
        """Set startup registration based on enabled flag."""
        if enabled:
            return cls.register()
        else:
            return cls.unregister()
