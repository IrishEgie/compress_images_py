import PyInstaller.__main__
import sys
from pathlib import Path

# Get the directory containing this script
script_dir = Path(__file__).parent

def build_exe():
    PyInstaller.__main__.run([
        'main.py',  # your main script
        '--name=ImageCompressor',
        '--windowed',  # Don't show console window
        '--onefile',   # Create single executable
        '--icon=app_icon.ico',  # Optional: add if you have an icon
        '--add-data=LICENSE;.',  # Optional: include license if you have one
        '--clean',  # Clean cache
        # Add PIL plugins manually to ensure all image formats work
        '--hidden-import=PIL._tkinter_finder',
        '--collect-all=PIL',
        # High DPI support
        '--uac-admin',  # Request admin rights if needed
        # Add version info
        '--version-file=version_info.txt',  # Optional: add if you create this
    ])

if __name__ == "__main__":
    build_exe()