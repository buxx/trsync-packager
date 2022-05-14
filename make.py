from codecs import ignore_errors
import pathlib
import subprocess
import sys


def exec(command: str) -> None:
    process = subprocess.run(command, stderr=subprocess.PIPE, shell=True)
    if process.stdout:
        print(process.stdout.decode(errors="ignore"))
    if process.stderr:
        print(process.stderr.decode(errors="ignore"))
    if process.returncode:
        exit(process.returncode)


def main():
    print("Build trsync ...")
    if not pathlib.Path("trsync").exists():
        exec("git clone https://github.com/buxx/trsync")
    exec("cd trsync && git pull")
    exec(
        "cd trsync && cargo build --release --features windows --bin trsync_manager_systray"
    )

    print("Build trsync-manager-configure ...")
    if not pathlib.Path("trsync-manager-configure").exists():
        exec("git clone https://github.com/buxx/trsync-manager-configure")
    if not pathlib.Path("trsync-manager-configure\venv").exists():
        exec("cd trsync-manager-configure && python -m venv venv")
    exec("cd trsync-manager-configure && git pull")
    exec(
        r"cd trsync-manager-configure && .\venv\Scripts\activate.bat && pip install pip setuptools wheel pyinstaller"
    )
    exec(
        r"cd trsync-manager-configure && .\venv\Scripts\activate.bat && pip install -r requirements.txt"
    )
    exec(
        r"cd trsync-manager-configure && .\venv\Scripts\activate.bat && pyinstaller --name configure --onefile run.py"
    )


if __name__ == "__main__":
    main()
