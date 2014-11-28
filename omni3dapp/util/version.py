"""
The version utility module is used to get the current Cura version, and check for updates.
It can also see if we are running a development build of Cura.
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import os
import sys
import urllib2
import platform
import subprocess
try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree

from omni3dapp.util import resources
from omni3dapp.logger import log

def getVersion(getGitVersion = True):
    versionFile = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0], "../version"))

    if getGitVersion:
        gitPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0], ".."))
        try:
            gitProcess = subprocess.Popen(args = "git show -s --pretty=format:%H", shell = True, cwd = gitPath, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            (stdoutdata, stderrdata) = gitProcess.communicate()

            if gitProcess.returncode == 0:
                return stdoutdata
        except:
            pass

    if os.path.exists(versionFile):
        f = open(versionFile, "r")
        version = f.readline()
        f.close()
        return version.strip()
    log.error("Version file {0} was not found. Cannot import profile " \
            "file.".format(versionFile))
    return "." #No idea what the version is. TODO:Tell the user.

def isDevVersion():
    gitPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(
        __file__))[0], "../../.git"))
    hgPath  = os.path.abspath(os.path.join(os.path.split(os.path.abspath(
        __file__))[0], "../../.hg"))
    return os.path.exists(gitPath) or os.path.exists(hgPath)

def checkForNewerVersion():
    if isDevVersion():
        return None
    try:
        updateBaseURL = 'http://software.ultimaker.com'
        localVersion = map(int, getVersion(False).split('.'))
        while len(localVersion) < 3:
            localVersion += [1]
        latestFile = urllib2.urlopen("%s/latest.xml" % (updateBaseURL))
        latestXml = latestFile.read()
        latestFile.close()
        xmlTree = ElementTree.fromstring(latestXml)
        for release in xmlTree.iter('release'):
            os = str(release.attrib['os'])
            version = [int(release.attrib['major']), int(release.attrib['minor']), int(release.attrib['revision'])]
            filename = release.find("filename").text
            if platform.system() == os:
                if version > localVersion:
                    return "%s/current/%s" % (updateBaseURL, filename)
    except:
        #print sys.exc_info()
        return None
    return None

if __name__ == '__main__':
    print(getVersion())
