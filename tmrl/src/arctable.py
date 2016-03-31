'''
arctable.py
ARCtable_class. description and paramaters for the hdf5 file and tables used
during icu data collection for training.

created 09may2014

author: carlos
'''
import tables as tb
import os


class ARCtable(tb.IsDescription):
    '''The class used to design the ARC data collection tables'''
    globalframe     = tb.Int32Col  (shape=(),   dflt=0, pos=0) # global frame index
    viewframe       = tb.Int32Col  (shape=(),   dflt=0, pos=1) # view frame (resets every new view)
    confidence      = tb.Float32Col(shape=(15,1),       pos=2) # joint confidence
    realworld       = tb.Float32Col(shape=(15,3),       pos=3) # real world joint coordinates (15rows, 3 columns)
    projective      = tb.Float32Col(shape=(15,3),       pos=4) # real world joint coordinates (15rows, 3 columns)
    timestamp       = tb.Float32Col(shape=(),           pos=5) # system time stamp for the frame
    viewangle       = tb.Int32Col  (shape=(),   dflt=0, pos=6) # view angle
    actionlabel     = tb.Int32Col  (shape=(),   dflt=0, pos=7) # action int label
    actorlabel      = tb.Int32Col  (shape=(),   dflt=0, pos=8) # action int label
    actionname      = tb.StringCol (itemsize=(20), shape=(),   dflt=0, pos=9)  # action string name
    actorname       = tb.StringCol  (itemsize=(20), shape=(),   dflt=0, pos=10) # actor string name
    timestring      = tb.StringCol  (itemsize=(40), shape=(),   dflt=0, pos=11) # time as str
