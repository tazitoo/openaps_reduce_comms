#!/usr/bin/env python

import os
import pandas as pd 
import datetime  
def truncateFile( origFile, asofTime, timeCol):
    myDateStr = asofTime.strftime('%Y-%m-%d')
    df        = pd.read_csv( origFile , parse_dates=[timeCol])    
    dfToKeep  = df[df[timeCol] > asofTime]
    datedFile = origFile.split('.')[0] + '_' + myDateStr + '.'+ origFile.split('.')[1]
    os.rename( origFile, datedFile )
    dfToKeep.to_csv( origFile, index=False)
    return
    
#############################################################################
#                           USER DEFINED                                    #
#############################################################################
# duplicate the history files with original name + date ()
# save the last nHours of data to history files 
nHours = 30
now       = datetime.datetime.now()
asofTime  = now - datetime.timedelta(hours = nHours)
myDateStr = asofTime.strftime('%Y-%m-%d')

bgFile   = 'bgHistory.csv'
truncateFile( bgFile, asofTime, 'display_time')

predFile  = 'predictions.csv'   # should agree with openaps glucose report name
truncateFile( predFile, asofTime, 'timestamp')
