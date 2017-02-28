#/usr/bin/bash
/usr/local/bin/reset_spi_serial.py

OPENAPSDIR=/root/trial1
cd $OPENAPSDIR
#clean up old reports
rm -f enact/suggested.json

# this should be the equivalent to `openaps monitor-cgm`
./bgHistoryDailyGap.py

# get the data from the pump 
#(will make second python script to make DB)
/usr/local/bin/openaps use thumper_ML mmtune
/usr/local/bin/openaps report invoke monitor/clock.json 
/usr/local/bin/openaps report invoke monitor/temp_basal.json 
/usr/local/bin/openaps report invoke monitor/pumphistory.json 
/usr/local/bin/openaps report invoke monitor/iob.json 
/usr/local/bin/openaps report invoke monitor/meal2.json
/usr/local/bin/openaps report invoke monitor/auto-sens.json
/usr/local/bin/openaps report invoke enact/suggested.json
/usr/local/bin/openaps enact

# accumulate data for modeling
echo 'Reading pump settings and predictions...'
./readProfile_v2.py
echo 'Finished up...'

