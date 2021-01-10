# -*- coding: UTF8 -*-

"""
This is a synchronous job system.
"""

import time

from typing import List

from .config import Config


class Job:

    def __init__(self, action, sch: int):
        self.default_schedule = sch
        self.remaining_time = sch
        self.action = action

    def __sub__(self, val: int) -> int:
        return self.remaining_time - val

    def __isub__(self, val: int) -> int:
        self.remaining_time -= val
        return self.remaining_time

    def run_action(self) -> None:
        self.action()

    def reset(self) -> None:
        self.remaining_time = self.default_schedule


class Jobs:

    def __init__(self, jobs: List[Job], stop_event):
        self.jobs = jobs
        self.stop_event = stop_event

    def run(self) -> None:
        stop_delay = Config.multiprocessing_stop_delay
        while not self.stop_event.wait(stop_delay):
            self.jobs.sort(key=lambda x: x.remaining_time)
            next_job = self.jobs[0]
            to_wait = stop_delay if stop_delay < next_job.remaining_time else next_job.remaining_time
            for job in self.jobs:
                job -= to_wait
            if next_job.remaining_time <= 0:
                next_job.run_action()
                next_job.reset()
