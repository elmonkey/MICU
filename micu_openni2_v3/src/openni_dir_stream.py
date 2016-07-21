#!/usr/bin/env python
'''
Created on 19Jun2015
Stream rgb and depth images side by side using opencv-python (cv2). Streams are synchronized and aligned.

Requires the following libraries:
    1. OpenNI-Linux-<Platform>-2.2 <Library and driver>
    2. primesense-2.2.0.30 <python bindings>
    3. Python 2.7+
    4. OpenCV 2.4.X

Current features:
    1. Convert primensense oni -> numpy
    2. Stream and display rgb || depth || rgbd overlayed
    3. Keyboard commands    
        press esc to exit
        press s to save current screen and distancemap
    4. Sync and registered depth & rgb streams
    5. Print distance to center pixel
    6. Masks and overlays rgb stream on the depth stream

NOTE: 
    1. On device streams:  IR and RGB streams do not work together
       Depth & IR  = OK
       Depth & RGB = OK
       RGB & IR    = NOT OK
@author: Carlos Torres <carlitos408@gmail.com>
'''

import numpy as np
import cv2
from primesense import openni2#, nite2
from primesense import _openni2 as c_api


## Path of the OpenNI redistribution OpenNI2.so or OpenNI2.dll
# Windows
#dist = 'C:\Program Files\OpenNI2\Redist\OpenNI2.dll'
# OMAP
#dist = '/home/carlos/Install/kinect/OpenNI2-Linux-ARM-2.2/Redist/'
##alienware
#dist='/home/carlos/Install/kinect2/OpenNI2/Redist'

##pi3
dist = '/home/carlos/Install/kinect/OpenNI-Linux-Arm-2.2/Redist/'


## initialize openni and check
openni2.initialize(dist) #'C:\Program Files\OpenNI2\Redist\OpenNI2.dll') # accepts the path of the OpenNI redistribution
if (openni2.is_initialized()):
    print "openNI2 initialized"
else:
    print "openNI2 not initialized"

## Register the device
dev = openni2.Device.open_any()
## print sensor info

print "Sensor info: ", dev.get_sensor_info(openni2.SENSOR_DEPTH)

## create the streams stream
ir_stream = dev.create_ir_stream()
depth_stream = dev.create_depth_stream()


## Stream speed and resolution.
w   = 320 #640
h   = 240 #480
fps = 30
##configure the depth_stream
#print 'Get b4 video mode', depth_stream.get_video_mode()
depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM, resolutionX=w, resolutionY=h, fps=fps))


## Check and configure the mirroring -- default is True
# print 'Mirroring info1', depth_stream.get_mirroring_enabled()
depth_stream.set_mirroring_enabled(False)
ir_stream.set_mirroring_enabled(False)
#rgb_stream.set_mirroring_enabled(False)


## start the stream
#rgb_stream.start()
depth_stream.start()
ir_stream.start()

## synchronize the streams
#dev.set_depth_color_sync_enabled(True) # synchronize the streams

## IMPORTANT: ALIGN DEPTH2RGB (depth wrapped to match rgb stream)
#dev.set_image_registration_mode(openni2.IMAGE_REGISTRATION_DEPTH_TO_COLOR)

##help(dev.set_image_registration_mode)


def get_rgb():
    """
    Returns numpy 3L ndarray to represent the rgb image.
    """
    bgr   = np.fromstring(rgb_stream.read_frame().get_buffer_as_uint8(),dtype=np.uint8).reshape(h,w,3)
    rgb   = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
    return rgb    
#get_rgb




def get_depth():
    """
    Returns numpy ndarrays representing the raw and ranged depth images.
    Outputs:
        dmap:= distancemap in mm, 1L ndarray, dtype=uint16, min=0, max=2**12-1
        d4d := depth for dislay, 3L ndarray, dtype=uint8, min=0, max=255    
    Note1: 
        fromstring is faster than asarray or frombuffer
    Note2:     
        .reshape(120,160) #smaller image for faster response 
                OMAP/ARM default video configuration
        .reshape(240,320) # Used to MATCH RGB Image (OMAP/ARM)
                Requires .set_video_mode
    """
    dmap = np.fromstring(depth_stream.read_frame().get_buffer_as_uint16(),dtype=np.uint16).reshape(h,w)  # Works & It's FAST
    d4d = np.uint8(dmap.astype(float) *255/ 2**12-1) # Correct the range. Depth images are 12bits
    #d4d = 255 - cv2.cvtColor(d4d,cv2.COLOR_GRAY2RGB)
    d4d = np.dstack((d4d,d4d,d4d)) #faster than cv2 conversion
    return dmap, d4d
#get_depth




def mask_rgbd(d4d,rgb, th=0):
    """
    Overlays images and uses some blur to slightly smooth the mask
    (3L ndarray, 3L ndarray) -> 3L ndarray
    th:= threshold [0:1:128]
    """
    mask = d4d.copy()
    #mask = cv2.GaussianBlur(mask, (5,5),0)
    idx =(mask>th)
    mask[idx] = rgb[idx]
    return mask
#mask_rgbd


def get_ir():
    """
    Returns np arrays representing raw and ranged infra-red (IR) frame.
    Outputs:
        ir   := raw IR, 1L ndarray, dtype=np.uint16, min=0, max=2**12-1
        ir4d := IR for display, 3L ndarray, dtype=np.uint8, min=0, max=255
    """
    ir_frame = ir_stream.read_frame()
    ir_frame_data = ir_stream.read_frame().get_buffer_as_uint16()
    ir4d = np.ndarray((ir_frame.height,ir_frame.width), dtype=np.uint16, buffer=ir_frame_data).astype(np.float32)
    ir4d = np.uint8((ir4d/ir4d.max()) * 255)
    #ird4 = cv2.cvtColor(ir4d, cv2.COLOR_GRAY2RGB)
    ir4d = np.dstack((ir4d,ir4d,ir4d)) # faster than cv2 conversion
    return ir_frame, ir4d



## main loop
s=0
done = False
while not done:

    ## Streams
    #RGB
#    rgb = get_rgb()
    
    #DEPTH
    dmap,d4d = get_depth()
    # INFRARED
    ir, ir4d = get_ir()
    
    # Overlay rgb over the depth stream
 #   rgbd  = mask_rgbd(d4d,rgb, th=100)
    
    # canvas
    canvas = np.hstack((d4d,ir4d))
    #canvas = d4d
    ## Distance map
    #print 'Center pixel is {} mm away'.format(dmap[h/2,w/2])

    ## Display the stream
    #cv2.imshow('depth || rgb || rgbd', canvas )
    cv2.imshow('Depth || IR', canvas )
    key = cv2.waitKey(1) & 255
    
    ## Read keystrokes
    if key == 27: # terminate
        print "\tESC key detected!"
        done = True
    elif chr(key) =='s': #screen capture
        print "\ts key detected. Saving image and distance map {}".format(s)
        cv2.imwrite("ex5_"+str(s)+'.png', canvas)
        np.savetxt("ex5dmap_"+str(s)+'.out',dmap)
        #s+=1 # uncomment for multiple captures        
    #if
    
# end while

## Release resources 
cv2.destroyAllWindows()
#rgb_stream.stop()
depth_stream.stop()
openni2.unload()
print ("Terminated")
