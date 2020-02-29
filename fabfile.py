from fabric import Connection
from invoke import Responder
from fabric import task
import json
import uuid

import os
import logging

logging.raiseExceptions=False

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from config import (
                    HOSTNAME,
                    PASSWORD,
                    USERNAME,
                    ACCESS_IP
                    )

cxn = Connection(host=ACCESS_IP,
                 user=USERNAME,
                 connect_kwargs={"password": PASSWORD},
                 port=22)

@task
def omxplayer_sync(junk):
    remove_bloat()
    install_omxplayer_sync()

@task
def make_master(junk):
    cxn.sudo("rm -rf /etc/systemd/system/omxplayersync.service")
    append_text(cxn, "/etc/systemd/system/omxplayersync.service", "[Service]\nExecStart=/usr/bin/omxplayer-sync -muvb /home/pi/Videos/video.mp4")
    cxn.sudo("systemctl enable omxplayersync.service")
    cxn.sudo("systemctl start omxplayersync.service")

@task
def make_slave(junk):
    cxn.sudo("rm -rf /etc/systemd/system/omxplayersync.service")
    append_text(cxn, "/etc/systemd/system/omxplayersync.service", "[Service]\nExecStart=/usr/bin/omxplayer-sync -luvb /home/pi/Videos/video.mp4")
    cxn.sudo("systemctl enable omxplayersync.service")
    cxn.sudo("systemctl start omxplayersync.service")

@task
def add_startup_delay(junk):
    append_text(cxn, "/etc/rc.local", "sleep 20")

@task
def install_omxplayer_sync(junk):
    cxn.sudo("apt-get remove omxplayer")
    cxn.sudo("rm -rf /usr/bin/omxplayer /usr/bin/omxplayer.bin /usr/lib/omxplayer")
    cxn.sudo("apt-get install libpcre3 fonts-freefont-ttf fbset libssh-4 python3-dbus libssl-dev")
    cxn.sudo("wget security.debian.org/debian-security/pool/updates/main/o/openssl/libssl1.0.0_1.0.1t-1+deb8u12_armhf.deb")
    cxn.sudo("dpkg -i libssl1.0.0_1.0.1t-1+deb8u12_armhf.deb")
    cxn.sudo("wget https://github.com/magdesign/PocketVJ-CP-v3/raw/master/sync/omxplayer_0.3.7-git20170130-62fb580_armhf.deb")
    cxn.sudo("dpkg -i omxplayer_0.3.7-git20170130-62fb580_armhf.deb")
    cxn.sudo("wget -O /usr/bin/omxplayer-sync https://github.com/turingmachine/omxplayer-sync/raw/master/omxplayer-sync")
    cxn.sudo("chmod 0755 /usr/bin/omxplayer-sync")
    cxn.sudo("wget https://github.com/turingmachine/omxplayer-sync/raw/master/synctest.mp4")
    cxn.sudo("wget -O /usr/bin/omxplayer-sync https://github.com/turingmachine/omxplayer-sync/raw/master/omxplayer-sync")
    cxn.sudo("chmod 0755 /usr/bin/omxplayer-sync")
    cxn.sudo("wget https://github.com/turingmachine/omxplayer-sync/raw/master/synctest.mp4")
    cxn.sudo("rpi-update")

@task
def remove_bloat(junk):
    cxn.sudo('apt update')
    cxn.sudo("apt-get -y remove --purge libreoffice*")
    cxn.sudo("apt-get -y remove --purge wolfram*")
    cxn.sudo("apt-get -y remove modemmanager")
    cxn.sudo("apt-get -y remove --purge minecraft*")
    cxn.sudo("apt-get -y purge --auto-remove scratch")
    cxn.sudo("dpkg --remove flashplugin-installer")
    cxn.sudo("apt-get clean")
    cxn.sudo("apt-get autoremove")

@task
def reboot(junk):
    print('System reboot')
    cxn.sudo('reboot now')

def append_text(cxn, file_path, text):
    cxn.sudo('echo "%s" | sudo tee -a %s' % (text, file_path))
