import os

def createFolders(actor='patient_0'):
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
    
    ## Two storage locations: media or local
    if len(os.listdir('/media/')) >0:
        #sdcard = os.listdir('/media/')[0]
        #if len(os.listdir('/media/'+usr))>0: #check to see if there are any cards
        sdcard = os.listdir('/media/')[0]
        media = '/media/'+sdcard+'/'
        root = media+'icudata1/'
        storage = 'External'
    else: #if not, then save on local hdd
        usr = os.listdir('/home/')[0]
        local = '/home/'+usr+'/Documents/Python/openni2_omap/ICU_omap_v2/'
        root = local+'icudata1/'
        storage='Local'
    #end ifsdcards
    
    ## check existence of directory.
    name,idx = actor.split('_')    
    folder = root+actor
    done = False
    while not done:
        if os.path.isdir(folder):
            'Directory exists {}... renaming!'.format(folder)
            name,idx = actor.split('_')
            idx = str(int(idx)+1)
            print idx
            actor = ('_').join([name,idx])
            folder = root+actor
            
        else:
            print 'Directory {} Doesnt Exist. Creating It'.format(folder)
            folder4frames = folder+'/frames/'
            folder4csv    = folder+'/csv/'
            os.makedirs(folder4frames+'/rgb/')
            os.makedirs(folder4frames+'/depth/')
            os.makedirs(folder4csv)
            done = True
    print '{} storage location {}'.format(storage, root)
    print 'Directory for frames: {}'.format(folder4frames)
    print 'Directory for csv file: {}'.format(folder4csv)
    return folder4frames,folder4csv
# createFolders()

if __name__ == '__main__':
    createFolders(actor='patient_0')

