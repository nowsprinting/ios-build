#!/usr/bin/env python2.7
#coding=utf-8
#
# Copyright 2012, HUB Systems, Inc.
"""
UnitTest for "Build script for Android project".
"""
__author__ = "Koji Hasegawa"
__copyright__ = "Copyright 2011, HUB Systems, Inc."
__credits__ = ["Koji Hasegawa"]
__license__ = "Apache License Version 2.0"
__version__ = "1.0"

import unittest
import os
import shutil
from build import *

PLIST_PATH = 'Test-Info.plist'
COPYRIGHT_PATH = 'copyright.plist'


class BuildTests(unittest.TestCase):

    def test_plist_read_0_8_3_10(self):
        """通常のInfo.plistファイルの読み込みテスト"""
        try:
            shutil.copyfile('testing/Test_0_8_3_10-Info.plist', PLIST_PATH)
            plist = InfoPlist(PLIST_PATH)
            assert plist.shortVersion == "0.8.3"
            assert plist.buildVersion == 10
        finally:
            #tear down
            os.remove(PLIST_PATH)

    def test_plist_read_1_0(self):
        """通常のInfo.plistファイルの読み込みテスト"""
        try:
            shutil.copyfile('testing/Test_1_0-Info.plist', PLIST_PATH)
            plist = InfoPlist(PLIST_PATH)
            assert plist.shortVersion == "1.0.0"
            assert plist.buildVersion == 0
        finally:
            #tear down
            os.remove(PLIST_PATH)

    def test_plist_write(self):
        """書き込みのテスト"""
        try:
            shutil.copyfile('testing/Test_1_0-Info.plist', PLIST_PATH)
            plist = InfoPlist(PLIST_PATH)
            plist.shortVersion = "1.0.0"
            plist.buildVersion = 10
            plist.write()
            #reload for test
            plist = InfoPlist(PLIST_PATH)
            assert plist.shortVersion == "1.0.0"
            assert plist.buildVersion == 10
        finally:
            #tear down
            os.remove(PLIST_PATH)
        
    def test_buildVersion_read(self):
        """build.versionファイルの読み込みテスト"""
        try:
            shutil.copyfile('testing/build.version', 'build.version')
            buildVersion = BuildVersion()
            assert buildVersion.version == 11
        finally:
            #tear down
            os.remove('build.version')

    def test_buildVersion_no_file(self):
        """build.versionファイルが無い場合のテスト"""
        buildVersion = BuildVersion()
        assert buildVersion.version == 0

    def test_buildVersion_write(self):
        """build.versionファイルの書き込みテスト"""
        try:
            shutil.copyfile('testing/build.version', 'build.version')
            buildVersion = BuildVersion()
            buildVersion.version = 12
            buildVersion.write()
            #reload for test
            buildVersion = BuildVersion()
            assert buildVersion.version == 12
        finally:
            #tear down
            os.remove('build.version')

    def test_copyright_read_2010(self):
        """copyrightファイルの読み込みテスト. toは現在年に上書きされる"""
        try:
            shutil.copyfile('testing/copyright_2010.plist', COPYRIGHT_PATH)
            copyright_plist = Copyright(COPYRIGHT_PATH)
            copyright_plist.update(2012)
            copyright_plist.write()
            #reload for test
            copyright_plist = Copyright(COPYRIGHT_PATH)
            assert copyright_plist.copyright_year_from == 2010
            assert copyright_plist.copyright_year_to == 2012
        finally:
            #tear down
            os.remove(COPYRIGHT_PATH)

    def test_copyright_read_2013(self):
        """copyrightファイルの読み込みテスト. to>現在年のときは上書きしない"""
        try:
            shutil.copyfile('testing/copyright_2013.plist', COPYRIGHT_PATH)
            copyright_plist = Copyright(COPYRIGHT_PATH)
            copyright_plist.update(2012)
            copyright_plist.write()
            #reload for test
            copyright_plist = Copyright(COPYRIGHT_PATH)
            assert copyright_plist.copyright_year_from == 2010
            assert copyright_plist.copyright_year_to == 2013
        finally:
            #tear down
            os.remove(COPYRIGHT_PATH)

    def test_copyright_no_file(self):
        """copyrightファイルが無い場合、新規作成される"""        
        try:
            if os.path.exists(COPYRIGHT_PATH):
                os.remove(COPYRIGHT_PATH)
            copyright_plist = Copyright(COPYRIGHT_PATH)
            copyright_plist.update(2012)
            copyright_plist.write()
            #reload for test
            assert os.path.exists(COPYRIGHT_PATH)
            copyright_plist = Copyright(COPYRIGHT_PATH)
            assert copyright_plist.copyright_year_from == 2012
            assert copyright_plist.copyright_year_to == 2012
        finally:
            #tear down
            os.remove(COPYRIGHT_PATH)

if __name__ == '__main__':
    unittest.main()
