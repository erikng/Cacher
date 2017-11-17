#!/usr/bin/python

from datetime import date, timedelta
from distutils.version import LooseVersion
import glob
import json
import logging
import optparse
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib2
import StringIO

"""Cacher rewritten in Python.
Inspired by Michael Lynn https://gist.github.com/pudquick/ffdbdb52ae6960ca8e55
This script will process Caching Server Debug Logs.
You can output this data to stdout, send it to the Apple email alert mechanism,
or send to a slack channel.
Slack section adapted from another one of my tools (APInfo).
https://github.com/erikng/scripts/tree/master/APInfo
Author: Erik Gomez
Last Updated: 06-08-2017

Updated version for High Sierra
Author: Joseph Clark
Last Updated: 11-17-2017
"""
version = '3.0.4'


def cacher(lines, targetDate, friendlyNames):
    # Basically run through all the lines a single time and collect all the
    # relevant data to slice, do stats with, etc.
    noClientIdentityLog = []
    sizeLog = []
    AC2Log = []
    IPLog = []
    OSLog = []
    osVersionLog = []
    iOSModelLog = []
    iOSModelOnlyLog = []
    fileTypeLog = []
    fileTypeUniqueLog = []
    urlLog = []
    urlUniqueLog = []
    deviceNumberLog = []
    finalOutput = []
    FriendlyLog = []
    macOSFamilyLog = []
    macOSDeviceNumber = []
    iOSFamilyLog = []
    iOSDeviceNumber = []
    AppleTVNumberLog = []
    iPadNumberLog = []
    iPhoneNumberLog = []
    iPodNumberLog = []
    # Friendly Darwin versions for macOS. This allows us to dynamically add
    # the macOS version (for the alert), while dynamically looping through the
    # logs.
    friendlyDarwin = {
        '17.0.0': '10.13.0',
        '16.7.0': '10.12.6',
        '16.6.0': '10.12.5',
        '16.5.0': '10.12.4',
        '16.4.0': '10.12.3',
        '16.3.0': '10.12.2',
        '16.1.0': '10.12.1',
        '16.0.0': '10.12.0',
        '10.12': '10.12.0',  # match 10.12 to 10.12.0 for consistency
        '15.6.0': '10.11.6',
        '15.5.0': '10.11.5',
        '15.4.0': '10.11.4',
        '15.3.0': '10.11.3',
        '15.2.0': '10.11.2',
        '15.0.0': '10.11.0/1',
        '14.5.0': '10.10.5',
        '14.4.0': '10.10.4',
        '14.3.0': '10.10.3',
        '14.1.1': '10.12.2',
        '14.1.0': '10.10.2',
        '14.0.0': '10.10.0/1',
    }
    # Friendly Models of known models. This allows us to dynamically add the
    # names to each model (for the alert), while dynamically looping through
    # the logs.
    friendlyModels = {
        'AppleTV3,1': '3rd Generation Apple TVs',
        'AppleTV3,2': '4th Generation Apple TVs',
        'AppleTV5,3': '5th Generation Apple TVs',
        'iPhone3,1': 'iPhone 4 [GSM]',
        'iPhone3,2': 'iPhone 4 [GSM 2012]',
        'iPhone3,3': 'iPhone 4 [CDMA]',
        'iPhone4,1': 'iPhone 4S',
        'iPhone5,1': 'iPhone 5 [GSM]',
        'iPhone5,2': 'iPhone 5 [CDMA]',
        'iPhone5,3': 'iPhone 5C',
        'iPhone5,4': 'iPhone 5C [Global]',
        'iPhone6,1': 'iPhone 5S',
        'iPhone6,2': 'iPhone 5S [China Model]',
        'iPhone7,1': 'iPhone 6 Plus',
        'iPhone7,2': 'iPhone 6',
        'iPhone8,1': 'iPhone 6S',
        'iPhone8,2': 'iPhone 6S Plus',
        'iPhone8,4': 'iPhone SE',
        'iPhone9,1': 'iPhone 7 [Global]',
        'iPhone9,2': 'iPhone 7 Plus [Global]',
        'iPhone9,3': 'iPhone 7 [GSM]',
        'iPhone9,4': 'iPhone 7 Plus [GSM]',
        'iPhone10,1': 'iPhone 8 [Global]',
        'iPhone10,2': 'iPhone 8 Plus [Global]',
        'iPhone10,3': 'iPhone X [Global]',
        'iPhone10,4': 'iPhone 8 [GSM]',
        'iPhone10,5': 'iPhone 8 Plus [GSM]',
        'iPhone10,6': 'iPhone X [GSM]',
        'iPad2,1': 'iPad 2nd Generation [Wifi]',
        'iPad2,2': 'iPad 2nd Generation [Wifi + GSM]',
        'iPad2,3': 'iPad 2nd Generation [Wifi + CDMA]',
        'iPad2,4': 'iPad 2nd Generation [M2012 Wifi Revision]',
        'iPad2,5': 'iPad Mini 1st Generation [Wifi]',
        'iPad2,6': 'iPad Mini 1st Generation [Wifi + GSM]',
        'iPad2,7': 'iPad Mini 1st Generation [Wifi + CDMA]',
        'iPad3,1': 'iPad 3rd Generation [Wifi]',
        'iPad3,2': 'iPad 3rd Generation [Wifi + GSM]',
        'iPad3,3': 'iPad 3rd Generation [Wifi + CDMA]',
        'iPad3,4': 'iPad 4th Generation [Wifi]',
        'iPad3,5': 'iPad 4th Generation [Wifi + GSM]',
        'iPad3,6': 'iPad 4th Generation [Wifi + CDMA]',
        'iPad4,1': 'iPad Air 1st Generation [Wifi]',
        'iPad4,2': 'iPad Air 1st Generation [Wifi + Cellular]',
        'iPad4,3': 'iPad Air 1st Generation [China Model]',
        'iPad4,4': 'iPad Mini 2nd Generation [Wifi]',
        'iPad4,5': 'iPad Mini 2nd Generation [Wifi + Cellular]',
        'iPad4,6': 'iPad Mini 2nd Generation [China Model]',
        'iPad4,7': 'iPad Mini 3rd Generation [Wifi]',
        'iPad4,8': 'iPad Mini 3rd Generation [Wifi + Cellular]',
        'iPad4,9': 'iPad Mini 3rd Generation [China Model]',
        'iPad5,1': 'iPad Mini 4th Generation [Wifi]',
        'iPad5,2': 'iPad Mini 4th Generation [Wifi + Cellular]',
        'iPad5,3': 'iPad Air 2nd Generation [Wifi]',
        'iPad5,4': 'iPad Air 2nd Generation [Wifi + Cellular]',
        'iPad6,3': 'iPad Pro 9.7 Inch 1st Generation [Wifi]',
        'iPad6,4': 'iPad Pro 9.7 Inch 1st Generation [Wifi + Cellular]',
        'iPad6,7': 'iPad Pro 12.9 Inch 1st Generation [Wifi]',
        'iPad6,8': 'iPad Pro 12.9 Inch 1st Generation [Wifi + Cellular]',
        'iPad6,11': 'iPad 5th Generation [Wifi]',
        'iPad6,12': 'iPad 5th Generation [Wifi + Cellular]',
        'iPad7,1': 'iPad Pro 12.9 Inch 2nd Generation [Wifi]',
        'iPad7,2': 'iPad Pro 12.9 Inch 2nd Generation [Wifi + Cellular]',
        'iPad7,3': 'iPad Pro 10.5 Inch 1st Generation [Wifi]',
        'iPad7,4': 'iPad Pro 10.5 Inch 1st Generation [Wifi + Cellular]',
        'iPod5,1': 'iPod Touch 5th Generation',
        'iPod7,1': 'iPod Touch 6th Generation'
    }
    totalbytesserved = []
    totalbytesfromorigin = []
    totalbytesfrompeers = []
    for x in lines:
        # If there aren't at least 3 pieces somehow, they'll get filled in
        # with blanks
        datestr, timestr, logmsg = (x.split(' ', 2) + ['', '', ''])[:3]
        if datestr == targetDate:
            # Only do work if the string is on the date we care about
            # try:
                linesplit = str.split(logmsg)
                # split the logmsg line (by spaces) so I can hardcode some
                # calls. Fragile (could break with a Server update) but it meh.

                # Beginning of Server bandwidth section
                #
                # This is a slightly less fragile method to calculate the
                # amount of data the caching server has served.
                # Eg:
                # Served all 39.2 MB of 39.2 MB; 3 KB from cache,
                # 39.2 MB stored from Internet, 0 bytes from peers
                if 'Served all' in logmsg:
                    total_served_size = linesplit[12]
                    total_served_bwtype = linesplit[13][:-1]
                    fromorigin_size = linesplit[17]
                    fromoriginbwtype = linesplit[13][:-1]
                    frompeers_size = linesplit[21]
                    frompeersbwtype = linesplit[13][:-1]
                    # Convert size of served to client to bytes
                    if total_served_bwtype == 'KB':
                        bytes_served = "%.0f" % (
                            float(total_served_size) * 1024)
                    elif total_served_bwtype == 'MB':
                        bytes_served = "%.0f" % (
                            float(total_served_size) * 1048576)
                    elif total_served_bwtype == 'GB':
                        bytes_served = "%.0f" % (
                            float(total_served_size) * 1073741824)
                    elif total_served_bwtype == 'TB':
                        bytes_served = "%.0f" % (
                            float(total_served_size) * 1099511627776)
                    elif total_served_bwtype == 'bytes':
                        bytes_served = total_served_size
                    # Convert size of from internet(origin) to bytes
                    if fromoriginbwtype == 'KB':
                        bytesfromorigin = "%.0f" % (
                            float(fromorigin_size) * 1024)
                    elif fromoriginbwtype == 'MB':
                        bytesfromorigin = "%.0f" % (
                            float(fromorigin_size) * 1048576)
                    elif fromoriginbwtype == 'GB':
                        bytesfromorigin = "%.0f" % (
                            float(fromorigin_size) * 1073741824)
                    elif fromoriginbwtype == 'TB':
                        bytesfromorigin = "%.0f" % (
                            float(fromorigin_size) * 1099511627776)
                    elif fromoriginbwtype == 'bytes':
                        bytesfromorigin = fromorigin_size
                    # Convert size of from peers to bytes
                    if frompeersbwtype == 'KB':
                        bytesfrompeers = "%.0f" % (
                            float(frompeers_size) * 1024)
                    elif frompeersbwtype == 'MB':
                        bytesfrompeers = "%.0f" % (
                            float(frompeers_size) * 1048576)
                    elif frompeersbwtype == 'GB':
                        bytesfrompeers = "%.0f" % (
                            float(frompeers_size) * 1073741824)
                    elif frompeersbwtype == 'TB':
                        bytesfrompeers = "%.0f" % (
                            float(frompeers_size) * 1099511627776)
                    elif frompeersbwtype == 'bytes':
                        bytesfrompeers = frompeers_size
                    # Append each bw size to the total count
                    totalbytesserved.append(bytes_served)
                    totalbytesfromorigin.append(bytesfromorigin)
                    totalbytesfrompeers.append(bytesfrompeers)
                # Search through the logs for incomplete transactions (served)
               #
                if 'Served all' not in logmsg and ' Served ' in logmsg:
                    total_served_size = linesplit[12]
                    total_served_bwtype = linesplit[13][:-1]
                    fromorigin_size = linesplit[17]
                    fromoriginbwtype = linesplit[13][:-1]
                    frompeers_size = linesplit[21]
                    frompeersbwtype = linesplit[13][:-1]
                    # Convert size of from cache to bytes
                    if total_served_bwtype == 'KB':
                        bytes_served = "%.0f" % (
                            float(total_served_size) * 1024)
                    elif total_served_bwtype == 'MB':
                        bytes_served = "%.0f" % (
                            float(total_served_size) * 1048576)
                    elif total_served_bwtype == 'GB':
                        bytes_served = "%.0f" % (
                            float(total_served_size) * 1073741824)
                    elif total_served_bwtype == 'TB':
                        bytes_served = "%.0f" % (
                            float(total_served_size) * 1099511627776)
                    elif total_served_bwtype == 'bytes':
                        bytes_served = total_served_size
                    # Convert size of from internet(origin) to bytes
                    if fromoriginbwtype == 'KB':
                        bytesfromorigin = "%.0f" % (
                            float(fromorigin_size) * 1024)
                    elif fromoriginbwtype == 'MB':
                        bytesfromorigin = "%.0f" % (
                            float(fromorigin_size) * 1048576)
                    elif fromoriginbwtype == 'GB':
                        bytesfromorigin = "%.0f" % (
                            float(fromorigin_size) * 1073741824)
                    elif fromoriginbwtype == 'TB':
                        bytesfromorigin = "%.0f" % (
                            float(fromorigin_size) * 1099511627776)
                    elif fromoriginbwtype == 'bytes':
                        bytesfromorigin = fromorigin_size
                    # Convert size of from peers to bytes
                    if frompeersbwtype == 'KB':
                        bytesfrompeers = "%.0f" % (
                            float(frompeers_size) * 1024)
                    elif frompeersbwtype == 'MB':
                        bytesfrompeers = "%.0f" % (
                            float(frompeers_size) * 1048576)
                    elif frompeersbwtype == 'GB':
                        bytesfrompeers = "%.0f" % (
                            float(frompeers_size) * 1073741824)
                    elif frompeersbwtype == 'TB':
                        bytesfrompeers = "%.0f" % (
                            float(frompeers_size) * 1099511627776)
                    elif frompeersbwtype == 'bytes':
                        bytesfrompeers = frompeers_size
                    # Append each bw size to the total count
                    totalbytesserved.append(bytes_served)
                    totalbytesfromorigin.append(bytesfromorigin)
                    totalbytesfrompeers.append(bytesfrompeers)
                # Beginning of Server downloads section
                #
                if 'Received GET request by' in logmsg:
                    noClientIdentityLog.append(logmsg)
                elif 'Received GET request from' in logmsg:
                    # Beginning of IP section
                    #
                    #
                    # Ex: '149.166.73.137:56833'. Split 6th string at ':' and
                    # pull only pull first value.
                    ip = linesplit[13].split(":")[0]
                    IPLog.append(ip)
                    #
                    #
                    # End of IP section

                    # Beginning of URL section
                    #
                    #
                    # The URL is always at the end so take the split line and
                    # pull its value.
                    URL = linesplit[-1]
                    urlLog.append(URL)
                    #
                    #
                    # End of URL section

                    # Beginning of OS Family, OS Version and Device section
                    #
                    #
                    # Example: 'Darwin/15.0.0', 'iOS/10.0.2' or 'OS X 10.12.0'
                    # Replace Look for iOS, Darwin or OS X. If OS X is found,
                    # Add 'macOS/' to force the consistency and split the
                    # string at '/'. This allows us to use 'macOS/10.12.2' for
                    # both osFamily (Ex: macOS) and osVersion (Ex: 10.12.2).
                    osFamily = re.match(
                        r'.+? ((iOS|Darwin|OS X)[/ ](([0-9]+\.?){1,}))',
                        x)
                    if osFamily is not None:
                        osFamily = osFamily.group(1).replace(
                            'OS X ', 'macOS/').split('/')[0]

                    osVersion = re.match(
                        r'.+? ((iOS|Darwin|OS X)[/ ](([0-9]+\.?){1,}))',
                        x)
                    if osVersion is not None:
                        osVersion = osVersion.group(1).replace(
                            'OS X ', 'macOS/').split('/')[1]

                    configurator = re.match(
                        r'.+?((Configurator)[/ ](([0-9]+\.?){1,}))',
                        x)
                    if configurator is not None:
                        configurator = configurator.group(1).split('/')[0]
                    # If 'Darwin' in the name, replace to 'macOS' so our future
                    # counts will be accurate.
                    if osFamily == 'Darwin':
                        osFamily = 'macOS'
                    # Loop through the friendlyDarwin key/value pairs and if
                    # osVersion is equal to the key (Ex: 16.3.0) replace it
                    # with its value (Ex: 10.12.2). This is also a fix for the
                    # count. Yay for coding in a bubble!
                    if osVersion is not None:
                        for k, v in friendlyDarwin.items():
                            if k == osVersion:
                                osVersion = v

                    # The iOS family is more fun, in that Caching Server logs
                    # the model identifier.
                    if osFamily == 'iOS':
                        # Ex: 'model/iPhone7,2'.
                        iOSModel = re.match(
                            r'.+? model/([^ ]+?[0-9]+,?[0-9])?', x)
                        # Since the regular expression is now two goups, only
                        # take the date from the 2nd group.
                        # Write the osVersion/osFamily data to iOSModelLog,
                        # iOSModelOnlyLog and OSLog.
                        iOSModelLog.append((osVersion, iOSModel.group(1)))
                        iOSModelOnlyLog.append(iOSModel.group(1))
                        OSLog.append((osVersion, osFamily))
                    elif osFamily == 'macOS':
                        # Write the osVersion/osFamily data to OSLog.
                        OSLog.append((osVersion, osFamily))
                    elif configurator == 'Configurator':
                        AC2Log.append(configurator)

                    # if 'model/AppleTV' in logmsg:
                    # I think I still need to do this section but I can't
                    # remember.
                    #
                    #
                    # End of OS Family, OS Version and Device section

                    # Beginning of File Type section
                    #
                    #
                    # Regular Expression Part. Using the URL (split early),
                    # Look for the recognized filetypes (.pkg, .ipa, .ipsw,
                    # .zip and .epub). Ex:
                    # 1. '/a-09f98d6971/pre-thinned756.thinned.signed.dpkg.ipa'
                    # 2. '/031-8/com_apple_MobileAsset_CoreSuggestion/6c93.zip'
                    # 3. '[icloud:hvRq3yMBV7JO9hUBRo2p]'
                    if re.match(r'.+(\.pkg|\.ipa|\.ipsw|\.zip|\.epub)', URL):
                        fileType = re.match(
                            r'.+(\.pkg|\.ipa|\.ipsw|\.zip|\.epub)', URL)
                        fileTypeLog.append(fileType.group(1))
                    # Notice Example 3 posted above. Those are the odd URLs for
                    # Personal iCloud data. Since it has no discernable suffix,
                    # log a value of 'personal iCloud'. :shrug:
                    elif re.match(r'.+(\icloud)', URL):
                        fileType = re.match(r'.+(\icloud)', URL)
                        fileTypeLog.append('personal iCloud')
                    #
                    #
                    # End of File Type section
                #
                #
                # End of Server downloads section
            # except:
                # print x
                # raise Exception("Funky line - check it out")
    # Beginning of the final output.
    #
    #
    # Append to a new list. This then allows us to call it whenever we need.
    # We can then put this into the Server Alert, stdout, Slack, etc.
    finalOutput.append(
        'Cacher has retrieved the following stats for %s:' % targetDate)
    finalOutput.append('')
    # Add up our bytes from each store from our list to get a total
    totalbytesserved = sum(map(int, totalbytesserved))
    totalbytesfromorigin = sum(map(int, totalbytesfromorigin))
    totalbytesfrompeers = sum(map(int, totalbytesfrompeers))
    # Bail here since there aren't any bandwidth stats.
    if not totalbytesserved:
        print 'Cacher did not retrieve any stats for %s' % targetDate
        sys.exit(1)

    finalOutput.append(
        '%s of bandwith served to client devices.' % (
            convert_bytes_to_human_readable(totalbytesserved)))
    finalOutput.append(
        ' %s of bandwith requested from Apple' % (
            convert_bytes_to_human_readable(totalbytesfromorigin)))
    finalOutput.append(
        ' %s of bandwith requested from other Caching Servers' % (
            convert_bytes_to_human_readable(totalbytesfrompeers)))
    finalOutput.append('')

    # Total Numbers of IP addresses
    finalOutput.append(
        '%s IP Addresses hit the Caching Server yesterday consisting'
        ' of:' % len(IPLog))
    finalOutput.append('  %s Unique IP Addresses.' % len(set(IPLog)))
    finalOutput.append('')

    # Total Number of iOS devices
    # Don't display if 0 downloads
    if len(iOSModelOnlyLog) > 0:
        finalOutput.append(
            'A total of %s iOS downloads were requested '
            'from the Caching Server yesterday consisting of:'
            % len(iOSModelOnlyLog))

    # Sort the list by device type (AppleTV, iPad, iPhone, iPod). If we aren't
    # using the friendly names, we use the standard sorting, but if we use the
    # friendly names, we will sort the list at the very end.
    if friendlyNames:
        # Friendly Name Sorting:
        # In order to sort the friendly names properly, we create a new list,
        # counting the amount of devices and swapping the key/value pairs from
        # the friendly names. Since we have to sort by friendly name, we create
        # a new list based off the following: modeltype/numberofdevices. We
        # then split this output on the "/" which gives us the number of the
        # number of devices and the modeltype in proper order.
        # Example:
        # iPhone3,1 becomes iPhone 4 [GSM]/numberofDevices which is then sorted
        # and finally split.
        for x in set(iOSModelOnlyLog):
            numberofDevices = iOSModelOnlyLog.count(x)
            modeltype = x
            for k, v in friendlyModels.items():
                if k == modeltype:
                    modeltype = v
            FriendlyLog.append('%s/%s' % (modeltype, numberofDevices))
            if 'Apple TV' in modeltype:
                AppleTVNumberLog.append('%s' % numberofDevices)
            elif 'iPad' in modeltype:
                iPadNumberLog.append('%s' % numberofDevices)
            elif 'iPhone' in modeltype:
                iPhoneNumberLog.append('%s' % numberofDevices)
            elif 'iPod' in modeltype:
                iPodNumberLog.append('%s' % numberofDevices)
        # Force conversion of lists to int
        AppleTVNumberLog = [int(i) for i in AppleTVNumberLog]
        iPadNumberLog = [int(i) for i in iPadNumberLog]
        iPhoneNumberLog = [int(i) for i in iPhoneNumberLog]
        iPodNumberLog = [int(i) for i in iPodNumberLog]
        # Output
        if sum(AppleTVNumberLog) > 0:
            finalOutput.append(
                ' A total of %s Apple TV downloads' % sum(AppleTVNumberLog))
        if sum(iPadNumberLog) > 0:
            finalOutput.append(
                ' A total of %s iPad downloads' % sum(iPadNumberLog))
        if sum(iPhoneNumberLog) > 0:
            finalOutput.append(
                ' A total of %s iPhone downloads' % sum(iPhoneNumberLog))
        if sum(iPodNumberLog) > 0:
            finalOutput.append(
                ' A total of %s iPod downloads' % sum(iPodNumberLog))
        for x in sorted(set(FriendlyLog)):
            numberofDevices = x.split('/')[1]
            modeltype = x.split('/')[0]
            finalOutput.append('  %s %s' % (numberofDevices, modeltype))
    else:
        # Non Friendly Name Sorting:
        # This one is easier than friendly names as it's alphabetized by
        # sorted(). Count the devices and prefix it on the output.
        for x in sorted(set(iOSModelOnlyLog)):
            numberofDevices = iOSModelOnlyLog.count(x)
            modeltype = x
            if 'AppleTV' in modeltype:
                AppleTVNumberLog.append('%s' % numberofDevices)
            elif 'iPad' in modeltype:
                iPadNumberLog.append('%s' % numberofDevices)
            elif 'iPhone' in modeltype:
                iPhoneNumberLog.append('%s' % numberofDevices)
            elif 'iPod' in modeltype:
                iPodNumberLog.append('%s' % numberofDevices)
        # Force conversion of lists to int
        AppleTVNumberLog = [int(i) for i in AppleTVNumberLog]
        iPadNumberLog = [int(i) for i in iPadNumberLog]
        iPhoneNumberLog = [int(i) for i in iPhoneNumberLog]
        iPodNumberLog = [int(i) for i in iPodNumberLog]
        # Output
        if sum(AppleTVNumberLog) > 0:
            finalOutput.append(
                ' A total of %s Apple TV downloads' % sum(AppleTVNumberLog))
        if sum(iPadNumberLog) > 0:
            finalOutput.append(
                ' A total of %s iPad downloads' % sum(iPadNumberLog))
        if sum(iPhoneNumberLog) > 0:
            finalOutput.append(
                ' A total of %s iPhone downloads' % sum(iPhoneNumberLog))
        if sum(iPodNumberLog) > 0:
            finalOutput.append(
                ' A total of %s iPod downloads' % sum(iPodNumberLog))
        for x in sorted(set(iOSModelOnlyLog)):
            numberofDevices = iOSModelOnlyLog.count(x)
            modeltype = x
            finalOutput.append('  %s %s' % (numberofDevices, modeltype))

    finalOutput.append('')

    # Total Number of OS Versions
    if len(OSLog) > 0:
        finalOutput.append(
            'A total of %s OS downloads were requested from the Caching Server'
            ' yesterday consisting of:' % len(OSLog))
    for x in sorted(set(OSLog)):
        numberofVersions = OSLog.count(x)
        osversion = x[0]
        osfamily = x[1]
        if osfamily == 'macOS':
            macOSFamilyLog.append(
                '%s/%s' % (osfamily + ' ' + osversion, numberofVersions))
            macOSDeviceNumber.append(numberofVersions)
        elif osfamily == 'iOS':
            iOSFamilyLog.append(
                '%s/%s' % (osfamily + ' ' + osversion, numberofVersions))
            iOSDeviceNumber.append(numberofVersions)

    # Sort the iOS versions with LooseVersion. StrictVersion fails since I am
    # cheating and adding /devicecount to the version. (Ex. iOS 10.2/2000)
    if sum(iOSDeviceNumber) > 0:
        finalOutput.append(' %s iOS downloads:' % sum(iOSDeviceNumber))
    for x in sorted(set(iOSFamilyLog), key=LooseVersion):
        numberofVersions = x.split('/')[1]
        modeltype = x.split('/')[0]
        finalOutput.append('  %s %s' % (numberofVersions, modeltype))

    # Sort the macOS versions normally, since they all start with 10.
    if sum(macOSDeviceNumber) > 0:
        finalOutput.append(' %s macOS downloads:' % sum(macOSDeviceNumber))
    for x in sorted(set(macOSFamilyLog)):
        numberofVersions = x.split('/')[1]
        modeltype = x.split('/')[0]
        finalOutput.append('  %s %s' % (numberofVersions, modeltype))
    finalOutput.append('')

    # Total Number of Apple Configurator 2 files.
    # I need logs with Apple Configurator 2 references so I can rewrite this.
    # Since you can't disintinguish between the version of AC2, I'm removing
    # the secondary line I had in the shell version.
    if len(AC2Log) > 0:
        finalOutput.append(
            'A total of %s files were requested from Apple'
            ' Configurator 2 devices' % len(AC2Log))
        finalOutput.append('')

    # Total Number of filetypes downloaded and their respect numbers
    if len(fileTypeLog) > 0:
        finalOutput.append(
            'A total of %s files were downloaded from the Caching'
            ' Server yesterday consisting of:' % len(fileTypeLog))
    for x in set(fileTypeLog):
        numberofFiles = fileTypeLog.count(x)
        finalOutput.append(' %s %s files' % (numberofFiles, x))
    finalOutput.append('')

    # Total Number of unique filetypes downloaded and their respect numbers
    urlUniqueLog = set(urlLog)
    if len(urlUniqueLog) > 0:
        finalOutput.append(
            'A total of %s unique files were downloaded from the'
            ' Caching Server yesterday consisting'
            ' of:' % len(urlUniqueLog))
    # Same logic taken from "File Type Section" so I'm not documenting it.
    for x in urlUniqueLog:
        if re.match(r'.+(\.pkg|\.ipa|\.ipsw|\.zip|\.epub)', x):
            fileType = re.match(
                r'.+(\.pkg|\.ipa|\.ipsw|\.zip|\.epub)', x)
            fileTypeUniqueLog.append(fileType.group(1))
        elif re.match(r'.+(\icloud)', URL):
            fileType = re.match(r'.+(\icloud)', x)
            fileTypeUniqueLog.append('personal iCloud')
    for x in set(sorted(fileTypeUniqueLog)):
        numberofFiles = fileTypeUniqueLog.count(x)
        finalOutput.append(' %s %s files' % (numberofFiles, x))
    finalOutput.append('')
    # Add Cacher version
    finalOutput.append('Cacher version: %s' % version)
    finalOutput.append('Uptime: %s' % get_uptime())
    # Check to see if there are entries in the noClientLog. If there are,
    # print to final message to warn the user.
    if noClientIdentityLog:
        finalOutput.append('')
        finalOutput.append(
            "WARNING: Found %s logs that did not contain "
            "the client identity. These logs have been dropped and are not "
            "counted in the statistics. More than likely LogClientIdentity "
            "was incorrectly set or not configured on this date."
            % len(noClientIdentityLog))
    #
    #
    # End of the final output.
    return finalOutput
    # print("\n".join(finalOutput))


