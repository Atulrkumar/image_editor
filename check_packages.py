"""
Check which packages are already installed for the Image Text Editor
Run this to see what's missing before trying pip install
"""

import sys

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} - INSTALLED")
        return True
    except ImportError:
        print(f"❌ {package_name} - NOT INSTALLED")
        return False

def main():
    print("=" * 60)
    print("Image Text Editor - Package Installation Check")
    print("=" * 60)
    print()
    
    required_packages = [
        ("flask", "flask"),
        ("pillow", "PIL"),
        ("requests", "requests"),
        ("python-dotenv", "dotenv"),
        ("anthropic", "anthropic"),
    ]
    
    installed = []
    missing = []
    
    for package_name, import_name in required_packages:
        if check_package(package_name, import_name):
            installed.append(package_name)
        else:
            missing.append(package_name)
    
    print()
    print("=" * 60)
    print(f"Summary: {len(installed)}/{len(required_packages)} packages installed")
    print("=" * 60)
    
    if missing:
        print()
        print("📦 Missing packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print()
        print("To install missing packages:")
        print(f"   pip install {' '.join(missing)}")
    else:
        print()
        print("🎉 All packages are installed!")
        print("You're ready to run the app with: python app.py")
    
    print()
    print("Python version:", sys.version)

if __name__ == "__main__":
    main()
