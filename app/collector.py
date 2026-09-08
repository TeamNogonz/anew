"""One dedicated collector process; never multiply crawlers with API replicas."""

import signal
import threading
import logging
from publisher import core_url, flush_outbox, publish_events
from database import mongodb
from scheduler import NewsScheduler


def main():
    core_url()  # Fail early on missing destination/credential.
    scheduler = NewsScheduler()
    signal.signal(signal.SIGTERM, lambda *_: scheduler.stop_event.set())
    signal.signal(signal.SIGINT, lambda *_: scheduler.stop_event.set())
    mongodb.connect()

    def publish_loop():
        while not scheduler.stop_event.is_set():
            try:
                publish_events(
                    []
                )  # Register choices even before the first news arrives.
                flush_outbox(scheduler.stop_event)
            except Exception as error:
                logging.getLogger(__name__).warning(
                    "publisher_unavailable type=%s", type(error).__name__
                )
            scheduler.stop_event.wait(15)

    publisher = threading.Thread(target=publish_loop, daemon=True)
    publisher.start()
    try:
        scheduler.start_scheduler()
    finally:
        scheduler.stop_scheduler()
        publisher.join(timeout=45)
        mongodb.disconnect()


if __name__ == "__main__":
    main()
