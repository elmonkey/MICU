# -------------------------
# Mounting usb thumbdrives
# ref: 
# http://www.htpcguides.com/properly-mount-usb-storage-raspberry-pi/
# NOTE: best to follow the link with the parameters listed here. The site has many more details.
#       I ranamed pi  (e.g., pi --> carlos@pi0, pi2, ... ,pi5).

# EASIEST METHOD: interface to properties -> disk -> select the drive -> mounting properties
# ====================
# create mount point
sudo mkdir /mnt/usbstorage
# change ownership
sudo chown -R carlos:carlos /mnt/usbstorage
sudo chmod -R 775 /mnt/usbstorage #777 removes all restrictions (security risk?)
# Set Persmission
sudo setfacl -Rdm g:carlos:rwx /mnt/usbstorage
sudo setfacl -Rm g:carlos:rwx /mnt/usbstorage
# update repos
sudo apt-get update -y
# ntfs utilities
sudo apt-get install ntfs-3g -y
sudo mount -o uid=carlos,gid=carlos /dev/sda1 /mnt/usbstorage

## Automount the USB Hard Drive on Boot
#The best way to do this is through the UUID. Get the UUID by using this commmand
sudo ls -l /dev/disk/by-uuid/
# output: 
#total 0
#lrwxrwxrwx 1 root root 15 Jan  1  1970 3d81d9e2-7d1b-4015-8c2c-29ec0875f762 -> ../../mmcblk0p2
#lrwxrwxrwx 1 root root 15 Jan  1  1970 787C-2FD4 -> ../../mmcblk0p1
#lrwxrwxrwx 1 root root 10 Oct 26 21:10 BA8F-FFE8 -> ../../sda1

## The UUID you want is formatted like this XXXX-XXXX for the sda1 drive. 
# If the drive is NTFS it can have a longer format like UUID="BABA3C2CBA3BE413". 
# CT NOTE: I USED QUOTATIONS!!

#sudo nano /etc/fstab
sudo pluma /etc/fstab # EASIER THAN REMEMBERING NANO COMMANDS

#  copy the following at the end/bottom of the file. and note the quotation marks and ntfs
# UUID="XXXXXXXXXXX"  /mnt/usbstorage ntfs   nofail,uid=carlos,gid=carlos   0   0
# test mount
sudo mount -a
# if no errors then reboot else go to the site (ref above) and try the suggestions.
sudo reboot
# test the thing
cd /mnt/usbstorage
ls
# create a file
pluma test_file.txt
