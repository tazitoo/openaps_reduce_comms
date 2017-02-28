#!/usr/bin/env python
#
import os
import os.path
import sys
import pandas as pd
#import subprocess
import json
import datetime

#############################################################################
#                           USER DEFINED                                    #
#############################################################################
openapsDir = './'
now = datetime.datetime.now()

basalProfileJSON= openapsDir + 'settings/basal_profile.json'
carbRatiosJSON  = openapsDir + 'settings/carb_ratios.json'
isfJSON         = openapsDir + 'settings/insulin_sensitivities.json'
bgTargetsJSON   = openapsDir + 'settings/bg_targets.json'
enactedJSON     = openapsDir + 'enact/enacted.json'

    

# read user settings from openaps reports - this stuff should be working
try:
    FH = open( basalProfileJSON, 'r')  # [{'ratio': 0.85}] is the format...
    foo = json.load(FH)
    basalDF = pd.DataFrame(foo)
    basalDF = basalDF.set_index(pd.to_datetime(basalDF['start']))   # most interesting column = 'rate'
    FH.close()
    profileBasal = basalDF['rate'].asof( pd.to_datetime(now))
except IOError:
    print ('Did not find basal profile  - will skip basal profile ...')
    
try:
    FH = open( carbRatiosJSON, 'r')  # [{'ratio': 0.85}] is the format...
    foo = json.load(FH)
    carbRatioDF = pd.DataFrame(foo['schedule'])
    carbRatioDF = carbRatioDF.set_index(pd.to_datetime(carbRatioDF['start']))   # most interesting column = 'ratio'
    FH.close()
    profileCarbRatio = carbRatioDF['ratio'].asof(pd.to_datetime(now))
except IOError:
    print ('Did not find carb ratio profile  - will skip carb profile ...')
    
    
try:
    FH = open( isfJSON, 'r')  # [{'ratio': 0.85}] is the format...
    foo = json.load(FH)
    isfDF = pd.DataFrame(foo['sensitivities'])
    isfDF = isfDF.set_index(pd.to_datetime(isfDF['start']))    # most interesting column = 'sensitivity'
    FH.close()
    profileISF = isfDF['sensitivity'].asof(pd.to_datetime(now))
except IOError:
    print ('Did not find ISF profile  - will skip ISF profile ...')
    
try:
    FH = open( bgTargetsJSON, 'r')  # [{'ratio': 0.85}] is the format...
    foo = json.load(FH)
    bgTargetDF = pd.DataFrame(foo['targets'])
    bgTargetDF = bgTargetDF.set_index(pd.to_datetime(bgTargetDF['start']))   # most interesting columns = 'high' & 'low'
    FH.close()
    profileTarget = bgTargetDF['low'].asof(pd.to_datetime(now))
except IOError:
    print ('Did not find target profile  - will skip target profile ...')
    
#print('From pump settings - ')
#print('Basal      = ',   profileBasal)
#print('Carb ratio = ',   profileCarbRatio)
#print('ISF        = ',   profileISF)
#print('Target     = ',   profileTarget)
#
#print()
#print('From openaps enact - ')
#print('Timestamp = ', timestamp)
#print('BG        = ', curBG)
#print('IOB        = ', iob)
#print('COB        = ', cob)
#print('Temp basal = ', predRate)
#print('eventual BG= ', eventualBG)

try:
    FH = open( enactedJSON, 'r')  # [{'ratio': 0.85}] is the format...
    foo        = json.load(FH)
    FH.close()
    iob        = foo['IOB']
    cob        = foo['COB']
    eventualBG = foo['eventualBG']
    predRate   = foo['rate']
    curBG      = foo['bg']
    tick      = foo['tick']
    timestamp  = foo['timestamp']
    myCols = ['timestamp', 'bg', 'basal', 'carbratio', 'isf', 'tick','target', 'iob', 'cob', 'temp_basal', 'eventualBG']
    myList = [[timestamp, curBG, profileBasal, profileCarbRatio, profileISF, tick, profileTarget, iob, cob, predRate, eventualBG]]
    df = pd.DataFrame(myList, columns=myCols)
    csvFile = 'predictions.csv'
    if os.path.isfile(csvFile) :
        with open( csvFile , 'a') as f:
            df.to_csv(f, index=False, header=False)
    else:
        with open( csvFile, 'a') as f:
            df.to_csv(f, index=False, header=True)
except IOError:
    print ('Did not find enacted report  - will skip enacted predictions ...')

