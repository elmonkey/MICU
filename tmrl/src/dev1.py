#!/usr/bin/python
'''
Created on Jan 31, 2014
Versions:
    Feb1
    Feb2
    May9
    May30
    Jul 23 - corrected depth map generation (no longer using histogram/frame)
    Aug 11 - Optmized rgb and depth capture/update functions
    Aug 17 - Added NTP
    Dec 7  - Added tcp server and client support

Dependencies:
1) pyopenni to acquire: depth, rgb, & mask(user pixels) from primesense device
2) numpy to convert openni structures/data to mat arrays
3) opencv for display, saving frames, and generating videos
4) pytables (hdf5) for data rcording


Status: operational
    It can record/displays frames (w or w/o user deteced) and store the info
    display device frames; vis=True
    save current view by pressing spacebar (stored in "../data/screen/" folder
    saves frames in "../data/frames/" folder; requires save_frames_flag=True
    generates avi videos "../data/videos/"; requires generate_videos=True
    terminate code by pressing "Esc"


Current features:
    1) Saves png for types for the run: rgb, depth, mask, skel, all
        rgbdm is saved at 4:1. See "frames" folder
            save_frames_flag=True
    2) Current view/frame can be saved by pressing spacebar. See "screen" folder
        NOTE: skelton & 'useful' mask appear when user is being tracked, else
            blank frames are saved.

    2) Displays the images: normal, medium, or small
        rgb, skeleton_joints, depth,mask
        Currently displaying small

    3) Extracts joints (beow is original pyopenni format)
        type(joint) -> class
        type(joint.point) -> list
        len(joint.point) -> 3
        type(joint.confidence)-> float

    4) Realworld and Projective joint coordinates stored in dictionaries
        pyopenni joints -> r_jnts={} and p_jnts={}
        keys:= str, ["head", "torso", "l_shoulder", ... r_shoulder, etc.]
        values: = list,[x,y,z,confidence]where elements are floats

    5) Create an HDF5 file (pytable)
        name: 'mmARC_device#.h5'
        group: 'action'
        table: 'actor'
            ||globalframe|viewframe|jnt_confidence|realworld[xyz]|...
             |projective[xyz]|timestamp|viewangle|actionlabel|actorlabel|...
             |locatime_stimestamp||
    
    6) tcp client
        devid: dev1 (or dev2)
        commands: connect, check, disconnect


ToDo:
    1) Needs a time/scheduler to begin recording in a synchronized manner
    2) Create a dictionary w frame number, user id, and joint+confidence
    3) Try NTP for timestamp synchronization


DONE
    1) DONE: Save joints to respective frame
    2) DONE: Save ALL info to hdf5 <--> Requires arctable.py "ARCtable"
        action: str, name of the action E.g., kick
        angle: int, orientation angle wrt to front facing dev. E.g., [0:40:320]
        actor: str, actor name
        dev: str, device indx label # -> "dev1"
        projective: dictionary, projective 15-joint coordinates.
            key := joint; value:= [x,y,z,conf], list of floats
        realworld: dictionary, real world 15-joint coordinates [x y z]
        time: foat, time stamp from system/computer
        frame number : frame
        name: str, name used to save the rgb image (use: str.replace(rgb,mask))
        status: Bool, currently tracking a user (any user) o the scene

Useful - but not required (TODO):
    1) Dictionary: carmine={}
        keys=[tracking, confidence, projective, realWorld, timestamp, device,
              action, actor, angle, imname,userid]#, pose, sequence, bmom, bRT,
              gRT, gmom, hogRGB, hogDepth]
              
Open a terminal, set server IP, and run the server
ctrl+alt+t
sudo ifconfig eth0 192.168.1.10 netmask 255.255.255.0
sudo ifconfig wlp8s0 192.168.1.10 netmask 255.255.255.0 #alienware ubuntu 15.10
sudo ifconfig enp7s0 192.168.1.14 netmask 255.255.255.0


@author: Carlos Torres <carlitos408@gmail.com>
'''
from openni import *
import numpy as np
import cv
import sys
import cv2
import time
import os, csv
#import tables as tb
#import arctable as arc
from tables import *
from time import localtime, strftime, gmtime

#import ntplib # NTP
#from time import ctime

