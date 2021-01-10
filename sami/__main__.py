# -*- coding: UTF8 -*-

import os
import sys
import signal
import logging

import multiprocessing as mp

import sami


def manage_jobs(network, stop_event):
    new_jobs = [
        (network.broadcast_autodiscover, sami.Config.broadcast_schedule),
        (network.request_nodes, sami.Config.nodes_discovery_schedule),
        (network.request_contacts, sami.Config.contact_discovery_schedule),
    ]
    # Takes care of loading the above data into Job objects.
    j = sami.Jobs([sami.Job(*args) for args in new_jobs], stop_event)
    j.run()


def manage_requests(network, stop_event):
    network.listen_for_requests(stop_event)


def manage_broadcast(network, stop_event) -> None:
    network.listen_for_autodiscover_packets(stop_event)


def start_server(network, stop_event) -> None:
    # network.what_is_up()

    req_process = mp.Process(target=manage_requests, args=(network, stop_event))
    broadcast_process = mp.Process(target=manage_broadcast, args=(network, stop_event))
    jobs_process = mp.Process(target=manage_jobs, args=(network, stop_event))

    req_process.start()
    broadcast_process.start()
    jobs_process.start()

    req_process.start()
    broadcast_process.start()
    jobs_process.join()


def main():
    global stop_event

    def stop(nw: sami.Network):
        stop_event.set()
        nw.connect_and_send_dummy_data_to_self()

    logging.info('Launching')
    databases = sami.Databases()
    master_node = sami.MasterNode()
    master_node.set_databases(databases)
    network = sami.Network(master_node)
    controller = sami.Controller(master_node, network)

    network_process = mp.Process(target=start_server, args=(network, stop_event))
    network_process.start()
    # Turns the server up on the user interface.
    controller.main_frame.set_server_display(True)

    controller.app.MainLoop()

    # Close the network process

    stop(network)

    network_process.terminate()
    network_process.join()
    network_process.close()


def update():
    # Updates the client using Git.
    try:
        import git
        g = git.cmd.Git(os.getcwd())
        g.pull()
    except ImportError:
        logging.warning('Could not check for updates.')


###########
# Logging #
###########


# handlers = [
#    logging.FileHandler(filename='C:/Temp/sami.log', mode='r+'),
#    logging.StreamHandler(sys.stdout),
# ]

logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] %(message)s',  # We add a timestamp and the status to each log entries.
    level=logging.INFO,
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename="sami.log",
    filemode="r+",
)


if __name__ == "__main__":
    # Create a new event, that will be used to stop all child processes.
    # Needs to be a global variable.
    stop_event = mp.Event()

    main()
