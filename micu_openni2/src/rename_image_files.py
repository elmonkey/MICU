# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 20:26:25 2014

correct and renames the files under a path/folder.


@author: carlos
"""

import os

# generate a list of image_filenames of all the images in a folder
def get_imlist(path,ext='.png'):
    """ Returns a list of filenames for all jpg images in a directory."""
    return [os.path.join(path,f) for f in os.listdir(path) if f.endswith(ext)]
#get_imlist


if __name__== "__main__":
    path= "/media/carlos/My Book/DataSets/Sleep/victor/top_view/vic/screenshoots/"
    offset = len(get_imlist(path))/4
    path= "/media/carlos/My Book/DataSets/Sleep/victor/top_view/vic0_p3/state/screenshoots/"
    # get current working directory
    #os.getcwd()
    offset = 216
    # listing directories
    names_list =  get_imlist(path)
    for name in names_list:
        n = name.split('_')[-1].split('.')[0]
        newname = name.replace("vic0_p3/state","vic").replace(n, str(int(n)+offset))
        
        print "name:", name
        print "\tnewname: ", newname
#        os.renames(name, newname)
    print "====== offset: ", offset
