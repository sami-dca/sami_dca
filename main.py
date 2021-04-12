# -*- coding: UTF8 -*-

import os
import sys
import logging

import threading as th

import sami


def set_logging(func):
    def wrapper(*args, **kwargs):
        logging_level = logging.DEBUG

        logger = logging.getLogger()
        logger.setLevel(logging_level)

        formatter = logging.Formatter('%(asctime)s - [%(levelname)s | %(module)s] %(message)s')
        formatter.datefmt = '%m/%d/%Y %H:%M:%S'

        # fh = logging.FileHandler(filename='C:/Temp/sami/sami.log', mode='w')
        # fh.setLevel(logging_level)
        # h.setFormatter(formatter)

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging_level)
        sh.setFormatter(formatter)

        # logger.addHandler(fh)
        logger.addHandler(sh)

        return func(*args, **kwargs)
    return wrapper


def manage_jobs(network, stop_event):
    network.what_is_up()
    new_jobs = [
        (network.broadcast_autodiscover, sami.Config.broadcast_schedule),
        (network.request_nodes, sami.Config.nodes_discovery_schedule),
        (network.request_contacts, sami.Config.contact_discovery_schedule),
    ]
    # Takes care of loading the above data into Job objects.
    j = sami.Jobs([sami.Job(*args) for args in new_jobs], stop_event)
    j.run_all()
    j.run()


def manage_requests(network, stop_event):
    network.listen_for_requests(stop_event)  # TODO: Listen on all interfaces (LMAO)


def manage_broadcast(network, stop_event) -> None:
    network.listen_for_autodiscover_packets(stop_event)


@set_logging
def main():
    global stop_event

    def stop(nw: sami.Network):
        stop_event.set()
        nw.send_dummy_data_to_self()

    logging.info('Launching')

    databases = sami.Databases()
    master_node = sami.MasterNode()
    master_node.set_databases(databases)
    network = sami.Network(master_node)
    controller = sami.Controller(master_node, network)

    req_process = th.Thread(target=manage_requests, args=(network, stop_event), daemon=True)
    broadcast_process = th.Thread(target=manage_broadcast, args=(network, stop_event), daemon=True)
    jobs_process = th.Thread(target=manage_jobs, args=(network, stop_event), daemon=False)

    req_process.start()
    logging.debug("'req' process started")
    broadcast_process.start()
    logging.debug("'broadcast' process started")
    jobs_process.start()
    logging.debug("'jobs' process started")

    # Turns the server up on the user interface.
    controller.main_frame.set_server_display(True)

    controller.app.MainLoop()

    # Close the network process
    stop(network)

    req_process.join()
    logging.debug("'req' process stopped")
    broadcast_process.join()
    logging.debug("'broadcast' process stopped")
    jobs_process.join()
    logging.debug("'jobs' process stopped")


def update():
    # Updates the client using Git.
    try:
        import git
        g = git.cmd.Git(os.getcwd())
        g.pull()
    except ImportError:
        logging.warning('Could not check for updates.')


if __name__ == "__main__":
    # Create a new event, that will be used to stop all child processes.
    # Needs to be a global variable.
    stop_event = th.Event()

    main()
