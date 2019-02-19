import asyncio
import os
import time
from threading import current_thread

from daemon import DaemonContext
from daemon.pidfile import PIDLockFile

DAEMONS_DIR = os.path.join(os.getcwd(), 'daemons')


def start_daemon(i: int):
    path = os.path.join(DAEMONS_DIR, str(i))
    if not os.path.exists(path):
        os.makedirs(path)
    pid_path = os.path.join(path, f'daemon_{i}.pid')
    lockfile = PIDLockFile(pid_path)
    daemon_log_path = os.path.join(path, f'daemon_{i}.log')
    logio = open(daemon_log_path, 'w')

    with DaemonContext(
            detach_process=True,
            stdout=logio,
            stderr=logio,
            pidfile=lockfile):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tick_time())


async def tick_time():
    while True:
        print(f'({os.getpid()}-{current_thread().name})'
              f' time:{time.time()}')
        await asyncio.sleep(1)
