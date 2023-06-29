from time import sleep
from typing import Callable

import numpy as np

from .utils import get_time


class Job:
    def __init__(self, action: Callable[[], None], schedule: int | float):
        self._action = action
        self.schedule = schedule
        self.last_ran = 0

    def action(self):
        """
        Light wrapper around the action,
        setting the ``last_ran`` attribute at the same time.
        """
        # Note: I'm unsure whether last_ran should be updated
        #  before or after the run
        self.last_ran = get_time()
        self._action()

    @property
    def remaining_time(self) -> int:
        return self.schedule - (get_time() - self.last_ran)


class Jobs:
    def __init__(self, *, condition: Callable[[], bool]):
        self.condition = condition
        self._jobs = []

    def register(self, job: Job) -> None:
        self._jobs.append(job)

    def run(self) -> None:
        """
        Runs the jobs synchronously.
        Because of its sequential nature, there might be inconsistencies in the
        execution timings when schedules are short and/or jobs take a while to run.
        """
        # Run all
        for job in self._jobs:
            job.action()
        # Run until condition is not met anymore
        while self.condition() and self._jobs:
            next_job = self._jobs[np.argmin([job.remaining_time for job in self._jobs])]
            remaining_time = next_job.remaining_time
            if remaining_time <= 0:
                next_job.action()
            else:
                sleep(remaining_time)
