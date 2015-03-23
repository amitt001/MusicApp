#!/usr/bin/env python

'''
HDF5 to JSON
'''

import sys
import os
import shutil
import json

try:
    import pandas as pd
except:
    print 'Module Pandas is not installed'

try:
    import numpy as np
except:
    print 'Module Numpy is not installed'

###################################################

class hdfconvert:
    
    '''
    Converts the content of HDF5 file into JSON.
    Convert to JSON in same pattern as stored in 
    HDF5 file.
    '''
    
    def __init__(self):
        pass

    def htoj(self, hdf):
        
        '''
        main workshore to convert HDF5 to JSON.

        Creates a directory named HDFtoJSON-inside it creates a subdirectory
        with same name as HDF file name.
        
        In this directory json files are created with group name at the root
        of HDF file.
        '''
        
        if not os.path.splitext(hdf)[-1] == '.h5':
            print os.path.splitext(hdf)[-1]
            return

        fileName = os.path.splitext(os.path.split(hdf)[-1])[0]
        saveDir = os.path.abspath('./HDFtoJSON')
        fileSubDir = saveDir + '/' + fileName
        os.mkdir(fileSubDir)

        with pd.HDFStore(hdf, 'r') as store:
            for key in store.keys():
                jsonfile = fileSubDir + '/' + key.split('/')[1]
                with open(jsonfile, 'w') as jobj:
                    frame = json.loads(pd.DataFrame.to_json(store.get(key)))
                    json.dump(frame, jobj)

    def help(self):
        print ('Run with HDF5 file or directory containing HDF5 File\n')
        print ('For Ex: \n\npython ' + os.path.basename(__file__) + ' hdf_file.h5/dir_name\n')



if __name__ == '__main__':
    
    dirName = 'HDFtoJSON'
    try:
        os.mkdir(dirName)
    except OSError, e:
        print ('\nDirectory HDFtoJSON already exists\n')
        choice = str(raw_input('Replace (Y/n)'))
        if choice == 'Y' or choice == 'y':
            try:
                os.rmdir(dirName)
            except OSError, e:
               shutil.rmtree(dirName, ignore_errors=True) 
            os.mkdir(dirName)
        else:
            sys.exit(1)
    try:
        hdf = sys.argv[1]
        if hdf == '-h':
            hdfconvert().help()
        
        elif os.path.splitext(hdf)[1] == '.h5':
            hdf = os.path.abspath(hdf)
            json_output = hdfconvert().htoj(hdf)

        elif os.path.splitext(hdf)[1] != '':
            hdfconvert().help()

        else:
            hdf = os.path.abspath(hdf)
            for i,j,k in os.walk(hdf):
                if not j:
                    for l in k:
                        print i + '/' + l,
                        fileloc = i+'/'+l
                        hdfconvert().htoj(fileloc)
                        print '...Done'
                
    except IndexError, e:
        print '\nNo Data Found. Add option -h for help\n'

