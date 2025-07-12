import os
import sys
import subprocess
import shutil

def main():
    # Clean up previous builds
    print("Cleaning up previous builds...")
    for item in ['build', 'dist']:
        if os.path.exists(item):
            shutil.rmtree(item)
    if os.path.exists('JSGCLingunanWorshipTeamPresenter.spec'):
        os.remove('JSGCLingunanWorshipTeamPresenter.spec')
    
    # Ensure required directories exist
    os.makedirs('dist', exist_ok=True)
    
    # Run PyInstaller
    print("Building executable...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=JSGCLingunanWorshipTeamPresenter',
        '--onefile',
        '--windowed',
        '--icon=config/app_logo.png',
        '--add-data=config/app_logo.png;config',
        '--add-data=config/defaults.json;config',
        '--clean',
        '--noconfirm',
        '_app.py'
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful!")
        print("The executable is in the 'dist' folder.")
        print("You can now distribute 'JSGCLingunanWorshipTeamPresenter.exe' as a standalone application.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        print("Please make sure all required packages are installed.")
        print("You can install them using: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == '__main__':
    main()
