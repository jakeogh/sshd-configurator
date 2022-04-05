#!/usr/bin/env python3
# pylint: disable=R0903  # too few public methods

import logging
import sys

import attr
import click
from daemonize import Daemonize

from .sshd_configurator_daemon import sshd_configurator_daemon


def warn_confd_sshd(logger):
    logger.error(
        "\nERROR: /etc/conf.d/sshd is not configured to depend on sshd-configurator"
    )
    logger.error('ERROR: add rc_need="sshd-configurator" to /etc/conf.d/sshd')
    sys.exit(1)


def warn_confd_sshd_configurator(logger, interface):
    logger.error(
        "\nERROR: /etc/conf.d/sshd-configurator is not configured to depend on",
        interface,
    )
    logger.error(
        'ERROR: add rc_need="net.' + interface + '" to /etc/conf.d/sshd-configurator'
    )
    sys.exit(1)


def warn_confd_sshd_configurator_interface(logger, interface):
    logger.error("\nERROR: SSHD_INTERFACE is not set in /etc/conf.d/sshd-configurator.")
    logger.error(
        'ERROR: add SSHD_INTERFACE="' + interface + '" to /etc/conf.d/sshd-configurator'
    )
    sys.exit(1)


def run_checks(interface, logger):
    try:
        with open("/etc/conf.d/sshd", "r", encoding="utf8") as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != "#", fhr)
            try:
                result = [s for s in fhr if s.startswith("rc_need=")][-1]
            except IndexError:
                warn_confd_sshd(logger=logger)
            else:
                if "sshd-configurator" not in result:
                    warn_confd_sshd(logger=logger)
    except FileNotFoundError:
        warn_confd_sshd(logger=logger)

    listen_service = "net." + interface
    try:
        with open("/etc/conf.d/sshd-configurator", "r", encoding="utf8") as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != "#", fhr)
            try:
                result = [s for s in fhr if s.startswith("rc_need=")][-1]
            except IndexError:
                warn_confd_sshd_configurator(interface=interface, logger=logger)
            else:
                if listen_service not in result:
                    warn_confd_sshd_configurator(interface=interface, logger=logger)
    except FileNotFoundError:
        warn_confd_sshd_configurator(interface=interface, logger=logger)

    try:
        with open("/etc/conf.d/sshd-configurator", "r", encoding="utf8") as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != "#", fhr)
            try:
                result = [s for s in fhr if s.startswith("SSHD_INTERFACE=")][-1]
            except IndexError:
                warn_confd_sshd_configurator_interface(
                    interface=interface, logger=logger
                )
            else:
                if interface not in result:
                    warn_confd_sshd_configurator_interface(
                        interface=interface, logger=logger
                    )
    except FileNotFoundError:
        warn_confd_sshd_configurator_interface(interface=interface, logger=logger)


@attr.s(auto_attribs=True)
class SSHD_CONFIGURATOR:
    interface: str
    daemon: bool
    sshd_config: str
    logger: logging.Logger

    def run(self):
        print("run")
        print("self.logger:", self.logger)
        sshd_configurator_daemon(
            interface=self.interface,
            daemon=self.daemon,
            sshd_config=self.sshd_config,
            logger=self.logger,
        )


@click.command()
@click.argument("interface", nargs=1)
@click.option("--daemon", is_flag=True)
@click.option("--sshd-config-file", is_flag=False, default="/etc/ssh/sshd_config")
def sshd_configurator(interface, daemon, sshd_config_file):
    pidfile = "/run/sshd-configurator.pid"
    log = logging.getLogger(__name__)
    run_checks(interface=interface, logger=log)
    # logger.setLevel(logging.DEBUG)
    # logger.propagate = False
    lfh = logging.StreamHandler()
    lfh.setLevel(logging.DEBUG)
    log.addHandler(lfh)
    keep_fds = [lfh.stream.fileno()]

    foreground = not daemon
    sshd_configurator_obj = SSHD_CONFIGURATOR(
        interface=interface, daemon=daemon, sshd_config=sshd_config_file, logger=log
    )
    daemon = Daemonize(
        app="ssh_configurator",
        pid=pidfile,
        action=sshd_configurator_obj.run,
        foreground=foreground,
        keep_fds=keep_fds,
    )
    daemon.start()


if __name__ == "__main__":
    sshd_configurator()