def convert_bytes_to_human_readable(number_of_bytes):
    if number_of_bytes < 0:
        raise ValueError("ERROR: number of bytes can not be less than 0")

    step_to_greater_unit = 1024.
    number_of_bytes = float(number_of_bytes)
    unit = 'bytes'
    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'KB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'MB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'GB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'TB'

    precision = 1
    number_of_bytes = round(number_of_bytes, precision)
    return str(number_of_bytes) + ' ' + unit


def check_serverconfig():
    try:
        config = '/Library/Preferences/com.apple.AssetCache.plist'
        plist = plistlib.readPlist(config)
        return plist['LogClientIdentity']
    except Exception:
        return None


def get_uptime():
    try:
        cmd = ['/usr/bin/uptime']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        splitout = str.split(output)
        uptimeamount = splitout[2]
        # Uptime Type to use if units are "less than days"
        uptimetype = splitout[3].replace(',', '')
        if uptimeamount[-1:]==',':
            # Last char is a comma; this likely indicates that the
            # `uptimetype` is in hours and not in a "greater" unit
            uptimeamount = uptimeamount[:-1] # get rid of the comma at the end
            uptimeamount = uptimeamount.split(':')
            hourtype = ' hour, ' if uptimeamount[0]==1 else ' hours, '
            uptimeamount = uptimeamount[0] + hourtype + uptimeamount[1]
            # `uptimetype` to use if main units are in hours and minutes,
            # which is not the best way to handle this... but it works.
            uptimetype = 'minutes'
        return '%s %s' % (uptimeamount, uptimetype)
    except Exception:
        return None



