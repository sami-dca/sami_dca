from ..jobs import Jobs
from ._base import BaseThread


class JobsThread(BaseThread):

    """
    Background thread handling jobs.

    Example
    -------
    Instanciate the thread

    >>> jobs_thread = JobsThread()

    Register jobs in

    >>> jobs_thread.jobs.register(...)

    Run the thread, launching the jobs in the background

    >>> jobs_thread.start()

    Jobs can also be added after the start

    >>> jobs_thread.jobs.register(...)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jobs = Jobs(condition=lambda: self.running)

    def run(self):
        self.jobs.run()  # Blocking
