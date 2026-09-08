"""One dedicated collector process; never multiply crawlers with API replicas."""

import signal
from database import mongodb
from scheduler import NewsScheduler


def main():
    scheduler = NewsScheduler()
    signal.signal(signal.SIGTERM, lambda *_: scheduler.stop_event.set())
    signal.signal(signal.SIGINT, lambda *_: scheduler.stop_event.set())
    mongodb.connect()
    try:
        scheduler.start_scheduler()
    finally:
        scheduler.stop_scheduler()
        mongodb.disconnect()


if __name__ == "__main__":
    main()