def post_to_slack(targetDate, cacherdata, slackchannel, slackusername,
                  slackwebhook):
    # Server App Icon DL
    url = 'https://itunes.apple.com/lookup?id=883878097'
    try:
        request = urllib2.urlopen(url)
        jsondata = json.loads(request.read())
        iconurl = jsondata['results'][0]['artworkUrl100']
    except (urllib2.URLError, ValueError, KeyError) as e:
        # hardcode icon url in case it fails.
        iconurl = 'http://is5.mzstatic.com/image/thumb/Purple122/v4/b9/e8/c4' \
            '/b9e8c4b9-ce9c-174a-c1a8-d0ad0fc21da9/source/100x100bb.png'
    # Slack payload
    payload = {
        "channel": slackchannel,
        "username": slackusername,
        "icon_url": iconurl,
        "attachments": [
            {
                'pretext': 'Caching Server Data ' + targetDate,
                'text': cacherdata
            }
        ]
    }
    try:
        cmd = ['/usr/bin/curl', '-X', 'POST', '--data-urlencode',
               'payload=' + json.dumps(payload), slackwebhook]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
    except Exception:
        print 'Failed to send message to Slack'


def main():
    # Check for macOS Server 5.2 or higher. Use LooseVersion just in case.
    #if LooseVersion(get_serverversion()) >= LooseVersion('5.2'):
    #    pass
    #else:
    #    print "Server version is %s and not compatible" % get_serverversion()
    #    sys.exit(1)

    # Options
    usage = '%prog [options]'
    o = optparse.OptionParser(usage=usage)
    o.add_option('--targetdate',
                 help=('Optional: Date to parse. Example: 2017-01-15.'))
    o.add_option('--logpath',
                 help=('Optional: Caching Log Path. Defaults to: '
                       '/Library/Server/Caching/Logs'))
    o.add_option('--deviceids',
                 help='Optional: Use Device IDs (Ex: iPhone7,2). Defaults'
                 ' to: False',
                 action='store_true')
    o.add_option('--nostdout',
                 help='Optional: Do not print to standard out',
                 action='store_true')
    o.add_option("--slackalert", action="store_true", default=False,
                 help=("Optional: Use Slack"))
    o.add_option("--slackwebhook", default=None,
                 help=("Optional: Slack Webhook URL. Requires Slack Option."))
    o.add_option("--slackusername", default=None,
                 help=("Optional: Slack username. Defaults to Cacher."
                       "Requires Slack Option."))
    o.add_option("--slackchannel", default=None,
                 help=("Optional: Slack channel. Can be username or channel "
                       "Ex. #channel or @username. Requires Slack Option."))

    opts, args = o.parse_args()

    # Check if LogClientIdentity is configured correctly. If it isn't - bail.
    serverconfig = check_serverconfig()
    if serverconfig is True:
        pass
    elif type(serverconfig) is str or type(serverconfig) is int:
        print "LogClientIdentity is incorrectly set to: %s - Type: %s" \
            % (str(serverconfig), type(serverconfig).__name__)
        print "Please run \"sudo -u _assetcache defaults write /Library/Preferences/com.apple.AssetCache.plist LogClientIdentity -bool True\""
        sys.exit(1)
    elif not serverconfig:
        print "LogClientIdentity is not set"
        print "Please run \"sudo -u _assetcache defaults write /Library/Preferences/com.apple.AssetCache.plist LogClientIdentity -bool True\""
        sys.exit(1)
    else:
        print "LogClientIdentity is set to: %s" % str(serverconfig)
        print "Please run \"sudo -u _assetcache defaults write /Library/Preferences/com.apple.AssetCache.plist LogClientIdentity -bool True\""
        sys.exit(1)

    # Grab other options
    if opts.targetdate:
        targetDate = opts.targetdate
    else:
        targetDate = str(date.today() - timedelta(1))
    if opts.logpath:
        logPath = opts.logpath
    else:
        logPath = '/Library/Server/Caching/Logs'
    if opts.deviceids:
        friendlyNames = False
    else:
        friendlyNames = True
    if opts.nostdout:
        stdOut = False
    else:
        stdOut = True
    if opts.slackalert:
        slackAlert = True
    else:
        slackAlert = False
    slackalert = opts.slackalert
    slackwebhook = opts.slackwebhook
    if opts.slackusername:
        slackusername = opts.slackusername
    else:
        slackusername = 'Cacher'
    slackchannel = opts.slackchannel

    # Gather logs from Unified logging
    rawLog = subprocess.check_output('log show  --predicate \'subsystem == "com.apple.AssetCache"\' --debug --info', shell=True);
    rawLog = StringIO.StringIO(rawLog);


    # Run the function that does most of the work.
    cacherdata = cacher(rawLog.readlines(), targetDate, friendlyNames)
    # Output conditionals
    if stdOut:
        print("\n".join(cacherdata))
    if slackAlert:
        print ''
    if slackalert is True:
        post_to_slack(targetDate, "\n".join(cacherdata), slackchannel,
                      slackusername, slackwebhook)


if __name__ == '__main__':
    main()
