#!/bin/sh
#Installation script for opencv2.9, openni2.2 and primesense python wrapper
#author: Carlos Torres <carlitos408"gmail.com>

sudo apt-get update && sudo apt-get dist-upgrade && sudo apt-get autoclean && sudo apt-get autoremove && sudo apt-get update 

sudo apt-get install -y build-essential cmake cmake-gui qt5-default libvtk6-dev

sudo apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libjasper-dev libopenexr-dev libgdal-dev

sudo apt-get install -y libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev

sudo apt-get install -y libeigen3-dev ant default-jdk
sudo apt-get install -y libtbb-dev # no raspbian candidate
sudo apt-get install -y python-dev python-tk python-numpy python3-dev python3-tk python3-numpy

sudo pip install pandas
sudo apt-get install -y libudev1 libudev-dev
sudo apt-get install -y git g++ python libusb-1.0-0-dev freeglut3-dev doxygen graphviz

# python development
sudo apt-get -y install python-dev python-numpy
sudo apt-get -y install python-scipy python-setuptools ipython python-pip
sudo apt-get -y install libboost-python-dev

# OpenCV 2.4.9
sudo apt-get install -y libopencv-dev python-opencv

## Follow the github for primense2 installation
# ref: https://github.com/elmonkey/Python_OpenNI2
cd ~/Install && mkdir kinect && cd kinect
git clone https://github.com/occipital/OpenNI2 && cd OpenNI2
## Compile. Remove the floating point operation flag
# line 4: Remove/delete  "-mfloat-abi=softfp" (save & close)
#pluma ThirdParty/PSCommon/BuildSystem/Platform.ARM
#PLATFORM=Arm make -j2 # OpenNI2 directory
# Create ARM installer
#cd Packing/
#python ReleaseVersion.py Arm

#cp Final/OpenNI-Linux-Arm-2.2.tar.bz2 ~/Install/kinect/

## If no errors, the compressed installer will be created in "Final" folder (i.e., OpenNI-Linux-Arm-2.2.tar.bz2).

#cd Final && cp OpenNI-Linux-Arm-2.2.tar.bz2 ~/Install/kinect/openni2

## Extract the contents to OpenNI-Linux-Arm-2.2 and rename the folder (helps with multiple installations/versions)
#mv ~/Install/kinect/openni2/OpenNI-Linux-Arm-2.2 ~/Install/kinect/
##Install
#sudo ./install.sh

## Primesense python wrapper
#wget https://pypi.python.org/pypi/primesense/
#cd primesense-2.x.x.xx.x
#sudo python setup.py install

## Remote access via VNC
#https://www.raspberrypi.org/documentation/remote-access/vnc/README.md
#http://mitchtech.net/vnc-setup-on-raspberry-pi-from-ubuntu/

## Get the micu repo
cd ~/Documents/ && mkdir Python && cd Python
git clone https://github.com/elmonkey/MICU.git

# activate remote desktop access via vnc
# https://www.raspberrypi.org/documentation/remote-access/vnc/README.md
#device name = pi2
#ip  = 192.xxx.x.xx
#pwd = vxxxxx
