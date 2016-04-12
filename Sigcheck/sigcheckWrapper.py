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
import hashlib
import wx

REF_FILE = "ref.csv"
LOG_FILE = "sigcheckWrapper.log"
RESULTS_FILE = "results.csv"
BUFF_SIZE = 65536
TRAY_TOOLTIP = 'SigCheck has found a discrepancy with your computer certificates!'
TRAY_ICON = 'icon.png'


def writelog(text, logger):
    logger.write(str(datetime.datetime.now()) + ": " + text + '\n')


def checksigs():
    # first, check to see if there is a log file with the same name as LOG_FILE,
    #  if there is, rename it to *.log.bak and delete any old *.log.bak with the
    #  same name:
    if os.path.isfile(LOG_FILE):
        if os.path.isfile(LOG_FILE + ".bak"):
            os.remove(LOG_FILE + ".bak")

        if os.path.isfile(LOG_FILE):
            os.rename(LOG_FILE, LOG_FILE + ".bak")
            # os.remove(LOG_FILE)

    logger = open(LOG_FILE, 'w')
    writelog("Initialized the log file", logger)

    writelog("Running sigcheck on all certificate stores", logger)
    process = Popen(['sigcheck.exe', '-t', '*', '-c'], stdout=PIPE)

    (output, err) = process.communicate()

    exit_code = process.wait()

    if exit_code > 0:
        # the return code was not normal, log the error code.
        writelog("The process did not exit with a known good code exited with: {}".format(exit_code), logger)
        exit()

    # check for errors and an error code
    if err:
        writelog("An error has occurred \n", logger)
        writelog(err)

    writelog("Checking for previous instance of the results file", logger)

    if os.path.isfile(RESULTS_FILE):
        writelog("Deleting the old results file", logger)
        os.remove(RESULTS_FILE)

    writelog("Opening file to save current results to", logger)
    f = open(RESULTS_FILE, 'w')

    # first, split the output into an array of it's lines:
    output = output.splitlines()

    # now, write the contents to the last run file
    for line in output:
        f.write(line)
        f.write('\n')

    f.close()

    f = open(RESULTS_FILE, 'r')

    # now, I need to do the comparison...
    # load up the reference file
    # compare against what we just ran
    # if there are issues, create a notification alert!

    reffile = open(REF_FILE, 'r')

    sha256ref = hashlib.sha256()
    sha256gen = hashlib.sha256()

    while True:
        datagen = f.read(BUFF_SIZE)
        if not datagen:
            break
        sha256gen.update(datagen)

    while True:
        dataref = reffile.read(BUFF_SIZE)
        if not dataref:
            break
        sha256ref.update(dataref)

    if sha256gen.hexdigest() == sha256ref.hexdigest():
        writelog("The files have the same hash {0}".format(sha256gen.hexdigest()), logger)
    else:
        writelog("The files don't match, fire up the notification window", logger)
        app = wx.App()
        TaskBarIcon()
        app.MainLoop()

    writelog("Job completed, closing files...", logger)
    # always remember to close the file!
    f.close()
    reffile.close()
    logger.close()


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Open Sigcheck Folder', self.on_open)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    @staticmethod
    def on_left_down(event):
        Popen('explorer ' + os.getcwd())

    @staticmethod
    def on_open(self, event):
        Popen('explorer ' + os.getcwd())

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)


def main():

    checksigs()

if __name__ == '__main__':
    main()