#import socket
import client


XML_FILE = 'config.xml'
#MAX_DEPTH_SIZE = 10000

context = Context()
context.init_from_xml_file(XML_FILE)

depth_generator = DepthGenerator()
depth_generator.create(context)

image_generator = ImageGenerator()
image_generator.create(context)

user_generator = UserGenerator()
user_generator.create(context)

user_generator.alternative_view_point_cap.set_view_point(image_generator)

depth_map   = None

# drawing skeleton of detected user(s)
radius = 10
green  = (0,255,0)
blue   = (255,0,0)
red    = (0,0,255)
colors = [green, blue, red]
confs  = [1.0, 0.5, 0.0]

x = 480/2
y = 640/2

# skeleton-joint handler:
handler  = {"head":         SKEL_HEAD,
            "neck":         SKEL_NECK,
            "torso":        SKEL_TORSO,
            "l_shoulder":   SKEL_LEFT_SHOULDER,
            "l_elbow":      SKEL_LEFT_ELBOW,
            "l_hand":       SKEL_LEFT_HAND,
            "l_hip":        SKEL_LEFT_HIP,
            "l_knee":       SKEL_LEFT_KNEE,
            "l_foot":       SKEL_LEFT_FOOT,
            "r_shoulder":   SKEL_RIGHT_SHOULDER,
            "r_elbow":      SKEL_RIGHT_ELBOW,
            "r_hand":       SKEL_RIGHT_HAND,
            "r_hip":        SKEL_RIGHT_HIP,
            "r_knee":       SKEL_RIGHT_KNEE,
            "r_foot":       SKEL_RIGHT_FOOT
          }
# handler


# array to store the image modalities+overlayed_skeleton (4images)
rgb   = np.zeros((480,640,3), np.uint8)
rgbdm = np.zeros((480,640*4, 3), np.uint8)

#check and/or generate the folder to store the images:
p = "../data/"#frames/"
if not os.path.isdir(p):
    print "creating folder"
    os.makedirs(p)
#if
screen = "../data/screenshots/"
#if not os.path.isdir(screen):
#    print "creating folder"
#    os.makedirs(screen)
#if



# Pose to use to calibrate the user
pose_to_use ='Psi'

# Obtain the skeleton & pose detection capabilities
skel_cap = user_generator.skeleton_cap
pose_cap = user_generator.pose_detection_cap

# ====== Declare the callbacks
def new_user(src, id):
    print "1/4 User {} detected. Looking for pose..." .format(id)
    pose_cap.start_detection(pose_to_use, id)
#new_user()

def pose_detected(src, pose, id):
    print "2/4 Detected pose {} on user {}. Requesting calibration..." .format(pose,id)
    pose_cap.stop_detection(id)
    skel_cap.request_calibration(id, True)
#pose_detected

def calibration_start(src, id):
    print "3/4 Calibration started for user {}." .format(id)

def calibration_complete(src, id, status):
    if status == CALIBRATION_STATUS_OK:
        print "4/4 User {} calibrated successfully! Starting to track." .format(id)
        skel_cap.start_tracking(id)
    else:
        print "ERR User {} failed to calibrate. Restarting process." .format(id)
        new_user(user_generator, id)

def lost_user(src, id):
    print "--- User {} lost." .format(id)

# Register them
user_generator.register_user_cb(new_user, lost_user)
pose_cap.register_pose_detected_cb(pose_detected)
skel_cap.register_c_start_cb(calibration_start)
skel_cap.register_c_complete_cb(calibration_complete)

# Set the profile
skel_cap.set_profile(SKEL_PROFILE_ALL)

# Start generating
context.start_generating_all()
print "0/4 Starting to detect users. Press Esc to exit."



def capture_depth():
    """ 
    Create np.array from Carmine raw depthmap string using 16 or 8 bits
    depth = np.fromstring(depth_generator.get_raw_depth_map_8(), "uint8").reshape(480, 640)
    max = 255 #=(2**8)-1
    """
    dmap = np.fromstring(depth_generator.get_raw_depth_map(),dtype=np.uint16).reshape(480, 640)
    max = 4095 # = (2**12)-1
    depth_norm=(dmap.astype(float) * 255/max).astype(np.uint8)
    d4d = cv2.cvtColor(depth_norm, cv2.COLOR_GRAY2RGB) # depth4Display
    return dmap, d4d
