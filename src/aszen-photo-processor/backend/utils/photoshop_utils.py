# backend/utils/photoshop_utils.py
import os
import platform

def find_photoshop():
    """Find Photoshop installation path"""
    system = platform.system()
    
    if system == "Windows":
        # Windows paths
        paths = [
            "C:\\Program Files\\Adobe\\Adobe Photoshop 2025\\Photoshop.exe",
            "C:\\Program Files\\Adobe\\Adobe Photoshop 2024\\Photoshop.exe",
            "C:\\Program Files\\Adobe\\Adobe Photoshop 2023\\Photoshop.exe",
            "C:\\Program Files\\Adobe\\Adobe Photoshop 2022\\Photoshop.exe",
            "C:\\Program Files\\Adobe\\Adobe Photoshop CC\\Photoshop.exe",
            "C:\\Program Files (x86)\\Adobe\\Adobe Photoshop CC\\Photoshop.exe"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
                
        # Try registry (Windows-specific)
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Adobe\\Photoshop")
            version = winreg.QueryValueEx(key, "Version")[0]
            path = winreg.QueryValueEx(key, "ApplicationPath")[0]
            return os.path.join(path, "Photoshop.exe")
        except:
            pass
            
    elif system == "Darwin":  # macOS
        # Mac paths
        paths = [
            "/Applications/Adobe Photoshop 2025/Adobe Photoshop 2025.app/Contents/MacOS/Adobe Photoshop 2025",
            "/Applications/Adobe Photoshop 2024/Adobe Photoshop 2024.app/Contents/MacOS/Adobe Photoshop 2024",
            "/Applications/Adobe Photoshop 2023/Adobe Photoshop 2023.app/Contents/MacOS/Adobe Photoshop 2023",
            "/Applications/Adobe Photoshop 2022/Adobe Photoshop 2022.app/Contents/MacOS/Adobe Photoshop 2022",
            "/Applications/Adobe Photoshop CC/Adobe Photoshop CC.app/Contents/MacOS/Adobe Photoshop CC"
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
    
    return None