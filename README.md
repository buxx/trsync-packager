## Windows

If Windows < 11, install winget. Then :

* Install git `winget install git`
* Install Python 3.8 `winget install -e --id Python.Python.3 -v 3.8.10150.0`
* Install build tools `winget install -e --id Microsoft.VisualStudio.2022.BuildTools`
* Install Rust from https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe
* Install InnoSetup from https://jrsoftware.org/isdl.php
* Run make.py script with `python make.py`

Installer is now available in dist/tracim.exe
