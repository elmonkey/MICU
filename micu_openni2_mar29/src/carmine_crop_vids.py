'''
Created on Apr 14, 2014
Crop & Generate videos with added captions

Allow user to enter a starting frame and ending frame
1) rgb
2) depth
3) mask
dependiencies: openni, opencv, numpy

@author: Carlos
'''
##!/usr/bin/python

import os, cv2
import numpy as np


p_src ="../data/icuTVframes/" # folder where to get frames
#p_dst ="../data/cropvideos/" # folder where to save video


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


def flipLRImagesInList(imlist):
    '''Given a list of images, flip the pixels elements left to right to fix the
    perspeective error while recording'''
    for image in imlist:
        im = cv2.imread(image)
        im = np.fliplr(im)
        cv2.imwrite(image,im)
    print "Done flipping pixels in images from given list"
#flipLRImagesInList

# use the narturalsorted images to generated video:
rgbs   = get_natural_imlist(p_src,"rgb")
depths = get_natural_imlist(p_src,"depth")
skels  = get_natural_imlist(p_src,"skel")
masks  = get_natural_imlist(p_src,"mask")
all = [rgbs,depths,masks,skels]

print len(rgbs)
flipLRImagesInList(rgbs)
print "done with rgbs"
flipLRImagesInList(depths)
print "done with depths"
flipLRImagesInList(masks)
print "done with masks"

