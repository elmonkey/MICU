'''
Created on Jan 31, 2014
Gnerates videos
1) rgb
2) depth
3) mask
dependiencies: openni, opencv, numpy

@author: Carlos
'''
#!/usr/bin/python

import os, cv2, openni
import numpy as np


p_src ="../data/icudoorframes/" # folder where to get frames
p_dst ="../data/cropvideos/"    # folder where to save video

rgbdm = np.zeros((480,640*4, 3), np.uint8)


def get_natural_imlist(path,imtype="rgb"):
    '''
    Returns a naturally sorted list of png files from the 'path'directory.
    inputs:
        path:= str, folder that contains the images
        imtype:= modality for teh images (rgb,mask,depth)
    output:
        a NATURALLY sorted list of the images based on their index
            0, 1,2,.., 10, 11, etc.
    NOTE: assumed naming convention for the images: imtype_index#.png
    '''
    names = [os.path.join(path,f) for f in os.listdir(path) if (f.endswith('.png') and (imtype in f))]
    return sorted(names, key=lambda x:int(x.split("_")[1].split(".")[0]))
#get_natural_imlist

def gen_video(p_src, p_dst,s,e, imtype="rgb",fps=10, aviname='test', text=''):
    ''' Generates a .avi video file using the images in the path folder.
    inputs:
        p_src:= str, path to images/frames folder
        p_dst:= str, path to folder where avi will be stored
        imtype:= str, one of 5 types {rgb, mask, depth, skel, all}
        fps:= int, video speed in frames per second
        text= bool, generate video w text message "TESTING: +'frame #'"
        aviname:= str, name of the output video without the extension (.avi)
    (str,str,int,str) -> null
     '''
    #aviname = imtype+"_test"
    #aviname = "tita4BlightOFF"+imtype
    # use the narturalsorted images to generated video:
    natural_names = get_natural_imlist(p_src,"rgb")

##    im = cv2.imread(natural_names[0])
    h,w= rgbdm.shape[0:2]
    x=5 #int(w/2)
    y=h-15#int(h/2)
    text_color = (0,255,0) # BGR
    n=0
    # object that contains the properties of the avi
    writer = cv2.VideoWriter(filename= p_dst+aviname+".avi",
        fourcc=cv2.cv.CV_FOURCC('I','Y','U','V'), fps=10, frameSize=(w,h))
    # go tru the images on the list and create the avi
    for name in natural_names[s:e]:
        rgb = cv2.imread(name)
        mask= cv2.imread(name.replace('rgb', 'mask'))
        depth = cv2.imread(name.replace('rgb', 'depth'))
        skel  = cv2.imread(name.replace('rgb','skel'))

        rgbdm[:,0:640]    = rgb
        rgbdm[:,640:1280] = depth #cv2.cvtColor(depth4display,cv2.COLOR_GRAY2RGB)

        rgbdm[:,1280:1920]= mask #cv2.cvtColor(mask,cv2.COLOR_GRAY2RGB)
        rgbdm[:,1920:2560]= skel

##        if not(text ==""):
##        cv2.putText(rgbdm,text,(x,y), cv2.FONT_HERSHEY_PLAIN, 4.0, text_color,
##            thickness=3, lineType=cv2.CV_AA)

        rgbdm_small = cv2.resize(rgbdm,(1280,240)) # smallest
        cv2.imshow('canvas', rgbdm_small)
        cv2.waitKey(10)

        writer.write(rgbdm) # write to vid file
        n+=1

    print "Video generated, check path: ", p_dst
    print x,y
#gen_video

if not os.path.isdir(p_dst):
    print "creating folder"
    os.makedirs(p_dst)
#
imtype = "rgb"
aviname = aviname = "tita3B"+imtype


##gen_video(p_src, p_dst, imtype="rgb",fps=6, aviname=aviname)
gen_video(p_src, p_dst,s=1382,e=1449, imtype="rgb",fps=10, aviname=aviname)

##gen_video(p_src, p_dst, imtype="depth",fps=6)
##gen_video(p_src, p_dst, imtype="mask", fps=6)
##gen_video(p_src, p_dst, imtype="skel",fps=6)
##gen_video(p_src, p_dst, imtype="rgb",fps=6, text=True)

print "video creation complete!"

# use the narturalsorted images to generated video:
##natural_names  = get_natural_imlist(p_src,"depth")
##print len(natural_names)
