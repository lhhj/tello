#!/usr/bin/env python3
"""
Setup script for Tello Drone Controller
This script helps verify and install dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True

def main():
    print("=== Tello Drone Controller Setup ===\n")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Required packages
    packages = [
        "djitellopy==2.5.0",
        "opencv-python==4.8.1.78", 
        "pygame==2.5.2",
        "Pillow==10.0.1",
        "numpy==1.25.2"
    ]
    
    print("\nInstalling required packages...")
    
    failed_packages = []
    for package in packages:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
        print("Please install them manually using:")
        for package in failed_packages:
            print(f"   pip install {package}")
    else:
        print("\n✅ All packages installed successfully!")
        
    print("\n=== Setup Complete ===")
    print("\nNext steps:")
    print("1. Connect to your Tello drone's WiFi network (TELLO-XXXXXX)")
    print("2. Run the demo version: python tello_controller_demo.py")
    print("3. Run with real drone: python tello_controller.py")
    print("4. Test components: python test_components.py")

if __name__ == "__main__":
    main()