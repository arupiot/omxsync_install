# omxsync_install

Script to configure a Raspberry Pi with omxplayer-sync for synchronised video display.

## Get and burn OS image

* Get the [latest raspian image](https://downloads.raspberrypi.org/raspbian_lite_latest)
* Get [Etcher](https://www.balena.io/etcher/) to burn it with
* Burn image to mini SD card for use in Pi

## Configure Pi for wifi/ssh access

Raspbian has some built in magic to help configure sd cards directly.
Mount the flashed SD card on your PC and add two files to the boot folder.

* An empty file called `ssh`, this will turn on sshd
* Copy the `wpa_supplicant.conf` file from the `boot` folder of this repo and update it with the ssis and psk of your local wifi.
* Determine the ip address of the pi, either by booting with a screen attatched,
working on a network where the host broadcast works or other devious means.

## Install local requirements

* Clone this repo locally
* Create python 3 virtualenv
* Install requirements.txt: `pip3 install -r requirements.txt`

## Configure card build

* Create a `config_local.py` editing the following variables:

```
HOSTNAME = "hostname"
PASSWORD = "password"
USERNAME = "pivideo"
ACCESS_IP = "XXX.XXX.XXX.XXX"
```

### Build card with Fabric script

* In a terminal window, `cd` to the root of this repo
* Run `fab omxplayer_sync` and respond `y` to all the questions
* Run `fab make-master` if the connected raspberry pi is intended to be a master node, or `fab make-slave` if it is inteded to be a slave node
* Run `fab reboot`

Other commands are available and shown using `fab -l`
