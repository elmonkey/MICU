#!/usr/bin/python

'''
Created on July 15, 2014
ref: 
    http://euanfreeman.co.uk/tag/openni/
    http://docs.opencv.org/trunk/doc/py_tutorials/py_gui/py_mouse_handling/py_mouse_handling.html

CURRENT FEATURES:
=> Display
1. openni depthmap --> numpy/opencv array for display
2. openni rgb --> numpy/opencv array for display
=> Mouse Clicking Events
3. Prints on the prompt the distance (in milimiters) to the object's pixel
4. Draws circles where the user has clicked
    blue circle: valid point
    red cirlcle: invalid point (no data can be read ofrm tha position/material)
TO DO: 
1. Save images by pressing spacebar
2. Overlay and align(tricky) rgb on the pointcloud (depth image)
3. Save the pixel's information (col=y,row=x,depth=z, and intensity=l)
Status = Working

@author: carlos
'''

from openni import *
import numpy as np
import cv2
import cv
import time

# Averaging parameters
n=0
N=5

# Initialize
context = Context()
context.init()

# create the depth genrator to access the depth stream
depth_generator = DepthGenerator()
depth_generator.create(context)
depth_generator.set_resolution_preset(RES_VGA)
depth_generator.fps = 30

# Create the rgb image generator
image_generator = ImageGenerator()
image_generator.create(context)
image_generator.set_resolution_preset(RES_VGA)
image_generator.fps = 30

depth_generator.alternative_view_point_cap.set_view_point(image_generator)

depth_map = None


# Circle drawing parameters
row = 480/2 # height
col = 640/2 # width
radius = 3
filled = -1
color  = (0,0,0)
red    = (0,0,255)
blue   = (255,0,0)
green  = (0,255,0)
yellow = (0,255,255)

# Mouse call back variables
xg,yg = 0,0
printing = False




def capture_depth():
    """ 
    Create array from the raw depth map string.
    depth.get_raw_depth_map_8():= string
    Alternative to "update_depth_image" but doesn't provide floating point
    pixel intensities from depth_image. 
    () -> (1L uint16 ndarray, 3L uint8 ndarray)
    16-bits or two bytes:
        The 12 most signicant digits are used to represent the depth 
        The 4 least significant digits are the user id assigned to that pixel
        --> depth values range from 0 to 2**12-1
    """
    depth_frame = np.fromstring(depth_generator.get_raw_depth_map(), "uint16").reshape(480, 640) # 16bits per pixel
    # normalize and set to correct range and data type
    maxval = 2**12-1
    d4d = cv2.cvtColor(np.uint8(depth_frame.astype(float)*255 /maxval),cv2.COLOR_GRAY2RGB) # normalize the values
    return depth_frame, d4d
# get_depth


def capture_rgb():
    '''Get rgb stream from primesense and convert it to an rgb numpy array'''
    rgb = np.fromstring(image_generator.get_raw_image_map_bgr(), dtype=np.uint8).reshape(480, 640, 3)
    return rgb
# capture_rgb


def negativeImage(im):
    '''Computes the negative of a given image.'''
    base = np.ones(im.shape, dtype = np.uint8) * 255
    negim = base - im
    return negim
#negativeImage


# creating a callback function
def draw_circle(event, x,y,flags, param):
    """Mouse call back function. cv2.EVENT_< >
    Continuous promts: < > = MOUSEMOVE
    Selective prompts: < > = LBUTTONDOWN
    """
    global xg,yg, printing
    if event == cv2.EVENT_LBUTTONDOWN:
    #if event == cv2.EVENT_MOUSEMOVE:
        #cv2.circle(canvas,(x,y),radius,color,filled)
        #xg = x-641 # adjustment for rgb stacking: click on the depth
        xg = x
        yg = y
        printing = True
#draw_circle


def harriscorners(im):
    """Compute harris coners and overlay them on the input image. Pixel accuracy
    http://docs.opencv.org/trunk/doc/py_tutorials/py_feature2d/py_features_harris/py_features_harris.html
    """
    rgb = im.copy()
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    corners = cv2.cornerHarris(gray,2,3,0.04)
    #result is dilated for marking the corners, not important
    corners = cv2.dilate(corners,None)
    # thresholded corners will appear red
    rgb[corners>0.01*corners.max()] = [0,0,255]
    return rgb, corners
# harris corners



##def compEdges(im):
##    edges
##    return edges


