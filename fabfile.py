from fabric import Connection
from invoke import Responder
from fabric import task
#from patchwork.files import append
import json
import uuid

import os
import logging

logging.raiseExceptions=False

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from config import (NEW_PASSWORD,
                    NEW_USERNAME,
                    NEW_HOSTNAME,
                    ORIGINAL_HOSTNAME,
                    ORIGINAL_PASSWORD,
                    ORIGINAL_USERNAME,
                    ACCESS_IP
                    )

original_host = ACCESS_IP if ACCESS_IP is not None else "%s.local" % ORIGINAL_HOSTNAME
new_host = ACCESS_IP if ACCESS_IP is not None else "%s.local" % NEW_HOSTNAME

pi_cxn = Connection(host=original_host,
                 user=ORIGINAL_USERNAME,
                 connect_kwargs={"password": ORIGINAL_PASSWORD},
                 port=22)

@task
def prepare_omxplayer_sync(junk):
    cert_cxn = pi_cxn
    install_omxplayer_sync(cert_cxn)

@task
def prepare(junk):
    """
    Prepares the base image
    """


    #create_new_user(pi_cxn)

    # new_user_cxn = Connection(host=original_host,
    #                  user=NEW_USERNAME,
    #                  connect_kwargs={"password": NEW_PASSWORD},
    #                  port=22)

    cert_cxn = pi_cxn

    install_pip(cert_cxn)
    install_extra_libs(cert_cxn)

    remove_bloat(cert_cxn)

    configure_rsyslog(cert_cxn)
    #daily_reboot(cert_cxn)

    cert_cxn.sudo('reboot now')


@task
def finish(junk, mode="prod"):

    cert_cxn = pi_cxn

    update_boot_config(cert_cxn, screen)

    if mode == "prod":
        reduce_writes(cert_cxn)
    else:
        install_samba(cert_cxn)

    #set_ssh_config(cert_cxn, mode)

    #delete_old_user(cert_cxn)
    # add_bootstrap(cert_cxn)
    # cert_cxn.sudo("sudo python3 /opt/ishiki/bootstrap/clean_wifi.py")
    set_hostname(cert_cxn)
    cert_cxn.sudo('shutdown now')

def delete_old_user(cxn):
    cxn.sudo("deluser %s" % ORIGINAL_USERNAME)


def create_new_user(cxn):

    sudopass = Responder(pattern=r'UNIX password:',
                         response='%s\n' % NEW_PASSWORD)

    accept = Responder(pattern=r'\[\]:',
                         response='\n')

    yes = Responder(pattern=r'\[Y/n\]',
                         response='\n')

    cxn.sudo("adduser %s" % NEW_USERNAME, pty=True, watchers=[sudopass, accept, yes])

    # make sudo
    cxn.sudo("usermod -aG sudo %s" % NEW_USERNAME)

    # sudo without password
    append_text(cxn, "/etc/sudoers.d/%s-nopasswd" % NEW_USERNAME, "%s ALL=(ALL) NOPASSWD:ALL" % NEW_USERNAME)

    cxn.sudo("sudo chmod 644 /etc/sudoers.d/%s-nopasswd" % NEW_USERNAME)

def append_text(cxn, file_path, text):
    cxn.sudo('echo "%s" | sudo tee -a %s' % (text, file_path))


def command_in_dir(cxn, command, dir):
    cxn.sudo('sh -c "cd %s; %s"' % (dir, command))

def configure_rsyslog(cxn):
    _add_config_file(cxn, "rsyslog.conf", "/etc/rsyslog.conf", "root", chmod="644")


def daily_reboot(cxn):
    append_text(cxn, "/etc/crontab", "0 4    * * *   root    /sbin/shutdown -r +5")

def set_ssh_config(cxn, mode):
    if mode == "dev":
        _add_config_file(cxn, "sshd_config_dev", "/etc/ssh/sshd_config", "root", chmod="600")
    else:
        _add_config_file(cxn, "sshd_config", "/etc/ssh/sshd_config", "root", chmod="600")
    cxn.sudo("systemctl restart ssh")


def install_pip(cxn):
    cxn.sudo("apt-get update")
    cxn.sudo("apt-get install -y curl python3-distutils python3-testresources")
    cxn.sudo("curl https://bootstrap.pypa.io/get-pip.py | sudo python3")
    #cxn.sudo("curl --silent --show-error --retry 5 https://bootstrap.pypa.io/" "get-pip.py | sudo python3")

def install_samba(cxn):
    cxn.sudo("apt-get -y install samba")
    _add_config_file(cxn, "smb.conf", "/etc/samba/smb.conf", "root")
    cxn.sudo("/etc/init.d/samba-ad-dc restart")

    smbpass = Responder(pattern=r'SMB password:',
                         response='%s\n' % NEW_PASSWORD)

    cxn.sudo("smbpasswd -a %s" % NEW_USERNAME, pty=True, watchers=[smbpass])

