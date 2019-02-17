#!/usr/bin/env python3

import os
import click
import netifaces


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


@click.command()
@click.argument('interface', nargs=1)
@click.option('--sshd-config', is_flag=False, default='/etc/ssh/sshd_config')
def check_sshd_config(interface, sshd_config):
    assert interface in netifaces.interfaces()
    assert os.path.getsize(sshd_config) != 0
    listen_address = netifaces.ifaddresses(interface)[2][0]['addr']
    assert listen_address
    ssh_rule = 'ListenAddress ' + listen_address + ':22\n'
    ssh_rule = ssh_rule.encode('utf8')
    write_unique_line_to_file(line=ssh_rule, file_to_write=sshd_config)


if __name__ == '__main__':
    check_sshd_config()
