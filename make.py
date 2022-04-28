from codecs import ignore_errors
import subprocess
import sys

def exec(command: str) -> None:
    print(subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode(errors="ignore"))


def main():
    exec("dir C:")


if __name__ == "__main__":
    main()