#capture_depth


def capture_rgb():
    """
    Get rgb stream from primesense and convert it to an rgb numpy array.
    """
    rgb = np.fromstring(image_generator.get_raw_image_map_bgr(), dtype=np.uint8).reshape(480, 640, 3)
    return rgb
# capture_rgb


def capture_mask():
    """
    Get mask from pyopenni user_generator [0,1].
        mask:= numpy array, single channel in [0 255] range
    """
    #mask:= binary [0,1], converted to [0,255]
    mask = np.uint8(np.asarray(user_generator.get_user_pixels(0)).reshape(480, 640)*255)
    return mask
#capture_mask

def save_frames(globalframe, rgb,depth,mask,skel, p="../data/frames/", msg = False):#,depth,mask, n):
    """
    Saves the images to as lossless pngs and appends the frame number n
    """
    # save te images to the path
    if msg:
        print "Saving image {} to {}".format(globalframe,p)
    cv2.imwrite(p+"rgb/"+"rgb_"+str(globalframe)+".png",rgb)
    cv2.imwrite(p+"depth/"+"depth_"+str(globalframe)+".png",depth)
    if len(np.unique(mask)) > 1:    
        cv2.imwrite(p+"mask/"+"mask_"+str(globalframe)+".png",mask)
    if len(np.unique(skel)) > 1:
        cv2.imwrite(p+"skel/"+"skel_"+str(globalframe)+".png",skel)
    #cv2.imwrite(p+"all_"+str(globalframe)+".png",rgbdm)
    return
# save_frames

def convert2projective(joint):
    """
    Convert pyopenni joint_object into a list of floats:[x,y, z, confidence]
    x, y, z, and confidence are floats
    """
##    print 'jnt: ', [joint.point]
    pt = depth_generator.to_projective([joint.point])[0]
    projective_joint= [float(pt[0]), float(pt[1]), float(pt[2])]#, joint.confidence]
    return projective_joint
#convert2projective

def get_joints(id):
    """
    Extract/convert real-world joints to projective
    key:= , str joint label [head, neck, lshoulder, rshoulder]
    value:= float, [x,y,z, confidence]
    input:
        id:= int, user id number for which joint coorindates are needed
    outputs:
        p_joints:= dictionary, projective joints coordinates
        r_joints:= dictionary of real-world joint coordinates (same format)
            value:= list [float, float, float ,float]
            key:= str, joint label (see below)
    >>> get_joints(int)-> dictionary, dictionary
    Accessing dictionary:
        >>> p[head] ->  [20.0, 30.0, 10.0, 0.5] 
    """
    # initialize the dictionaries:
    r={}
    p={}
    real_w = {}
    for key in handler.keys():
        r[key] = skel_cap.get_joint_position(id,handler[key])# -> [str,str,str,float]
        # Convert to projective
        p[key] = convert2projective(r[key])
        # Convert the data in the original dictonary to format
        real_w[key] = [ float(r[key].point[0]),float(r[key].point[1]),
                        float(r[key].point[2]),r[key].confidence]
        # confidences:
    return p, real_w
# get_joints


def get_joint_arrays(id):
    """
    Extract/convert real-world joints to projective
    key:= , str joint label [head, neck, lshoulder, rshoulder]
    value:= float, [x,y,z, confidence]
    input:
        id:= int, user id number for which joint coorindates are needed
    outputs:
    old:
        p_joints:= dictionary, projective joints coordinates
        r_joints:= dictionary of real-world joint coordinates (same format)
            value:= list [float, float, float ,float]
            key:= str, joint label (see below)
        >>> get_joints(int)-> dictionary, dictionary
        Accessing dictionary:
            >>> p[head] ->  [20.0, 30.0, 10.0, 0.5]
    NEW:
        confidences = np.array; shape=(15,1)
        proj_coords = np.array; shape=(15,3)
        real_coords = np.array; shape=(15,3)
    >>> get_joints(int)-> array(15,3),array(15,3),array(15,1)
    >>> print handler.keys() #for order or joints or see 'handler '
    """
    # initialize the dictionaries:
    r={}
    p={}
    real_w    = {}
    real_list = []
    proj_list = []
    conf_list =[]
    for key in handler.keys():
        r[key] = skel_cap.get_joint_position(id,handler[key])# -> [str,str,str,float]
        # Convert to projective
        p[key] = convert2projective(r[key])
        # Convert the data in the original dictonary to format
        real_w[key] = [ float(r[key].point[0]),float(r[key].point[1]),
                        float(r[key].point[2])]#,r[key].confidence]
        #convert to list
        conf_list.append(r[key].confidence)
        proj_list.append(p[key])
        real_list.append(real_w[key])
    # convert to array
    confidences = (np.array(conf_list)).reshape(15,1)
    proj_coords = (np.array(proj_list)).reshape(15,3)
    real_coords = (np.array(real_list)).reshape(15,3)
    return proj_coords, real_coords, confidences