## MAIN LOOP
# start the device carmine
context.start_generating_all()

#winName = 'canvas: rgb || negative || depth'
winName = 'canvas: depth'
cv2.namedWindow(winName)
cv2.setMouseCallback(winName,draw_circle)
pts = []


# Run metrics
globalframe = 0
run_time    = 0
accu_depth  = np.ones((480,640,N),dtype=np.float64)

ready = False

## --- MAIN LOOP ---
i = 1
done = False
while not done:
    tic = time.time()
    key =cv2.waitKey(1) & 255
    if key == 27:
        done = True

    # read depth & rgb streams
    depth, depth4display = capture_depth()
    rgb = capture_rgb()
    # overlayed
    mask   = np.uint8(depth4display)
    mask   = np.where(depth4display>0,1,mask)
    mask = mask*rgb

    if n == N or n==1:
        ready = True
        n=0
    if not ready:
        accu_depth[:,:,n]        = depth

    # depth & rgb captions
    cv2.putText(depth4display,"depth",(10,470), cv2.FONT_HERSHEY_PLAIN, 2.0, blue,
                thickness=2, lineType=cv2.CV_AA)

    rgb1 = rgb.copy()
    cv2.putText(rgb1,"rgb",(10,470), cv2.FONT_HERSHEY_PLAIN, 2.0, yellow,
                thickness=2, lineType=cv2.CV_AA)
    cv2.line(rgb1,(col,row-4), (col,row+4), yellow, thickness=2)
    cv2.line(rgb1,(col-4,row), (col+4,row), yellow, thickness=2)

    mask1 =mask.copy()
    cv2.putText(mask1,"overlayed",(10,470), cv2.FONT_HERSHEY_PLAIN, 2.0, green,
                thickness=2, lineType=cv2.CV_AA)

    #pixel = depth_generator.map[col,row]
    if printing:
        #xg = xg-639 
        print 'Clicked on Canvas-pixel coords: (%d, %d)'%(xg, yg)
        if xg>=0 and xg <640: #depth
            pixel = depth_generator.map[np.abs(xg),yg]
            if pixel == 0:
                print str(pixel)+ ' unknown (e.g., relfection or out of range)'
                color = red
            else: #pixel not 0
                print 'PT'+str(i)+' clicked (',xg,yg,'): ',str(pixel),'mm away.'
                pts.append([xg,yg])
                color = blue
        elif xg >= 640 and xg <1279: #rgb
            xg -= 639
            color = yellow
            print 'yellow'
        elif xg >= 1279: #mask
            xg -= 1279
            color = green
            print 'green'
        i+=1
        printing = False
##    if ready:
##        cv2.circle(rgb1,(xg,yg),radius,color,filled)
##        cv2.circle(depth4display,(xg,yg),radius,color,filled)
##        cv2.circle(mask,(xg,yg),radius,color,filled)
    cv2.circle(rgb1,(xg,yg),radius,color,filled)
    cv2.circle(depth4display,(xg,yg),radius,color,filled)
    cv2.circle(mask1,(xg,yg),radius,color,filled)
    corners,detected = harriscorners(rgb)
    cv2.putText(corners,"harris",(10,470), cv2.FONT_HERSHEY_PLAIN, 2.0, red,
                thickness=2, lineType=cv2.CV_AA)    

    #rgbm = rgb.copy()
    # stack the images and display
    canvas = np.hstack((mask,depth4display,rgb1))
    cv2.imshow(winName, canvas)
    #canvas = np.vstack((np.hstack((depth4display,rgb1)),np.hstack((mask1,corners)) ))
    #cv2.imshow(winName, cv2.resize(canvas,(canvas.shape[1]/2,canvas.shape[0]/2)))

    context.wait_any_update_all()
    n +=1
    globalframe += 1
    #print "Frame number %d" %globalframe
    toc = time.time()
    run_time += toc-tic
#while

# print 'depth:', depth.shape, ' rgb:', rgb.shape, ' negative:', negim.shape
fps = globalframe/run_time
#print type(mask), mask.dtype, mask.shape, mask.min(), mask.max(), np.unique(mask), len(np.unique(mask))
# print some timing information:
print ("total run time is %.2f secs" % run_time)
print ("fps: %.2f" %fps)


height = len(pts)
pts = np.array(pts).reshape(height,2)
#print pts
#print type(pts)

# close carmine context and stop device
context.stop_generating_all()
cv2.destroyAllWindows()