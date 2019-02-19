import os
import subprocess
import sys
from shutil import rmtree

from daemonize import DAEMONS_DIR


def get_pid(path):
    with open(path) as f:
        pid = f.readline()
        yield pid


def kill_pid(pid):
    completed = subprocess.run(f'kill -9 {pid}', shell=True)
    return completed.returncode


def clear_daemons():
    for root, _, files in os.walk(DAEMONS_DIR):
        for f in files:
            path = f'{root}/{f}'
            _, ext = os.path.splitext(path)
            if ext == '.pid':
                for pid in get_pid(path):
                    if kill_pid(pid) == 1:
                        sys.exit(1)
    rmtree(DAEMONS_DIR)
    print('Done ✨')


def main():
    clear_daemons()


if __name__ == '__main__':
    main()
