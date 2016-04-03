#!/usr/bin/python
'''
Created on Nov 6, 2013

@author: carlos <carlitos408@gmail.com>
'''
import cv2
import numpy as np
import os

def get_nat_list(path, name="file", ext = ".txt"):
    """ 
    Returns a list of PATHS for all fils w the given sub-strings
    in NATURAL ORDER located in the given path.
    usage:
    for folder with files named: [filename0.txt, filename1.txt,... ,filenameN.txt]
    files = get_nat_list('../root/data/', 'filename','.txt') 
    (str,str,str) -> (list)
    """
    # list of paths:
    paths = [os.path.join(path,f) for f in os.listdir(path) if (( f.endswith(ext) or f.endswith(ext.upper())) 
           and (f.count(name)>0 ) )]
    print len(paths)
    paths = sorted(paths, key=lambda x:int(x.split('/')[-1].split(name)[1].split(".")[0]))
    # list of paths:
    names = sorted([ p.split('/')[-1] for p in paths ])
    # images idx numbers:
    idx = sorted([ p.split('/')[-1].split(name)[1].split(".")[0] for p in paths ])
    if len(names)== 0:
        print " === No images with {} under path {} were found!===".format(name, path)
    idx = np.asarray(idx,dtype=int)
    #idx.sort() # sort the indexes in ascending order
    return paths, idx, #paths
#get_nat_list

def gen_video(p_src, p_dst, vidname='test', imtype="rgb_", fps=10, text=False):
    """
    Generates a .avi video file using the images in the path folder.
    inputs:
        p_src:= str, path to images/frames folder
        p_dst:= str, path to folder where avi will be stored
        imtype:= str, one of 2 types {rgb, depth}
        fps:= int, video speed in frames per second
        text= bool, generate video w text message "TESTING: +'frame #'"
        aviname:= str, name of the output video without the extension (.avi)
    (str,str,int,str) -> null
    """
    # Text Color
    green  = (0,255,0)
    winName = 'Input With frame Number'
    
    # use the narturalsorted images to generated video:
    paths,idxs = get_nat_list(p_src, name=imtype, ext='.png' )
    
    im = cv2.imread(paths[0])
    w, h, l = im.shape
    
    # object that contains the properties of the avi
    fourcc=cv2.cv.CV_FOURCC('X','V','I','D')
    ##writer = cv2.VideoWriter(filename= p_dst+aviname+".avi",
    ##    fourcc=cv2.cv.CV_FOURCC('I','Y','U','V'), fps=fps, frameSize=(w,h))
    ##writer = cv2.VideoWriter(filename= p_dst+aviname+".avi",
    ##    fourcc=cv2.cv.CV_FOURCC('X','V','I','D'), fps=fps, frameSize=(w,h))
    #writer = cv2.VideoWriter(p_dst+aviname+".avi",fourcc, fps, (w,h))
    
    
    video = cv2.VideoWriter(p_dst+vidname+".avi",fourcc, fps=fps, frameSize=(h,w))

##    video = cv2.VideoWriter(vidname+".avi",
##        fourcc=cv2.cv.CV_FOURCC('M','J','P','G'), fps=fps, frameSize=(h,w))

    for p in paths[:2850]:
#        print p 
        n, idx = p.split('/')[-1].split('.')[0].split('_')
        #print "frame: {}, idx: {}".format(n,idx)
        im = cv2.imread(p)
        im4display = im.copy()

        # Captions and circle
        if text:
            cv2.putText(im4display,"frame_"+idx,(20,220), cv2.FONT_HERSHEY_PLAIN, 1.5, green,
                        thickness=1, lineType=cv2.CV_AA)
        # if_text
        # Display images
        cv2.imshow(winName, im4display)
        cv2.waitKey(1)        
        video.write(im4display) # write to vid file
    # for_p
    video.release()        
    cv2.destroyAllWindows()
    print "Video generated, check path: ", p_dst
#gen_video



#EXECUTE:
if __name__=="__main__":
    #paths = ["/media/carlos/BlueHdd/Eye-CU/icu_eva/icudev1/patient1/screenshoots/" ]
    #vidnames=["icudev1"]
    path_dst = '/media/carlos/BlueHdd/Eye-CU/icu_eva/icudev1/patient1/videos/'
    vidnames = ["icudev"+str(x) for x in range (1,2)]
    #paths = ["/media/carlos/BlueHdd/Eye-CU/icu_eva/icudev1/patient1/screenshoots/" ]    
    for vidname in vidnames:
        path_src = "/media/carlos/BlueHdd/Eye-CU/icu_eva/"+vidname+"/patient1/screenshoots/"
        print "Currently processing files from: {} and creating video: {}.".format(path_src, vidname)
        gen_video(path_src, path_dst, vidname, imtype="rgb_",fps=15.0, text=True)    
        #paths,idxs = get_nat_list(path_src, name='rgb_', ext='.png' )
        #print "There are {} images in the path \n\t{}".format(len(idxs), path_src)
        
        print 'CODE EXECUTION COMPLETED for !', path_src
    cv2.destroyAllWindows()
#execute

