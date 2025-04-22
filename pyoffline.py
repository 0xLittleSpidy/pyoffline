import os
import sys
import requests
import zipfile
import shutil
import subprocess
from urllib.parse import urlparse
import argparse

def download_repo(repo_url):
    """Download a GitHub repository as a zip file and extract it to current directory"""
    try:
        # Handle different GitHub URL formats
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        if repo_url.startswith('git@github.com:'):
            repo_url = repo_url.replace('git@github.com:', 'https://github.com/')
        
        # Convert to the zip download URL
        if not repo_url.startswith('https://github.com/'):
            raise ValueError("Invalid GitHub repository URL")
        
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL")
        
        owner, repo = path_parts[:2]
        if repo.endswith('/'):
            repo = repo[:-1]
        
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
        
        # Try main branch first, then master
        try:
            response = requests.get(zip_url, stream=True)
            if response.status_code != 200:
                zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
                response = requests.get(zip_url, stream=True)
                if response.status_code != 200:
                    raise ValueError("Could not find main or master branch")
        except requests.RequestException as e:
            raise ValueError(f"Failed to download repository: {e}")
        
        # Download the zip file to current directory
        zip_path = os.path.join(os.getcwd(), 'repo_temp.zip')
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the zip file to current directory
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.getcwd())
        
        # Find the extracted folder (either main or master branch)
        extracted_folder = None
        for item in os.listdir(os.getcwd()):
            if item == 'repo_temp.zip':
                continue
            if item.startswith(repo + '-'):
                extracted_folder = os.path.join(os.getcwd(), item)
                break
        
        if not extracted_folder:
            raise ValueError("Failed to find extracted repository folder")
        
        # Remove the zip file
        os.remove(zip_path)
        
        return extracted_folder, repo
    except Exception as e:
        raise ValueError(f"Error downloading repository: {e}")

def find_requirements_file(repo_path):
    """Search for requirements.txt in the repository"""
    for root, _, files in os.walk(repo_path):
        if 'requirements.txt' in files:
            return os.path.join(root, 'requirements.txt')
    return None

def download_dependencies(requirements_path, repo_path, platform):
    """Download all dependencies to the specified directory"""
    try:
        # Create wheels directory inside the repo
        wheels_dir = os.path.join(repo_path, 'wheels')
        os.makedirs(wheels_dir, exist_ok=True)
        
        print("\nAttempting to download dependencies...")
        
        # Build pip download command based on platform
        cmd = ['pip', 'download', '-r', requirements_path, '--dest', wheels_dir]
        
        if platform != 'none':
            cmd.extend(['--platform', platform, '--python-version', '3'])
            if platform != 'any':
                cmd.append('--only-binary=:all:')
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: Some dependencies might not be available for {platform}:")
            print(result.stderr)
            print("Attempting to download platform-agnostic packages...")
            cmd = ['pip', 'download', '-r', requirements_path, '--dest', wheels_dir]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("Attempting to download with source packages allowed...")
                cmd = ['pip', 'download', '-r', requirements_path, '--dest', wheels_dir, '--no-binary', ':none:']
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"Failed to download dependencies: {result.stderr}")
        
        return wheels_dir
    except Exception as e:
        raise RuntimeError(f"Error downloading dependencies: {e}")

def zip_repository(repo_path, output_name):
    """Create a zip file of the repository"""
    try:
        # Get the folder name
        folder_name = os.path.basename(repo_path)
        
        # Create the zip file in current directory
        shutil.make_archive(output_name, 'zip', os.path.dirname(repo_path), folder_name)
        return f"{output_name}.zip"
    except Exception as e:
        raise RuntimeError(f"Error creating zip file: {e}")

def get_file_size_mb(file_path):
    """Get file size in megabytes"""
    try:
        return round(os.path.getsize(file_path) / (1024 * 1024), 2)
    except:
        return "unknown"

def main():
    parser = argparse.ArgumentParser(
        description='PyOffline - GitHub Repository Downloader with Dependency Bundler\n'
                    'Download Python projects with all dependencies for offline installation',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'repo_url', 
        help='GitHub repository URL (e.g., https://github.com/user/repo or user/repo)'
    )
    parser.add_argument(
        '-p', '--platform', 
        default='manylinux2014_x86_64',
        help='Platform for wheel downloads:\n'
             '  manylinux2014_x86_64 - Linux 64-bit (default)\n'
             '  win_amd64 - Windows 64-bit\n'
             '  macosx_10_9_x86_64 - macOS Intel\n'
             '  any - Platform-agnostic wheels\n'
             '  none - Allow source packages'
    )
    parser.add_argument(
        '-k', '--keep', 
        action='store_true',
        help='Keep the downloaded repository folder after zipping'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output during operation'
    )
    
    args = parser.parse_args()
    
    try:
        print(f"PyOffline: Downloading repository: {args.repo_url}")
        repo_path, repo_name = download_repo(args.repo_url)
        print(f"Repository downloaded to: {os.path.basename(repo_path)}")
        
        requirements_path = find_requirements_file(repo_path)
        if requirements_path:
            print(f"\nFound requirements.txt at: {os.path.relpath(requirements_path, repo_path)}")
            print(f"Downloading dependencies for platform: {args.platform}")
            wheels_dir = download_dependencies(requirements_path, repo_path, args.platform)
            print(f"Dependencies downloaded to: {os.path.relpath(wheels_dir, repo_path)}")
        else:
            print("\nNo requirements.txt found, skipping dependency download")
        
        zip_name = repo_name.lower().replace('_', '-')
        print(f"\nCreating zip file: {zip_name}.zip")
        zip_path = zip_repository(repo_path, zip_name)
        zip_size = get_file_size_mb(zip_path)
        print(f"Zip file created: {zip_path}")
        print(f"Size: {zip_size} MB")
        
        # Clean up if not keeping the folder
        if not args.keep:
            shutil.rmtree(repo_path)
            print("Temporary files cleaned up")
        
        print("\n" + "="*50)
        print("PyOffline operation completed successfully!")
        print(f"Offline bundle created: {zip_path}")
        
        if requirements_path:
            print("\nTo install on offline machine:")
            print(f"1. Unzip {zip_name}.zip")
            print(f"2. cd {repo_name}-*")
            print("3. Install dependencies:")
            print("   pip install --no-index --find-links=./wheels -r requirements.txt")
        print("="*50)
    except Exception as e:
        print(f"\nPyOffline Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
