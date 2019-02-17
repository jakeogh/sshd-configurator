#!/usr/bin/env python3

import os
import sys
#import logging
import netifaces
import atexit
import signal
from time import sleep
#logging.basicConfig(level=logging.DEBUG)

'''
    Parse sshd_config and make sure sshd is configured to start on the
    interface specified in /etc/conf.d/sshd-configurator
'''

def write_unique_line_to_file(line, file_to_write):
    '''
    Write line to file_to_write iff line not in file_to_write.
    '''
    assert isinstance(line, bytes)
    assert line.count(b'\n') == 1
    assert line.endswith(b'\n')
    with open(file_to_write, 'rb+') as fh:
        if line not in fh:
            fh.write(line)


def warn_confd_sshd(logger):
    logger.error("\nERROR: /etc/conf.d/sshd is not configured to depend on sshd-configurator", file=sys.stderr)
    logger.error("ERROR: add rc_need=\"sshd-configurator\" to /etc/conf.d/sshd", file=sys.stderr)
    quit(1)


def warn_confd_sshd_configurator(logger, interface):
    logger.error("\nERROR: /etc/conf.d/sshd-configurator is not configured to depend on", interface, file=sys.stderr)
    logger.error("ERROR: add rc_need=\"net." + interface + "\" to /etc/conf.d/sshd-configurator", file=sys.stderr)
    quit(1)


def warn_confd_sshd_configurator_interface(logger, interface):
    logger.error("\nERROR: SSHD_INTERFACE is not set in /etc/conf.d/sshd-configurator.", file=sys.stderr)
    logger.error("ERROR: add SSHD_INTERFACE=\"" + interface + "\" to /etc/conf.d/sshd-configurator", file=sys.stderr)
    quit(1)


def sshd_configurator_daemon(interface, daemon, sshd_config, logger):
    assert interface in netifaces.interfaces()
    assert os.path.getsize(sshd_config) != 0
    listen_address = netifaces.ifaddresses(interface)[2][0]['addr']
    assert listen_address
    ssh_rule = 'ListenAddress ' + listen_address + ':22\n'
    ssh_rule = ssh_rule.encode('utf8')

    try:
        with open('/etc/conf.d/sshd', 'r') as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != '#', fhr)
            try:
                result = [s for s in fhr if s.startswith('rc_need=')][-1]
            except IndexError:
                warn_confd_sshd(logger=logger)
            else:
                if 'sshd-configurator' not in result:
                    warn_confd_sshd(logger=logger)
    except FileNotFoundError:
        warn_confd_sshd(logger=logger)

    listen_service = "net." + interface
    try:
        with open('/etc/conf.d/sshd-configurator', 'r') as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != '#', fhr)
            try:
                result = [s for s in fhr if s.startswith('rc_need=')][-1]
            except IndexError:
                warn_confd_sshd_configurator(interface=interface, logger=logger)
            else:
                if listen_service not in result:
                    warn_confd_sshd_configurator(interface=interface, logger=logger)
    except FileNotFoundError:
        warn_confd_sshd_configurator(interface=interface, logger=logger)

    try:
        with open('/etc/conf.d/sshd-configurator', 'r') as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != '#', fhr)
            try:
                result = [s for s in fhr if s.startswith("SSHD_INTERFACE=")][-1]
            except IndexError:
                warn_confd_sshd_configurator_interface(interface=interface, logger=logger)
            else:
                if interface not in result:
                    warn_confd_sshd_configurator_interface(interface=interface, logger=logger)
    except FileNotFoundError:
        warn_confd_sshd_configurator_interface(interface=interface, logger=logger)

    try:
        write_unique_line_to_file(line=ssh_rule, file_to_write=sshd_config)
    except PermissionError:
        logger.error("ERROR: Unable to write to", sshd_config, file=sys.stderr)
        logger.error("ERROR: Run \"chattr -i " + sshd_config + "\"", file=sys.stderr)
        quit(1)

    def un_mute(*args):
        command = "chattr -i " + sshd_config
        os.system(command)

    if os.geteuid() == 0:
        #if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
        if daemon:
            command = "chattr +i " + sshd_config
            os.system(command)
            atexit.register(un_mute)
            signal.signal(signal.SIGTERM, un_mute)
            signal.signal(signal.SIGHUP, un_mute)

            while True:
                sleep(1000000)
        else:
            print("sshd appears to be properly configured to use", interface, file=sys.stderr)
            quit(0)



#if __name__ == '__main__':
#    sshd_configurator()
