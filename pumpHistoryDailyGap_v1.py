#!/usr/bin/env python
#
# Current thinking: keep - 
# 1.  historical record of glucose readings  (CSV)
#     (visualize & train model with this...)
# 2. current daily record of glucose (JSON - used by loop for auto-sens)
# 3. mimimal current data pull (JSON minimize data pulled from CGM receiver)

# NOTE: all times dealt with as strings - exception being calculateGap -
# since pandas.to_json would set all times as UTC - and openaps would report CGM data 
#
# will start with glucose (simpler) and move on to pump (harder)...
# and keep time series of every other potentially important variable

import os
import sys
import pandas as pd
import subprocess
import datetime

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
    
def calculateGap( lastTimeStr ):
    # function looks at time difference from last glucose report and current time
    # returns a float with the number of hours the next report needs to pull data for...
    
    print( 'lastTimeStr = ', lastTimeStr )
    lastTime = datetime.datetime.strptime( lastTimeStr, '%Y-%m-%dT%H:%M:%S')
    now           = datetime.datetime.now()
    elapsedTime = now - lastTime 
    totalSecs = elapsedTime.total_seconds()
    safetyFactor = 0.25
    totalHrs = totalSecs/3600.0 + safetyFactor
    print ('Elapsed time - ', elapsedTime, totalSecs, totalHrs)
    hourStr   = "{0:.1f}".format( totalHrs )
    return hourStr  
#############################################################################
#                           USER DEFINED                                    #
#############################################################################
skipHist   = False
skipGap    = False
dia = 3.0  # duration of insulin activity - pump history = 24h + dia  
cgmDevice  = 'share'
pumpDevice = 'thumper_ML'
#openapsDir = '/home2/brian/trial1/'  # on bert
openapsDir = '/home/brian/trial1/'  # on whitey
#openapsDir = '.'
histFile   = 'pumpHistory.csv'
dailyFile  = 'pumphistory.json'   # should agree with openaps pump report name
gapFile    = 'pump_short.json'  # just the latest data

pumpReport = openapsDir + '/monitor/' + dailyFile
#pumpReport = dailyFile
print( pumpReport)
#
# load existing data
#
try:
    hist = pd.read_csv( histFile ) #, parse_dates=['timestamp', 'system_time'] )
except IOError:
    print( 'Did not find history file - will skipHist...')
    skipHist = True
#    hist = pd.DataFrame()
    
try:    
    daily = pd.read_json( pumpReport, convert_dates = False )
except ValueError:
    print( 'Did not find daily report - pulling a new one...')
    #
    # this needs to be robust
    #
    cmdStr = 'cd ' + openapsDir +'; openaps report invoke monitor/' + dailyFile
    os.system( cmdStr )
    daily = pd.read_json( pumpReport, convert_dates=False )
    skipGap = True


# need to localize timestamps?
# data.tz_localize('utc')

print('Prep:')
print( 'Daily file - ', daily.shape )
print ('skipHist = ', skipHist)
if skipHist == False:
    print ('History file - ', hist.shape)
print ('skipGap = ', skipGap)
#
# figure out how much of a gap we have from last daily report until now
#
if skipGap == False:
    mostRecentReportTime = daily.ix[daily.index[0], 'timestamp']#.to_datetime()
    if skipHist == True:
        hourStr = '27'  
    else:
        hourStr = calculateGap( mostRecentReportTime )
    print('Gap length = ', hourStr)

    # run gap report in openaps
    cdStr     = 'cd ' + openapsDir
    joinStr   = ' ; '
    #
    # this needs to be robust!
    #
    reportStr = ' openaps use ' + pumpDevice + ' iter_pump_hours ' + hourStr
    cmdStr = cdStr + joinStr + reportStr
    result = subprocess.check_output(cmdStr, shell=True)
    gap    = pd.read_json( StringIO(result) , convert_dates=False)

#    print ('-----------')
#    print ('Gap report - ')
#    print ('-----------')
#    print (gap)
#    
#    print ('-----------')
#    print ('Daily report - ')
#    print ('-----------')
#    print (daily.head(n=5) )
    
# once we have hist, daily and gap file, merge all into single data frame
if skipHist ==  False:
    frames = [hist, daily]
    df = pd.concat( frames, ignore_index=True )
else:
    df = daily.copy()
    
if (skipGap == False) & (gap.shape[0] > 0):
    frames = [df, gap]
    df = pd.concat( frames, ignore_index=True )

print ('Concated all - ', df.shape)
df = df.drop_duplicates(subset=['_description'])
print ('Deduped all - ', df.shape)

 
# save history file
df.sort(columns=['timestamp'], ascending=False, inplace=True)
print ('-----------')
print ('Final df concated - ')
print ('-----------')
print (df.head(n=5) )

df.to_csv( histFile , index=False)  # avoid writing index column to csv

# save last 300 entries out to current day Openaps glucose report
# so a static count probably is not enough for pumphistory...figure out how much
# is 24hrs of pumphistory
now    = datetime.datetime.now()
oneDay = datetime.timedelta(days=1)
diaHours = datetime.timedelta(hours=dia)
yesterday = now - oneDay - diaHours
yStr = datetime.datetime.strftime( yesterday, '%Y-%m-%dT%H:%M:%S')
df[df['timestamp'] > yStr].to_json(pumpReport, orient='records')
#df.head(n=300).to_json(pumpReport, orient='records') #, date_format='iso', date_unit='s', orient='records')
