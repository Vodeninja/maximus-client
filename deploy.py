#!/usr/bin/env python3
"""
Deployment script for maximus-client package
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"❌ Error: {result.stderr}", file=sys.stderr)
    
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    
    return result

def clean_build():
    """Clean build directories."""
    print("🧹 Cleaning build directories...")
    
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean egg-info directories
    for egg_info in Path(".").glob("*.egg-info"):
        if egg_info.is_dir():
            shutil.rmtree(egg_info)
            print(f"   Removed {egg_info}/")

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing build dependencies...")
    run_command("python -m pip install --upgrade pip build twine")

def build_package():
    """Build the package."""
    print("🔨 Building package...")
    run_command("python -m build")

def check_package():
    """Check the package with twine."""
    print("🔍 Checking package...")
    run_command("python -m twine check dist/*")

def test_import():
    """Test package import."""
    print("🧪 Testing package import...")
    try:
        import maximus
        print("✅ Import test successful")
        print(f"   Package version: {maximus.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def upload_to_testpypi():
    """Upload to TestPyPI."""
    print("🚀 Uploading to TestPyPI...")
    run_command("python -m twine upload --repository testpypi dist/*")

def upload_to_pypi():
    """Upload to PyPI."""
    print("🚀 Uploading to PyPI...")
    run_command("python -m twine upload dist/*")

def main():
    print("🐍 Maximus Client Deployment Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("maximus").exists() or not Path("setup.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    try:
        # Ask what to do
        print("\nWhat would you like to do?")
        print("1. Build and test package")
        print("2. Upload to TestPyPI")
        print("3. Upload to PyPI")
        print("4. Full deployment (build + test + upload to PyPI)")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # Build and test
            install_dependencies()
            clean_build()
            build_package()
            check_package()
            test_import()
            print("\n✅ Package built and tested successfully!")
            
        elif choice == "2":
            # Upload to TestPyPI
            install_dependencies()
            clean_build()
            build_package()
            check_package()
            upload_to_testpypi()
            print("\n✅ Package uploaded to TestPyPI!")
            print("🔗 Check: https://test.pypi.org/project/maximus-client/")
            print("📥 Test install: pip install -i https://test.pypi.org/simple/ maximus-client")
            
        elif choice == "3":
            # Upload to PyPI
            print("\n⚠️  You are about to upload to the REAL PyPI!")
            confirm = input("Are you sure? Type 'yes' to confirm: ")
            if confirm.lower() == "yes":
                install_dependencies()
                clean_build()
                build_package()
                check_package()
                upload_to_pypi()
                print("\n✅ Package uploaded to PyPI!")
                print("🔗 Check: https://pypi.org/project/maximus-client/")
                print("📥 Install: pip install maximus-client")
            else:
                print("❌ Upload cancelled")
                
        elif choice == "4":
            # Full deployment
            print("\n🚀 Starting full deployment process...")
            
            # Build and test
            install_dependencies()
            clean_build()
            build_package()
            check_package()
            
            if not test_import():
                print("❌ Import test failed, stopping deployment")
                sys.exit(1)
            
            # Test on TestPyPI first
            print("\n📤 First uploading to TestPyPI for testing...")
            upload_to_testpypi()
            print("✅ Uploaded to TestPyPI")
            
            # Confirm PyPI upload
            print("\n⚠️  Ready to upload to PyPI!")
            confirm = input("Continue with PyPI upload? Type 'yes' to confirm: ")
            if confirm.lower() == "yes":
                upload_to_pypi()
                print("\n🎉 Full deployment completed!")
                print("🔗 PyPI: https://pypi.org/project/maximus-client/")
                print("📥 Install: pip install maximus-client")
            else:
                print("❌ PyPI upload cancelled")
        else:
            print("❌ Invalid choice")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()