#!/usr/bin/env python3

import os
import sys
import click
import netifaces

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


def warn_confd_sshd():
    print("\nWARNING: /etc/conf.d/sshd is not configured to depend on sshd-configurator", file=sys.stderr)
    print("WARNING: add rc_need=\"sshd-configurator\" to /etc/conf.d/sshd", file=sys.stderr)


def warn_confd_sshd_configurator(interface):
    print("\nWARNING: /etc/conf.d/sshd-configurator is not configured to depend on", interface, file=sys.stderr)
    print("WARNING: add rc_need=\"net." + interface + "\" to /etc/conf.d/sshd-configurator", file=sys.stderr)


def warn_confd_sshd_configurator_interface(interface):
    print("\nWARNING: SSHD_INTERFACE is not set in /etc/conf.d/sshd-configurator.", file=sys.stderr)
    print("WARNING: add SSHD_INTERFACE=\"" + interface + "\" to /etc/conf.d/sshd-configurator", file=sys.stderr)


@click.command()
@click.argument('interface', nargs=1)
@click.option('--sshd-config', is_flag=False, default='/etc/ssh/sshd_config')
def sshd_configurator(interface, sshd_config):
    assert interface in netifaces.interfaces()
    assert os.path.getsize(sshd_config) != 0
    listen_address = netifaces.ifaddresses(interface)[2][0]['addr']
    assert listen_address
    ssh_rule = 'ListenAddress ' + listen_address + ':22\n'
    ssh_rule = ssh_rule.encode('utf8')
    write_unique_line_to_file(line=ssh_rule, file_to_write=sshd_config)
    try:
        with open('/etc/conf.d/sshd', 'r') as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != '#', fhr)
            try:
                result = [s for s in fhr if "sshd-configurator" in s][-1]
            except IndexError:
                warn_confd_sshd()
            else:
                if not result.startswith("rc_need="):
                    warn_confd_sshd()
    except FileNotFoundError:
        warn_confd_sshd()

    listen_service = "net." + interface
    try:
        with open('/etc/conf.d/sshd-configurator', 'r') as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != '#', fhr)
            try:
                result = [s for s in fhr if 'rc_need=' in s][-1]
            except IndexError:
                warn_confd_sshd_configurator(interface)
            else:
                if not listen_service result:
                    warn_confd_sshd_configurator(interface)
    except FileNotFoundError:
        warn_confd_sshd_configurator(interface)

    try:
        with open('/etc/conf.d/sshd-configurator', 'r') as fh:
            fhr = filter(None, (line.strip() for line in fh))
            fhr = filter(lambda row: row[0] != '#', fhr)
            try:
                result = [s for s in fhr if "SSHD_INTERFACE=" in s][-1]
            except IndexError:
                warn_confd_sshd_configurator_interface(interface)
            else:
                if not interface in result):
                    warn_confd_sshd_configurator_interface(interface)
    except FileNotFoundError:
        warn_confd_sshd_configurator_interface(interface)

if __name__ == '__main__':
    sshd_configurator()