def install_omxplayer_sync(cxn):
    cxn.sudo("apt-get remove omxplayer")
    cxn.sudo("rm -rf /usr/bin/omxplayer /usr/bin/omxplayer.bin /usr/lib/omxplayer")
    cxn.sudo("apt-get install libpcre3 fonts-freefont-ttf fbset libssh-4 python3-dbus")
    cxn.sudo("wget https://github.com/magdesign/PocketVJ-CP-v3/raw/master/sync/omxplayer_0.3.7-git20170130-62fb580_armhf.deb")
    cxn.sudo("dpkg -i omxplayer_0.3.7~git20170130~62fb580_armhf.deb")
    cxn.sudo("wget -O /usr/bin/omxplayer-sync https://github.com/turingmachine/omxplayer-sync/raw/master/omxplayer-sync")
    cxn.sudo("chmod 0755 /usr/bin/omxplayer-sync")
    cxn.sudo("wget https://github.com/turingmachine/omxplayer-sync/raw/master/synctest.mp4")
    cxn.sudo("wget -O /usr/bin/omxplayer-sync https://github.com/turingmachine/omxplayer-sync/raw/master/omxplayer-sync")
    cxn.sudo("chmod 0755 /usr/bin/omxplayer-sync")
    cxn.sudo("wget https://github.com/turingmachine/omxplayer-sync/raw/master/synctest.mp4")

def install_extra_libs(cxn):
    cxn.sudo("apt-get update")
    cxn.sudo("pip install --user wheel")
    cxn.sudo("pip install --upgrade pip")
    cxn.sudo("apt-get -y install libssl-dev python-nacl python3-dev python3-distutils python3-testresources python-cryptography git cmake ntp autossh libxi6 libffi-dev")
    cxn.sudo("pip install pyudev")
    cxn.sudo("pip install pyroute2")

def remove_bloat(cxn):
    cxn.sudo('apt update')
    cxn.sudo("apt-get -y remove --purge libreoffice*")
    cxn.sudo("apt-get -y remove --purge wolfram*")
    cxn.sudo("apt-get -y remove modemmanager")
    cxn.sudo("apt-get -y remove --purge minecraft*")
    cxn.sudo("apt-get -y purge --auto-remove scratch")
    cxn.sudo("dpkg --remove flashplugin-installer")
    cxn.sudo("apt-get clean")
    cxn.sudo("apt-get autoremove")

def set_hostname(cxn):
    cxn.sudo("sed -i 's/%s/%s/g' /etc/hostname" % (ORIGINAL_HOSTNAME, NEW_HOSTNAME))
    cxn.sudo("sed -i 's/%s/%s/g' /etc/hosts" % (ORIGINAL_HOSTNAME, NEW_HOSTNAME))
    cxn.sudo("hostname %s" % NEW_HOSTNAME)

def _add_config_file(cxn, name, dst, owner, chmod=None):

    cxn.put("config_files/%s" % name, "put_temp")
    cxn.sudo("cp put_temp %s" % dst)
    cxn.sudo("rm put_temp")
    if chmod is not None:
        cxn.sudo("chmod %s %s" % (chmod, dst))
    cxn.sudo("chown %s %s" % (owner, dst))
    cxn.sudo("chgrp %s %s" % (owner, dst))


def _add_software_file(cxn, name, dst, owner, chmod=755):

    cxn.put("bootstrap/%s" % name, "put_temp")
    cxn.sudo("mv put_temp %s" % dst)
    cxn.sudo("chmod %s %s" % (chmod, dst))
    cxn.sudo("chown %s %s" % (owner, dst))
    cxn.sudo("chgrp %s %s" % (owner, dst))


def _put_file(cxn, src, dst, owner, chmod=None):
    cxn.put(src, "put_temp")
    cxn.sudo("mv put_temp %s" % dst)
    if chmod is not None:
        cxn.sudo("chmod %s %s" % (chmod, dst))
    cxn.sudo("chown %s %s" % (owner, dst))
    cxn.sudo("chgrp %s %s" % (owner, dst))

def reboot(cxn):
    print('System reboot')
    cxn.sudo('reboot now')


def reduce_writes(cxn):

    # a set of optimisations from
    # http://www.zdnet.com/article/raspberry-pi-extending-the-life-of-the-sd-card/
    # and
    # https://narcisocerezo.wordpress.com/2014/06/25/create-a-robust-raspberry-pi-setup-for-24x7-operation/

    # minimise writes
    use_ram_partitions(cxn)
    _stop_fsck_running(cxn)
    _remove_swap(cxn)

    # _redirect_logrotate_state()
    # _dont_update_fake_hwclock()
    # _dont_do_man_indexing()

def use_ram_partitions(cxn):

    append_text(cxn, "/etc/fstab", "tmpfs    /tmp    tmpfs    defaults,noatime,nosuid,size=100m    0 0")
    append_text(cxn, "/etc/fstab", "tmpfs    /var/tmp    tmpfs    defaults,noatime,nosuid,size=30m    0 0")
    append_text(cxn, "/etc/fstab", "tmpfs    /var/log    tmpfs    defaults,noatime,nosuid,mode=0755,size=100m    0 0")

def _stop_fsck_running(cxn):
    cxn.sudo("tune2fs -c -1 -i 0 /dev/mmcblk0p2")

def _remove_swap(cxn):
    cxn.sudo("update-rc.d -f dphys-swapfile remove")
    cxn.sudo("swapoff /var/swap")
    cxn.sudo("rm /var/swap")
