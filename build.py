#!/usr/bin/env python2.7
#coding=utf-8
#
#The MIT License (MIT)
#
#Copyright (c) 2012-2013 HUB Systems, Inc.
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#the Software, and to permit persons to whom the Software is furnished to do so,
#subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
"""
Build script for iOS project.

Usage
    $ build.py
    Create .ipa file following path "bin/<targetname>_<configurationname>_<bundleversion>.ipa"

Processing this script
    1. Update the Info.plist file. Increment CFBundleVerson value.
    2. Create or update the "copyright.plist" file.
    3. Build target.
    4. Create .ipa file to build directory,

Cautions: This script create the following files.
    1. build.version
        This file is record the last CFBundleVersion (of all targets).
        You may wish to add to ".gitignore" file.
    2. ${targetname}-copyright.plist
        You can use this file to the display of copyright in application.
"""
__author__ = "Koji Hasegawa"
__copyright__ = "Copyright 2012-2013 HUB Systems, Inc."
__credits__ = ["Koji Hasegawa"]
__license__ = "MIT License"
__version__ = "1.1"

import shutil
import os
import re
import argparse
import plistlib
from subprocess import check_call
from datetime import datetime

#define Info.plist file path, Targets, and Configurations.
INFO_PLIST_FILE_PATH = '${TARGET_NAME}-Info.plist'
COPYRIGHT_FILE_PATH  = '${TARGET_NAME}-copyright.plist'
DEFAULT_TARGETS = ['Target1', 'Target2']
DEFAULT_CONFIGURATIONS = ["Debug", "Release"]


class InfoPlist:
    """Info.plist file accessor.
        read/write proerties: CFBundleShortVersionString, CFBundleVersion."""
    _SHORT_VERSION  = 'CFBundleShortVersionString'
    _VERSION        = 'CFBundleVersion'

    def __init__(self, path):
        self._path = path
        self._pl = plistlib.readPlist(path)
        self.shortVersion = self._pl[self._SHORT_VERSION]
        while re.search('\d+\.\d+\.\d+', self.shortVersion)==None:
            self.shortVersion = self.shortVersion + ".0"
        try:
            version = self._pl[self._VERSION]
            versions = version.split('.')
            self.buildVersion = int(versions[3])
        except:
            self.buildVersion = 0

    def write(self):
        self.version = self.shortVersion + '.' + str(self.buildVersion)
        self._pl[self._VERSION] = self.version
        plistlib.writePlist(self._pl, self._path)


class BuildVersion:
    """buldl.version file accessor.
        read/write property: version."""
    _FILE_PATH = 'build.version'

    def __init__(self):
        self.version = 0
        read = None
        try:
            read = open(self._FILE_PATH, 'r')
            for line in read:
                matched = re.search('(\d+)', line)
                if matched:
                    self.version = int(matched.group(1))
                    break
        except (IOError,OSError):
            pass
        finally:
            if read:
                read.close()

    def write(self):
        try:
            fp = open(self._FILE_PATH, 'w')
            fp.write(str(self.version) + '\n')
        finally:
            fp.close()


class Copyright:
    """copyright.plist file accessor.
        read/write properties: copyright_year_from, copyright_year_to."""
    _YEAR_FROM  = 'copyright_year_from'
    _YEAR_TO    = 'copyright_year_to'

    def __init__(self, path):
        self._path = path
        if os.path.exists(path):
            self._pl = plistlib.readPlist(path)
        else:
            self._pl = dict(copyright_year_from=0,copyright_year_to=0)
        self.copyright_year_from = self._pl[self._YEAR_FROM]
        self.copyright_year_to   = self._pl[self._YEAR_TO]

    def update(self, year):
        if self.copyright_year_from==0:
            self.copyright_year_from = year
        if self.copyright_year_to<year:
            self.copyright_year_to = year

    def write(self):
        self._pl[self._YEAR_FROM] = self.copyright_year_from
        self._pl[self._YEAR_TO]   = self.copyright_year_to
        plistlib.writePlist(self._pl, self._path)


#make archive (*.ipa file)
def archive2ipa(currentTarget, currentConfig, version):
    os.chdir("build")
    #clean directory.
    try:
        shutil.rmtree("Payload")
    except OSError as err:
        print "skip: {0}".format(err)
        pass
    shutil.copytree(currentConfig + "-iphoneos/" + currentTarget + ".app", "Payload/" + currentTarget + ".app")
    #clean ipa
    ipaname = currentTarget + "_" + currentConfig + "_" + version + ".ipa"
    try:
        os.remove(ipaname)
    except OSError as err:
        print "skip: {0}".format(err)
        pass
    #do zip
    check_call(["zip", "-r", ipaname, "Payload"])
    #clean
    shutil.rmtree("Payload")
    os.chdir("..")


#make archive (*.zip file)
def archive2zip(currentTarget, currentConfig, version):
    os.chdir("build/" + currentConfig + "-iphoneos")
    #clean zip
    zipname = "../" + currentTarget + "_" + currentConfig + "_" + version + ".zip"
    try:
        os.remove(zipname)
    except OSError as err:
        print "skip: {0}".format(err)
        pass
    #do zip
    check_call(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", currentTarget + ".app", zipname])
    os.chdir("../..")


if __name__ == '__main__':
    # Check arguments
    argParser = argparse.ArgumentParser(description='Build script for iOS project.')
    argParser.add_argument('-t', '--target', metavar='NAME', nargs=1, help='build the target NAME')
    argParser.add_argument('-c', '--configuration', metavar='NAME', nargs=1, help='use the build configuration NAME for building each target')
    args = argParser.parse_args()
    
    # Check max build version.
    buildVersion = BuildVersion()
    maxBuildVersion = buildVersion.version
    for target in DEFAULT_TARGETS:
        plistPath = INFO_PLIST_FILE_PATH.replace('${TARGET_NAME}', target)
        infoPlist = InfoPlist(plistPath)
        maxBuildVersion = max(maxBuildVersion, infoPlist.buildVersion)
        
    # Write build version.
    buildVersion.version = maxBuildVersion + 1;
    buildVersion.write()
    
    #Specify build target and configuration.
    if args.target:
        targets = [args.target[0]]
    else:
        targets = DEFAULT_TARGETS
    if args.configuration:
        configurations = [args.configuration[0]]
    else:
        configurations = DEFAULT_CONFIGURATIONS
    
    #Build
    findRelease = re.compile('release')
    for target in targets:
        infoPlistPath = INFO_PLIST_FILE_PATH.replace('${TARGET_NAME}', target)
        infoPlist = InfoPlist(infoPlistPath)
        infoPlist.buildVersion = buildVersion.version
        infoPlist.write()
        copyrightPlistPath = COPYRIGHT_FILE_PATH.replace('${TARGET_NAME}', target)
        copyrightPlist = Copyright(copyrightPlistPath)
        copyrightPlist.update(datetime.today().year)
        copyrightPlist.write()
        
        for configuration in configurations:
            #clean
            check_call(["xcodebuild", "-target", target, "-configuration", configuration, "clean"])
            #build
            check_call(["xcodebuild", "-target", target, "-configuration", configuration, "build"])
            #make archive
            if findRelease.search(configuration.lower())<0:
                archive2ipa(target, configuration, infoPlist.version)
            else:
                archive2zip(target, configuration, infoPlist.version)
