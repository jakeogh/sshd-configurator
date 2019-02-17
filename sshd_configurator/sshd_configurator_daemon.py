#!/usr/bin/env python3

import os
import sys
#import logging
import netifaces
#import atexit
#import signal
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


def sshd_configurator_daemon(interface, daemon, sshd_config, logger):
    assert interface in netifaces.interfaces()
    assert os.path.getsize(sshd_config) != 0
    listen_address = netifaces.ifaddresses(interface)[2][0]['addr']
    assert listen_address
    ssh_rule = 'ListenAddress ' + listen_address + ':22\n'
    ssh_rule = ssh_rule.encode('utf8')

    try:
        write_unique_line_to_file(line=ssh_rule, file_to_write=sshd_config)
    except PermissionError:
        logger.error("ERROR: Unable to write to", sshd_config)
        logger.error("ERROR: Run \"chattr -i " + sshd_config + "\"")
        quit(1)

    #def un_mute(*args):
    #    command = "chattr -i " + sshd_config
    #    os.system(command)

    if os.geteuid() == 0:
        #if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
        if daemon:
            #command = "chattr +i " + sshd_config
            #os.system(command)
            #atexit.register(un_mute)
            #signal.signal(signal.SIGTERM, un_mute)
            #signal.signal(signal.SIGHUP, un_mute)

            while True:
                sleep(1000000)
        else:
            print("sshd appears to be properly configured to use", interface, file=sys.stderr)
            quit(0)
