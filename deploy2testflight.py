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
Upload ipa files to testflightapp.com
"""
__author__ = "Koji Hasegawa"
__copyright__ = "Copyright 2012-2013 HUB Systems, Inc."
__credits__ = ["Koji Hasegawa"]
__license__ = "MIT License"
__version__ = "1.0"

import os
import subprocess
import argparse
import plistlib
import requests


#define Default Targets and Configurations.
DEFAULT_TARGETS = ['Target1','Target2']
DEFAULT_CONFIGURATIONS = ['Debug','Release']

#define TestFlight API token
UPLOAD_API_TOKEN = "your_api_token"
TEAM_TOKEN = "your_team_token"


def ipaFilePath(target,config):
	# we need to convert Info.plist into a xml file (by default it's a binary plist)
    # this logic copied from: https://github.com/jfoucry/xcodebuild-wrapper
    infoPlist = "build/%s-iphoneos/%s.app/Info.plist"%(config,target)
    xmlfile = "/tmp/%s_%s.xml"%(target,config)
    subprocess.Popen('plutil -convert xml1 -o %s %s'%(xmlfile,infoPlist),shell=True).wait()
    infoPlistFile = open(xmlfile, 'r')
    app_plist = plistlib.readPlist(infoPlistFile)
    # Create ipa file name
    return "build/%s_%s_%s.ipa"%(target,config,app_plist['CFBundleVersion'])


def upload(file,notes):
    url = "http://testflightapp.com/api/builds.json"
    data = {'api_token':UPLOAD_API_TOKEN, 'team_token':TEAM_TOKEN, 'notes':notes, 'notify':True}
    ipa = {'file': open(file, 'rb')}
    res = requests.post(url, data=data, files=ipa)
    if res.status_code==200:
        print "done."
    else:
        print res.status_code
        print res.text


if __name__ == '__main__':
    # Check arguments
    argParser = argparse.ArgumentParser(description='Upload ipa files to testflightapp.com script for iOS project.')
    argParser.add_argument('-t', '--target', metavar='NAME', nargs=1, help='build the target NAME')
    argParser.add_argument('-c', '--configuration', metavar='NAME', nargs=1, help='use the build configuration NAME for building each target')
    args = argParser.parse_args()

    # Specify build target and configuration.
    if args.target:
        targets = [args.target[0]]
    else:
        targets = DEFAULT_TARGETS
    if args.configuration:
        configurations = [args.configuration[0]]
    else:
        configurations = DEFAULT_CONFIGURATIONS

    # Create note (commit that has not been merged into the master)
    notes = "Changelog:\n%s"%(os.popen("git log --no-merges --pretty=format:\"- %s\" master..").read())

    # Deploy
    for target in targets:
        for configuration in configurations:
            file = ipaFilePath(target,configuration)
            print "uploading %s..."%(file)
            upload(file,notes)
