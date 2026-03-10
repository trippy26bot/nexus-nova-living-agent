#!/usr/bin/env python3
"""
Nova Environment Adapter Layer
Detects and adapts to different operating systems
"""

import platform
import os
import subprocess
from pathlib import Path


class EnvironmentAdapter:
    """Unified interface across all operating systems"""
    
    def __init__(self):
        self.os_type = self.detect_environment()
        self.adapter = self.get_adapter()
    
    def detect_environment(self) -> str:
        """Detect current operating system"""
        os_name = platform.system()
        
        if os_name == "Darwin":
            return "mac"
        elif os_name == "Windows":
            return "windows"
        elif os_name == "Linux":
            # Check for specific Linux distribution
            try:
                with open("/etc/os-release", "r") as f:
                    if "ubuntu" in f.read().lower():
                        return "ubuntu"
                    elif "arch" in f.read().lower():
                        return "arch"
            except:
                pass
            return "linux"
        else:
            return "unknown"
    
    def get_adapter(self):
        """Get OS-specific adapter"""
        if self.os_type == "mac":
            return MacAdapter()
        elif self.os_type == "windows":
            return WindowsAdapter()
        else:
            return LinuxAdapter()
    
    def open_file(self, path: str):
        """Open file with default application"""
        return self.adapter.open_file(path)
    
    def open_url(self, url: str):
        """Open URL in default browser"""
        return self.adapter.open_url(url)
    
    def get_path(self, *parts) -> Path:
        """Get cross-platform path"""
        return Path(*parts)
    
    def get_home(self) -> Path:
        """Get home directory"""
        return Path.home()
    
    def list_dir(self, path: str) -> list:
        """List directory contents"""
        return os.listdir(path)


class MacAdapter:
    """macOS-specific adaptations"""
    
    def open_file(self, path: str):
        subprocess.run(["open", path], check=False)
    
    def open_url(self, url: str):
        subprocess.run(["open", url], check=False)


class WindowsAdapter:
    """Windows-specific adaptations"""
    
    def open_file(self, path: str):
        subprocess.run(["start", "", path], shell=True, check=False)
    
    def open_url(self, url: str):
        subprocess.run(["start", "", url], shell=True, check=False)


class LinuxAdapter:
    """Linux-specific adaptations"""
    
    def open_file(self, path: str):
        # Try common file managers
        for cmd in ["xdg-open", "gnome-open", "kfmclient"]:
            try:
                subprocess.run([cmd, path], check=False)
                return
            except:
                pass
    
    def open_url(self, url: str):
        subprocess.run(["xdg-open", url], check=False)


# Global instance
_env_adapter = None

def get_environment_adapter() -> EnvironmentAdapter:
    global _env_adapter
    if _env_adapter is None:
        _env_adapter = EnvironmentAdapter()
    return _env_adapter
