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

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
    
def calculateGap( lastTimeStr ):
    # function looks at time difference from last glucose report and current time
    # returns a float with the number of hours the next report needs to pull data for...
    import datetime
    print 'lastTimeStr = ', lastTimeStr
    lastTime = datetime.datetime.strptime( lastTimeStr, '%Y-%m-%dT%H:%M:%S')
    now           = datetime.datetime.now()
    elapsedTime = now - lastTime 
    totalSecs = elapsedTime.total_seconds()
    safetyFactor = 0.25
    totalHrs = totalSecs/3600.0 + safetyFactor
    print 'Elapsed time - ', elapsedTime, totalSecs, totalHrs
    hourStr   = "{0:.2f}".format( totalHrs )
    return hourStr  
#############################################################################
#                           USER DEFINED                                    #
#############################################################################
    
cgmDevice  = 'pinky'
openapsDir = '/home/brian/trial1/'
histFile   = 'bgHistory.csv'
dailyFile  = 'glucose.json'   # should agree with openaps glucose report name
gapFile    = 'glucose_short.json'  # just the latest data


skipHist   = False
skipGap    = False
glucoseReport = openapsDir + '/monitor/' + dailyFile
print glucoseReport
#
# load existing data
#
try:
    hist = pd.read_csv( histFile ) #, parse_dates=['display_time', 'system_time'] )
except IOError:
    print 'Did not find history file - will skipHist...'
    skipHist = True
#    hist = pd.DataFrame()
    
try:    
    daily = pd.read_json( glucoseReport, convert_dates = False )
except ValueError:
    print 'Did not find daily report - pulling a new one...'
    #
    # this needs to be robust
    #
    os.system( "cd /home/brian/trial1; openaps report invoke monitor/glucose.json")
    daily = pd.read_json( glucoseReport, convert_dates=False )
    skipGap = True


# need to localize timestamps?
# data.tz_localize('utc')

print 'Prep:'
print 'Daily file - ', daily.shape 
print 'skipHist = ', skipHist
if skipHist == False:
    print 'History file - ', hist.shape
print 'skipGap = ', skipGap
#
# figure out how much of a gap we have from last daily report until now
#
if skipGap == False:
    mostRecentReportTime = daily.ix[daily.index[0], 'display_time']#.to_datetime()
    hourStr = calculateGap( mostRecentReportTime )
    print'Gap length = ', hourStr

    # run gap report in openaps
    cdStr     = 'cd ' + openapsDir
    joinStr   = ' ; '
    #
    # this needs to be robust!
    #
    reportStr = ' openaps use ' + cgmDevice + ' iter_glucose_hours ' + hourStr
    cmdStr = cdStr + joinStr + reportStr
    result = subprocess.check_output(cmdStr, shell=True)
    gap    = pd.read_json( StringIO(result) , convert_dates=False)

    print '-----------'
    print 'Gap report - '
    print '-----------'
    print gap
    
    print '-----------'
    print 'Daily report - '
    print '-----------'
    print daily.head(n=5) 
    
# once we have hist, daily and gap file, merge all into single data frame
if skipHist ==  False:
    frames = [hist, daily]
    df = pd.concat( frames, ignore_index=True )
else:
    df = daily.copy()
    
if (skipGap == False) & (gap.shape[0] > 0):
    frames = [df, gap]
    df = pd.concat( frames, ignore_index=True )

df = df.drop_duplicates()
print 'Concated all - ', df.shape

 
# save history file
df.sort(columns=['display_time'], ascending=False, inplace=True)
print '-----------'
print 'Final df concated - '
print '-----------'
print df.head(n=5)

df.to_csv( histFile , index=False)  # avoid writing index column to csv

# save last 300 entries out to current day Openaps glucose report
df.head(n=300).to_json(glucoseReport, orient='records') #, date_format='iso', date_unit='s', orient='records')
