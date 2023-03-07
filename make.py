import argparse
from codecs import ignore_errors
import configparser
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import enum


class System(enum.Enum):
    Windows = 1
    Linux = 2
    Mac = 3


def exec(command: str, log_file_path: pathlib.Path) -> None:
    with log_file_path.open("w+") as log_file:
        process = subprocess.run(command, stdout=log_file, stderr=log_file, shell=True)
        if process.stdout:
            print(process.stdout.decode(errors="ignore"))
        if process.stderr:
            print(process.stderr.decode(errors="ignore"))
        if process.returncode:
            print(
                f"Error while executing command: '{command}', please read '{log_file_path}' log file"
            )
            exit(process.returncode)


def main():
    parser = argparse.ArgumentParser(description="Install Trsync or package it")
    parser.add_argument(
        "--build-installer",
        action="store_true",
        help="Build installer (with InnoSetup for Windows)",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install on the system after build",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="log file path",
        default="make.log",
    )
    parser.add_argument(
        "--working-directory",
        type=str,
        help="path where place source code and output files",
        default=".",
    )
    parser.add_argument(
        "--python-bin",
        type=str,
        default="python3",
    )
    parser.add_argument(
        "--startup-config-path",
        type=str,
        default="~/.config/autostart",
    )
    parser.add_argument(
        "--bin-path",
        type=str,
        default="~/bin",
    )
    parser.add_argument(
        "--install-startup",
        action="store_true",
        help="Enable startup application for current user",
    )
    parser.add_argument(
        "--install-entry",
        action="store_true",
        help="Install TrSync desktop entry",
    )
    parser.add_argument(
        "--replace-config-if-exist",
        action="store_true",
    )
    parser.add_argument(
        "--desktop-entry-dir-path",
        type=str,
        default="~/.local/share/applications",
    )
    parser.add_argument(
        "--user-icons-dir-path",
        type=str,
        default="~/.local/share/icons",
    )
    args = parser.parse_args()

    system_ = platform.system()
    if system_ == "Linux":
        system = System.Linux
    # elif system_ == 'Darwin':
    #     system = System.Mac
    elif system_ == "Windows":
        system = System.Windows
    else:
        print("Unsupported system: {system_}")
        exit(1)

    log_file_path = pathlib.Path(args.log_file).expanduser()
    working_directory = pathlib.Path(args.working_directory).expanduser()
    print(f"Logs available at: '{log_file_path}'")
    print(f"Working directory: '{working_directory}'")

    if not pathlib.Path("trsync").exists():
        print("Clone trsync sources ...")
        exec(
            f"cd {working_directory} && git clone https://github.com/buxx/trsync",
            log_file_path,
        )

    print("Pull latest trsync source code version ...")
    exec(f"cd {working_directory / 'trsync'} && git pull", log_file_path)

    print("Build trsync-manager-systray binary ...")
    extra_args = "--features windows" if system == System.Windows else ""
    exec(
        f"cd {working_directory / 'trsync'} && "
        f"cargo build --release {extra_args} --bin trsync_manager_systray",
        log_file_path,
    )

    bin_path = pathlib.Path(args.bin_path).expanduser()
    trsync_manager_systray_bin_path = pathlib.Path(bin_path) / "trsync-manager-systray"
    icons_path = pathlib.Path(args.user_icons_dir_path).expanduser()

    if args.build_installer:
        if system.Windows:
            print("Build installer with InnoSetup ...")
            # TODO : Solve PATH problem to permit use ISCC.exe without absolute url
            exec(
                '"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss',
                log_file_path,
            )
        else:
            print(
                f"Operation (--build-installer) not supported on this system ('{system.name}')"
            )
            exit(1)
    if args.install:
        if system == System.Linux:
            bin_path.mkdir(parents=True, exist_ok=True)
            ext = ".exe" if system == System.Windows else ""
            print(
                f"Install trsync-manager-systray binary at '{trsync_manager_systray_bin_path}' ..."
            )
            shutil.copy(
                pathlib.Path(f"trsync/target/release/trsync_manager_systray{ext}"),
                trsync_manager_systray_bin_path,
            )

            trsync_manager_config_path = pathlib.Path.home() / ".trsync.conf"
            if not trsync_manager_config_path.exists() or args.replace_config_if_exist:
                message_prefix = (
                    "Create" if not trsync_manager_config_path.exists() else "Replace"
                )
                print(
                    f"{message_prefix} default config file at '{trsync_manager_config_path}' ..."
                )
                config_content = pathlib.Path("trsync.conf").read_text()
                config_content += f"icons_path = {icons_path}\n"
                if (
                    not trsync_manager_config_path.exists()
                    or args.replace_config_if_exist
                ):
                    trsync_manager_config_path.write_text(config_content)
            else:
                print(
                    f"Config file '{trsync_manager_config_path}' already exist, update it if required"
                )
                config = configparser.ConfigParser()
                config.read(trsync_manager_config_path)
                if config.get("server", "icons_path", fallback=None) is None:
                    config.set("server", "icons_path", str(icons_path))
                    with trsync_manager_config_path.open("w") as f:
                        config.write(f)

            print(f"Install icons at '{icons_path}' ...")
            icons_path.mkdir(parents=True, exist_ok=True)
            for icon_path in pathlib.Path("trsync/systray").glob("trsync*.png"):
                shutil.copy(icon_path, icons_path)

        else:
            print(
                f"Operation (--install) not supported on this system ('{system.name}')"
            )
            exit(1)

    if args.install_startup:
        if system == System.Linux:
            # FIXME : check compatibility with current OS
            startup_config_path = pathlib.Path(args.startup_config_path).expanduser()
            startup_config_path.mkdir(parents=True, exist_ok=True)
            startup_script_path = startup_config_path / "trsync-manager-systray.desktop"
            print(f"Install startup script at '{startup_script_path}' ...")
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            script_content = pathlib.Path("startup.desktop").read_text()
            script_content = script_content.replace(
                "__EXE_FILE_PATH__", str(trsync_manager_systray_bin_path)
            )
            startup_script_path.write_text(script_content)
        else:
            print(
                f"Operation (--install-startup) not supported on this system ('{system.name}')"
            )
            exit(1)

    if args.install_entry:
        if system == System.Linux:
            desktop_entry_dir_path = (
                pathlib.Path(args.desktop_entry_dir_path).expanduser()
                / "trsync.desktop"
            )

            print(f"Install desktop entry at '{desktop_entry_dir_path}' ...")
            desktop_entry_dir_path.parent.mkdir(parents=True, exist_ok=True)
            script_content = pathlib.Path("entry.desktop").read_text()
            script_content = script_content.replace(
                # TODO
                "__VERSION__",
                "0.1",
            )
            script_content = script_content.replace(
                "__EXEC_PATH__",
                str(trsync_manager_systray_bin_path),
            )
            script_content = script_content.replace(
                "__ICON_PATH__", str(icons_path / "trsync.png")
            )
            desktop_entry_dir_path.write_text(script_content)

        else:
            print(
                f"Operation (--install-entry) not supported on this system ('{system.name}')"
            )
            exit(1)

    print("Finished successfully")


if __name__ == "__main__":
    main()
