import signal
import time

import sdnotify

n = sdnotify.SystemdNotifier()

if __name__ == '__main__':
    n.notify("WATCHDOG=1")
    time.sleep(2)

