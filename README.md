TemPy
=============================

0 - Requirements
-----------------------------
* Python 3.6.x
* python-requests
*  python-raspberry-gpio (AUR)

1 - Setup
-----------------------------
- Raspberry Pi
  "dtoverlay=w1-gpio" in /boot/config.txt
  "w1-gpio" and "w1-therm" in /etc/modules-load.d/w1therm.conf

- Tempy
  This program :) Placed in home folder for easy guthub pulled updates.
  Place systemd file in /etc/systemd/system/tempy.service
  systemctl enable & start

Optional:

- vnstat
  monitor data usage
  - edit /etc/vnstat.conf to point to correct interface
  - systemctl enable & start

- ddclient
  Update public ip address to nsupdate.info for ssh access
  - edit /etc/ddclient/ddclient.conf with config from home page
  - systemctl enable & start

- sshd
  ssh access
  - edit /etc/ssh/sshd_config
  - keys in ~/.ssh/authorized_keys
  - systemctl enable & start


1 - Usage
-----------------------------
- Run manually firs time to ensure pairing with server,
then start and enable systemd-service.

2 - Testing
-----------------------------
