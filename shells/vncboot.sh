#! /bin/sh
# /etc/init.d/vncboot
# install tighvncserver:
# sudo apt-get install tightvncserver
# Create vncboot in /etc/init.d/ as sudo su OR: 
# sudo cp ~/Documents/Python/MICU/shells/vncboot.sh /etc/init.d/
# cd /etc/init.d/
# sudo chmod 755 vncboot.sh
# update-rc.d -f lightdm remove
# update-rc.d vncboot.sh defaults
#
# To View form remote:
# vncviewer xx.x.x.xx:5901
#
# To reset pi pwd on a termina run the following two commands:
# vncpasswd # reenter new pwd twice (1:replace, 2:confirm -- vrl4162)
# service vncserver restart # or restart device

### BEGIN INIT INFO
# Provides: vncboot
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Start VNC Server at boot time
# Description: Start VNC Server at boot time.
### END INIT INFO

USER=carlos
HOME=/home/pi3

export USER HOME

case "$1" in
 start)
  echo "Starting VNC Server"
  #Insert your favoured settings for a VNC session
  su - $USER -c "/usr/bin/vncserver :1 -geometry 1024x600 -depth 16 -pixelformat rgb565"
  ;;

 stop)
  echo "Stopping VNC Server"
  /usr/bin/vncserver -kill :1
  ;;

 *)
  echo "Usage: /etc/init.d/vncboot {start|stop}"
  exit 1
  ;;
esac

exit 0
