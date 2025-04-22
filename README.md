# PyOffline 📦🔌

A Python tool to download GitHub repositories with all dependencies for offline installation. Perfect for air-gapped systems or environments with restricted internet access.

## Features ✨

- Downloads GitHub repositories (supports HTTPS and git@ URLs)
- Auto-detects and downloads Python dependencies from `requirements.txt`
- Multiple platform support (Linux, Windows, macOS)
- Creates a ready-to-use zip archive with all dependencies
- Three-stage download fallback for maximum compatibility
- Clean, verbose output with progress reporting

## Installation ⚙️

```bash
pip install git+https://github.com/0xLittleSpidy/pyoffline.git
```

Or download directly:

```bash
git clone https://github.com/0xLittleSpidy/pyoffline.git
cd pyoffline
```

## Usage 🚀

Basic usage:
```bash
python3 pyoffline.py https://github.com/someuser/cooltool.git
```

Advanced options:
```bash
pyoffline https://github.com/someuser/cooltool.git \
  --platform win_amd64 \  # For Windows
  --keep \               # Keep downloaded files
  --verbose             # Detailed output
```

## Platform Options 🖥️

| Platform Flag            | Description                     |
|--------------------------|---------------------------------|
| `manylinux2014_x86_64`   | Linux 64-bit (default)          |
| `win_amd64`              | Windows 64-bit                  |
| `macosx_10_9_x86_64`     | macOS Intel                     |
| `any`                    | Platform-agnostic wheels        |
| `none`                   | Allow source packages           |

## Example Workflow 📋

1. **Create offline bundle:**
   ```bash
   pyoffline https://github.com/someuser/cooltool.git
   ```
   
2. **Transfer `cooltool.zip` to offline machine**

3. **On offline machine:**
   ```bash
   unzip cooltool.zip
   cd cooltool-master
   pip install --no-index --find-links=./wheels -r requirements.txt
   ```

## Handling Special Cases ⚠️

If you encounter dependency issues:
```bash
# Try allowing source packages
pyoffline https://github.com/... --platform none

# Or platform-agnostic wheels
pyoffline https://github.com/... --platform any
```

## FAQ ❓

**Q: Why am I getting dependency errors?**  
A: Some packages may not have wheels for your platform. Try `--platform any` or `--platform none`.

**Q: Can I use private repositories?**  
A: Currently only public repos are supported. Private repo support is planned.

**Q: How do I install the bundled package offline?**  
A: See the [Example Workflow](#example-workflow) section above.

## Contributing
Contributions are welcome! If you'd like to contribute to this project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request.
---

Created with ❤️ for Pentesters working in restricted environments
