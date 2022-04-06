#!/usr/bin/env python3

import logging
import os
import sys
from pathlib import Path
# import atexit
# import signal
from time import sleep
from typing import Union

import netifaces
from eprint import eprint
from pathtool import comment_out_line_in_file
from pathtool import write_line_to_file

# logging.basicConfig(level=logging.DEBUG)

"""
    Parse sshd_config and make sure sshd is configured to start on the
    interface specified in /etc/conf.d/sshd-configurator
"""


def sshd_configurator_daemon(
    interface: str,
    daemon: bool,
    sshd_config: Path,
    logger: logging.Logger,
    verbose: Union[bool, int, float],
):
    assert interface in netifaces.interfaces()
    assert os.path.getsize(sshd_config) != 0
    listen_address = netifaces.ifaddresses(interface)[2][0]["addr"]
    assert listen_address
    ssh_rule = "ListenAddress " + listen_address + ":22\n"
    ssh_rule = ssh_rule.encode("utf8")

    try:
        write_line_to_file(
            line=ssh_rule, path=sshd_config, unique=True, verbose=verbose
        )
    except PermissionError:
        logger.error(
            f"ERROR: Unable to write {repr(ssh_rule)} to {sshd_config.as_posix()}"
        )
        logger.error(f'ERROR: Run "chattr -i {sshd_config.as_posix()} "')
        sys.exit(1)

    comment_out_line_in_file(line="UsePAM yes", path=sshd_config, verbose=verbose)

    ssh_rule = "UsePAM no\n".encode("utf8")
    try:
        write_line_to_file(
            line=ssh_rule, path=sshd_config, unique=True, verbose=verbose
        )
    except PermissionError:
        logger.error(
            f"ERROR: Unable to write {repr(ssh_rule)} to {sshd_config.as_posix()}"
        )
        logger.error(f'ERROR: Run "chattr -i {sshd_config.as_posix()} "')
        sys.exit(1)

    # def un_mute(*args):
    #    command = "chattr -i " + sshd_config
    #    os.system(command)

    if os.geteuid() == 0:
        # if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
        if daemon:
            # command = "chattr +i " + sshd_config
            # os.system(command)
            # atexit.register(un_mute)
            # signal.signal(signal.SIGTERM, un_mute)
            # signal.signal(signal.SIGHUP, un_mute)

            while True:
                sleep(1000000)
        else:
            eprint(
                "sshd appears to be properly configured to use",
                interface,
            )
            sys.exit(0)
