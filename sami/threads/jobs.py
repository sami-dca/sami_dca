from ._base import BaseThread
from ..design import Jobs, Job
from ..network import Networks
from ..config import broadcast_schedule, nodes_discovery_schedule, \
    contact_discovery_schedule


class JobsThread(BaseThread):
    """
    Thread handling synchronous jobs.
    """

    def run(self):
        networks: Networks = Networks()
        networks.map(lambda net: net.what_is_up())

        j = Jobs(jobs=[
            Job(
                action=lambda: networks.map(lambda net: net.broadcast_autodiscover),
                sch=broadcast_schedule,
            ),
            Job(
                action=lambda: networks.map(lambda net: net.request_nodes),
                sch=nodes_discovery_schedule,
            ),
            Job(
                action=lambda: networks.map(lambda net: net.request_contacts),
                sch=contact_discovery_schedule,
            ),
        ], stop_event=self.global_app_stop_event)
        j.run()
