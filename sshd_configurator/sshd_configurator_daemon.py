#!/usr/bin/env python3

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from time import sleep

import netifaces
from eprint import eprint
from pathtool import comment_out_line_in_file
from pathtool import write_line_to_file

# import atexit
# import signal
# logging.basicConfig(level=logging.DEBUG)

"""
    Parse sshd_config and make sure sshd is configured to start on the
    interface specified in /etc/conf.d/sshd-configurator
"""


def write_sshd_rule(
    *,
    rule: bytes,
    sshd_config: Path,
    logger: logging.Logger,
    verbose: bool | int | float,
):
    try:
        write_line_to_file(line=rule, path=sshd_config, unique=True, verbose=verbose)
    except PermissionError:
        logger.error(f"ERROR: Unable to write {repr(rule)} to {sshd_config.as_posix()}")
        logger.error(f'ERROR: Run "chattr -i {sshd_config.as_posix()} "')
        sys.exit(1)


def sshd_configurator_daemon(
    interface: str,
    daemon: bool,
    sshd_config: Path,
    logger: logging.Logger,
    verbose: bool | int | float,
):
    assert interface in netifaces.interfaces()
    assert os.path.getsize(sshd_config) != 0
    listen_address = netifaces.ifaddresses(interface)[2][0]["addr"]
    assert listen_address
    sshd_rule = "ListenAddress " + listen_address + ":22\n"
    sshd_rule = sshd_rule.encode("utf8")
    write_sshd_rule(
        rule=sshd_rule, sshd_config=sshd_config, logger=logger, verbose=verbose
    )
    comment_out_line_in_file(line="UsePAM yes", path=sshd_config, verbose=verbose)
    sshd_rule = "UsePAM no\n".encode("utf8")
    write_sshd_rule(
        rule=sshd_rule, sshd_config=sshd_config, logger=logger, verbose=verbose
    )

    sshd_rule = "PermitRootLogin no"
    comment_out_line_in_file(line=sshd_rule, path=sshd_config, verbose=verbose)

    sshd_rule = "PermitRootLogin yes\n".encode("utf8")
    write_sshd_rule(
        rule=sshd_rule, sshd_config=sshd_config, logger=logger, verbose=verbose
    )

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
