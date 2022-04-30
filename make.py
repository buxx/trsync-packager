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
    exec("cd trsync && cargo build --release --features windows")

    print("Build trsync-manager ...")
    if not pathlib.Path("trsync-manager").exists():
        exec("git clone https://github.com/buxx/trsync-manager")
    exec("cd trsync-manager && git pull")
    exec("cd trsync-manager && cargo build --release")

    print("Build trsync-manager-systray ...")
    if not pathlib.Path("trsync-manager-systray").exists():
        exec("git clone https://github.com/buxx/trsync-manager-systray")
    exec("cd trsync-manager-systray && git pull")
    exec("cd trsync-manager-systray && cargo build --release")

    print("Build trsync-manager-configure ...")
    if not pathlib.Path("trsync-manager-configure").exists():
        exec("git clone https://github.com/buxx/trsync-manager-configure")
    if not pathlib.Path("trsync-manager-configure\venv").exists():
        exec("cd trsync-manager-configure && python -m venv venv")
    exec("cd trsync-manager-configure && git pull")
    # exec(
    #    "cd trsync-manager-configure && .\venv\Scripts\activate.bat && pip install pip setuptools wheel pyinstaller"
    # )
    # exec(
    #    "cd trsync-manager-configure && .\venv\Scripts\activate.bat && pip install -r requirements.txt"
    # )
    # exec(
    #    "cd trsync-manager-configure && .\venv\Scripts\ctivate.bat && pyinstaller --name configure --onefile run.py"
    # )


if __name__ == "__main__":
    main()
