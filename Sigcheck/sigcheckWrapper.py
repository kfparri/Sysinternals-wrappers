'''
Module Name:        sigcheckWrapper
Author:             Kyle Parrish (kfparri@gmail.com)
Module Description: This module acts as a wrapper for sigcheck.  This wrapper will run sigcheck and compare it against
                        a known good list of certificates on the local machine.  If there are not changes, this module
                        does nothing.  If a change is detected, a notifcation will appear in the Windows taskbar.
Version:            0.1
Requirements:       The following will need to be installed on the machine running this script:
                        Python
                        wxPython

Changelog
    Date            Author              Description
================  ===============    ===========================================================================
    3.29.2016       Kyle Parrish        Initial release
'''

from subprocess import Popen, PIPE
import os
import datetime
import filecmp

REF_FILE = "ref.csv"
LOG_FILE = "sigcheckWrapper.log"
RESULTS_FILE = "results.csv"


def writeLog(text):
    logger.write(str(datetime.datetime.now()) + ": " + text + '\n')

# first, check to see if there is a log file with the same name as LOG_FILE,
#  if there is, rename it to *.log.bak and delete any old *.log.bak with the
#  same name:
if os.path.isfile(LOG_FILE):
    if os.path.isfile(LOG_FILE + ".bak"):
        os.remove(LOG_FILE + ".bak")

    if os.path.isfile(LOG_FILE):
        os.rename(LOG_FILE, LOG_FILE + ".bak")
        #os.remove(LOG_FILE)

    logger = open(LOG_FILE, 'w')
    writeLog("Initialized the log file")
else:
    logger = open(LOG_FILE, 'w')
    writeLog("Initialized the log file")

writeLog("Running sigcheck on all certificate stores")
process = Popen(['sigcheck.exe', '-t', '*', '-c'], stdout=PIPE)

(output, err) = process.communicate()

exit_code = process.wait()

if exit_code > 0:
    # the return code was not normal, log the error code.
    writeLog("The process did not exit with a known good code exited with: {}".format(exit_code))
    exit()


# check for errors and an error code
if err:
    writeLog("An error has occurred \n")
    writeLog(err)

writeLog("Checking for previous instance of the results file")

if os.path.isfile(RESULTS_FILE):
    writeLog("Deleting the old results file")
    os.remove(RESULTS_FILE)

writeLog("Opening file to save current results to")
f = open(RESULTS_FILE, 'w')

# first, split the output into an array of it's lines:
output = output.splitlines()

# now, write the contents to the last run file
for line in output:
    f.write(line)
    f.write('\n')

# now, I need to do the comparison...
# load up the reference file
# compare against what we just ran
# if there are issues, create a notification alert!

# I'm going to simply compare the two files, I have not had the certificates appear in a different order yet.
#THIS DOESN'T WORK, I NEED TO DO SOMETHING ELSE HERE:
if filecmp.cmp(REF_FILE, RESULTS_FILE):
    writeLog("The certificate files are the same!  No changes in certificates from the reference file!")
else:
    writeLog("The files don't match!  Displaying an error message!")
    # TODO: More to come here

writeLog("Job completed, closing files...")
# always remember to close the file!
f.close()
logger.close()
