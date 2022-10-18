"""
Script for running a Sami beacon.
"""

import threading as th

from logging import getLogger
from logging.config import fileConfig

import sami  # noqa
from sami.threads.events import GlobalStopEvent
from sami.config import settings
from sami.threads import JobsThread, RequestHandlingThread, SenderThread

# Load logging config
fileConfig(
    settings.logging_conf_file, defaults={"log_file_name": str(settings.log_file)}
)
logger = getLogger()


def main():
    global_app_stop_event: th.Event = GlobalStopEvent()

    logger.info("Launching")

    # Define background threads
    request_handling_thread = RequestHandlingThread(global_app_stop_event)
    sender_thread = SenderThread(global_app_stop_event)
    jobs_thread = JobsThread(global_app_stop_event)

    # Start threads
    request_handling_thread.start()
    sender_thread.start()
    jobs_thread.start()

    # Idle
    # TODO

    # Stops all threads
    global_app_stop_event.set()
    request_handling_thread.stop()
    sender_thread.stop()
    jobs_thread.stop()

    # Wait for all threads to finish
    jobs_thread.join()
    sender_thread.join()
    request_handling_thread.join()


if __name__ == "__main__":
    main()
