# TrSync packager/installation tool

## Requirements

### GNU/Linux

Python >= 3.8, Rust >= 1.56.0 and some libs (install example for debian likes) :

    apt-get install build-essential pkg-config libssl-dev libsqlite3-dev libpango1.0-dev libgtk-3-dev

### Windows

If Windows < 11, install winget.

Then :

* Install git `winget install git`
* Install Python 3.8 `winget install -e --id Python.Python.3 -v 3.8.10150.0`
* Install build tools `winget install -e --id Microsoft.VisualStudio.2022.BuildTools`
* Install Rust from https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe
* Install InnoSetup from https://jrsoftware.org/isdl.php

## Usage

### Build installer

*Note : Available for Windows only*

    python3 make.py --build-installer

Installer is now available at `dist/tracim.exe`

### Install

*Note : Available for GNLU/Linux only*

    python3 make.py --install --install-startup --install-entry

Note :

 * `--install-startup` is optional (setup TrSync as startup application for current user)
 * `--install-entry` is optional (setup TrSync as desktop application for current user)
