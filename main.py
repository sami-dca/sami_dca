import os
import threading as th

from logging import getLogger
from logging.config import fileConfig

import sami
from sami.threads.events import GlobalStopEvent
from sami.config import logging_conf_file, log_file
from sami.threads import JobsThread, RequestHandlingThread, SenderThread

# Load logging config
fileConfig(logging_conf_file, defaults={'log_file_name': str(log_file)})
logger = getLogger()


def main():
    global_app_stop_event: th.Event = GlobalStopEvent()

    logger.info('Launching')

    # The main thread will be the UI's
    controller = sami.Controller()

    # Define background threads
    request_handling_thread = RequestHandlingThread(global_app_stop_event)
    sender_thread = SenderThread(global_app_stop_event)
    jobs_thread = JobsThread(global_app_stop_event)

    # Start threads
    request_handling_thread.start()
    sender_thread.start()
    jobs_thread.start()

    # Turns the server up on the user interface.
    controller.main_frame.set_server_display(True)

    # Run the UI, holding the application open
    controller.app.MainLoop()

    # Stops all threads
    global_app_stop_event.set()
    request_handling_thread.stop()
    sender_thread.stop()
    jobs_thread.stop()

    # Wait for all threads to finish
    jobs_thread.join()
    sender_thread.join()
    request_handling_thread.join()


def update():
    # Updates the client using Git.
    try:
        import git
        g = git.cmd.Git(os.getcwd())
        g.pull()
    except ImportError:
        logger.warning('Could not check for software updates.')


if __name__ == "__main__":
    main()