# get_joint_arrays

def createFolders(actor='patient_0', root = "../data/icudata1/", to_mem=False):
    """
    Checks if a sdcard is connected and if a folder exists under 
        root/icudata/patient_<number>
    If it exists a new name is created
        newname = root/icudata/patient_<number+1>
        foldername = newfoldername
    Ultimately, creates folders for frames and csv files and returns paths.
        folder4frames='root/icudata/patient_<number+1>/frames/'
        folder4csv   ='root/icudata/patient_<number+1>/csv/'
    """
    #storage='Local'    
    ## check existence of directory.
    folder = root+actor
    name,idx = actor.split('_')
    done = False
    while not done:
        if os.path.isdir(folder):
            'Directory exists {}... renaming!'.format(root)
            name,idx = actor.split('_')
            idx = str(int(idx)+1)
            print idx
            actor = ('_').join([name,idx])
            folder = root+actor
            
        else:
            print 'Directory {} Doesnt Exist. Creating It'.format(folder)
            folder4csv    = folder+'/csv/'
            os.makedirs(folder4csv)        
            folder4frames = folder
            for r in ['raw', 'sync']:
                for m in ['rgb', 'depth', 'mask','skel']:
                    os.makedirs(folder4frames+'/'+r+'/'+m+'/')
            done = True
    print "Created the folders {} and {}".format(folder4frames, folder4csv)
    return folder4frames, folder4csv
# createFolders()


def talk2server(cmd='connect', dev=1):
    """
    Communicate with server 'if active'
    inputs:
        cmd = str 'connect' ,'check' , 'sync' or 'close'
        dev = int 1, 2, ... n, (must be declared in server_threads.py)
    outputs:
        server_reponse = str, server response
        server_time = str, server timestamp
    usage:
    server_response, server_time = talk2server(cmd='connect',dev=1)
    """
    # intialize
    server_response = "nada"
    server_time = 0.0
    try:
        server_response, server_time = client.check_tcp_server(cmd=cmd,dev=dev).split("_")
    except: # noserver response
        server_time="na"
        server_response="none"
    #print "server reponse: {} and timestamp: {}".format(server_response, server_time)
    return server_response, server_time



# ======== MAIN =========
#if __name__ == '__main__':

# time.sleep(20) # secs pause! for startup
print"About to begin execution of code"
dev = 1
synctype  = 'relaxed'
actorname = "patient_0"
test_flag = True
test_frames = 300000

## Runtime and Controls
nf  = 30 #172800# 60*60*24*2 # Number of video frames in one day at 2 fps
f   = 1  # frame counter
tic = 0
run_time   = 0
total_t    = 0
done = False
global_f =0
## TCP communication
print "Call to server"
server_response, server_time = talk2server(cmd='connect',dev=dev)    
print "Return from Server"

## Flags
vis_frames      = True# True   # display frames
save_frames_flag= True #True  # save all frames
generate_videos = False #True #True  # use the saved frames to generate .avi files

## The folders for all data
print "Creating Folders"
folder4frames,folder4csv=createFolders(actorname,root = "../data/icudata"+str(dev)+"/")
# start the device carmine
context.start_generating_all()

