# openaps_reduce_comms
Helper scripts to reduce communications with CGM and pump.

I use openaps as a predictive model controller to manage my blood sugar/T1D.  I use advanced features (auto-sensitivity and advanced meal assist) that require relatively long historical records from my CGM and my pump.

The issue: 
* My loop to gather the data runs every 3 minutes - yet each time it runs, I pull 1 day of data.  Any existing data from pre-existing reports is deleted and renewed.  This lack of reuse seems to reduce robustness (communications with pump and CGM can be problematic) - and I'm guessing also leads to reduced battery life since we are doing longer communication.

* My loop is entirely independent of any external sources - it runs entirely off-line.  The availability of wifi and even cell phone service is not guaranteed - but I will always have a need to manage T1D.  Part of that management is understanding how you have been responding to food and insulin in the past (many people use Nightscout for this...).  

* Current wisdom on intend-to-bolus thinks that shareble is too unstable to use in offline "camping mode".  Using the current script to minimize the amount of data pulled from the CGM, shareble is typically stable for a week before needing to reboot.

A fix:  use some python scripts to manage the data flow.  Save existing reports off to a CSV file, calculate how much extra data is needed for any new report, and fetch just that much from CGM/pump.

The end goal:
- improve communication robustness
- provide historical data for further analysis (visualisation and predictive models)

Current status:
* bgHistoryDailyGap.py - working 
* readProfile_v2.py - working
* shell script (reduceComms.sh) that implements loop with minimal CGM communication - working