# bufsize = 2**27; #64Mbytes in bits
## open/create csv file
with open(folder4csv+actorname+"_dev"+str(dev)+'.csv','w') as fp:#, bufsize) as fp:
    # Set the writer with comma delimiter
    writer=csv.writer(fp, delimiter=',')
    
    # Get the first timestamp    tic = time.time()
    start_time = time.time() 
    
    # Write zero data point
    datarow=['start time', tic, ' ', strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())]
    writer.writerow(datarow)
    
    # Write column names:
    colnames =['frame','localtic=gmtime','servertic=gmtime']
    writer.writerow((colnames))
    print "Done writing the csv headers"
    
    ##--- main loop ---
    done     = False
    while not done: # view <= nviews
        ## RGB-D Streams
        #collect images from carmine - even w/o a user detected
        rgb   = capture_rgb()
        #depth,d4d = update_depth_image()
        dmap, d4d = capture_depth()

        skel  = np.ones((480,640, 3), np.uint8)*255
        #cv2.putText(skel,"NO USER",(x,y), cv2.FONT_HERSHEY_PLAIN, 2.0, red,
        #thickness=2, lineType=cv2.CV_AA)
        mask  = capture_mask()

        # Extract head position of each tracked user
        for id in user_generator.users: # Consider only one user by ussing [0]
            if skel_cap.is_tracking(id):
                # Get the frames
                rgb   = capture_rgb()
                depth,d4d = capture_depth()
                mask  = capture_mask()
                skel  = rgb.copy()
                p_jnts, r_jnts, confidences = get_joint_arrays(id) # projective and real coordnates
                #draw joints:
                for i in np.arange(14):
                    center = (int(p_jnts[i,0]), int(p_jnts[i,1]))
                    conf = confidences[i]
                    color = colors[confs.index(conf)]
                    cv2.circle(skel, center ,radius, color, thickness=-2)
            #if skel_cap
        #for id
        
        ## Display the streams
        # Check the flags
        if vis_frames: # Display the streams
            rgbdm = np.hstack((rgb,d4d, skel, np.dstack((mask,mask,mask))))
            #rgbdm_small = rgbdm # orginal size
            #rgbdm_small = cv2.resize(rgbdm,(1280,240)) # medium
            rgbdm_small = cv2.resize(rgbdm,(640,240)) # smallest        
            cv2.imshow("1:4 scale", rgbdm_small) # small
            ## === Keyboard Commands ===
            key = cv2.waitKey(1) & 255
            if key == 27: 
                print "Terminating code!"
                done = True                
            #check vis_frames
        #update the streams
        context.wait_any_update_all()
        
        #Poll the server:
        server_response, server_time = talk2server(cmd='check',dev=dev)
        
        
        #print "here: " , server_response
        
        if server_response == 'save':
            #print 'Saving -- server response!'
            save_frames(f,rgb,dmap,mask,skel,p=folder4frames+'/sync/', msg=True)
            # Write Datarows
            datarow =[f,run_time, strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),server_time]
            writer.writerow(datarow)
            f+=1
        save_frames(global_f,rgb,dmap,mask,skel,p=folder4frames+'/raw/')
        global_f+=1
            
        if test_flag and (f==test_frames): 
            print "Terminating code!"
            done = True
        #elif chr(key) =='s':  #s-key to save current screen
        #    save_frames(f,rgb,dmap,p=folder4screens)
        
        #if
        # --- keyboard commands ---
    # while
    end_time = time.time()
    run_time = end_time - start_time
    #Write the last rows
    fps = f/(run_time)
    datarow=[['fps', fps],['runtime',run_time]]
    writer.writerows(datarow)
# end csv file        

# TERMINATE
print "===Terminating code!==="
# Close carmine context and stop device    

# Disconnect the client from the server
print "\tDisconecting client"
#client.check_tcp_server(cmd='close',dev=dev)
server_response, server_time = talk2server(cmd='close',dev=dev)    

# Close carmine context and stop device    
print "\tClosing carmine context"    
context.stop_generating_all()

# Release video/image resources
cv2.destroyAllWindows()
#vidout.release()
        
# print some timing information:
print "Time metrics:" 
print ("\ttotal run time is %.2f secs" %run_time)
print ("\tfps: %.2f" %fps)

# generate the .avi video files
if (save_frames and generate_videos):
    print "Video generated"
    os.system ("python carmine_generate_vids.py ")

sys.exit(0)
#if __main__
