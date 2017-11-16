# Cacher - High Sierra Edition
Updated Cacher to support High Sierra. This version will not support the old version of Caching Service using the Server app. Please see the origional cacher developer (https://github.com/erikng/Cacher) for support of older versions of the caching service. Cacher is a python script that will parse the OS X Caching Server debug logs and present you (to the best of its abilities) serving statistics.

High Sierra Apple Caching Log reporting

Some of the things Cacher can display:
- Total bandwidth served to clients
- Total bandwidth requested from Apple
- Total bandiwdth requested from other Caching servers
- Total IP Addresses
- Total Unique IP Addresses.
- Total iOS download requests including model type
- Total OS download requests specified by type (iOS and macOS)
- Total applications downloaded from Apple Configurator 2 devices
- Total downloaded files
- Total eBook (.epub) files
- Total personal iCloud files
- Total package (.pkg) files
- Total iOS application (.ipad) files
- Total Zip (.zip) files
- Total unique downloaded files
- Total unique eBook (.epub) files
- Total unique personal iCloud files
- Total unique package (.pkg) files
- Total unique iOS application (.ipad) files
- Total unique Zip (.zip) files

## Only for Unified Logging (ie. 10.13 and higher)
Cacher currently supports 10.13

## Usage
```
Usage: cacher.py [options]

Options:
  -h, --help            show this help message and exit
  --targetdate=TARGETDATE
                        Optional: Date to parse. Example: 2017-01-15.
  --deviceids           Optional: Use Device IDs (Ex: iPhone7,2). Defaults to:
                        False
  --nostdout            Optional: Do not print to standard out
  --serveralert         Optional: Send Server Alert
  --slackalert          Optional: Use Slack
  --slackwebhook=SLACKWEBHOOK
                        Optional: Slack Webhook URL. Requires Slack Option.
  --slackusername=SLACKUSERNAME
                        Optional: Slack username. Defaults to Cacher.Requires
                        Slack Option.
  --slackchannel=SLACKCHANNEL
                        Optional: Slack channel. Can be username or channel
                        Ex. #channel or @username. Requires Slack Option.
```

## Optional features
The following are optional features:

### Configure Caching service for logging
```
sudo -u _assetcache defaults write /Library/Preferences/com.apple.AssetCache.plist Verbose -bool True
sudo -u _assetcache defaults write /Library/Preferences/com.apple.AssetCache.plist LogClientIdentity -bool True
AssetCacheManagerUtil reloadSettings
AssetCacheManagerUtil deactivate
AssetCacheManagerUtil activate
```

### Target date
By default, Cacher will use look for logs from the previous date. To target logs from a custom date, use the `--targetdate` option.

`cacher.py --targetdate "2016-11-28"`

### Log path (High Sierra)
In this version of Cacher logs are collected by running the log command.
```
log show  --predicate 'subsystem == "com.apple.AssetCache"' --debug --info
```

### DeviceIDs
By default, Cacher will use the "Friendly Names" for iOS devices. To use the model Device ID, use the `--deviceids` option.

`cacher.py --deviceids`

Device IDs Example:
``` bash
A total of 3513 iOS downloads were requested from the Caching Server yesterday consisting of:
 A total of 4 Apple TV downloads
 A total of 417 iPad downloads
 A total of 3075 iPhone downloads
 A total of 17 iPod downloads
  4 AppleTV5,3
  4 iPad2,1
  7 iPad2,2
  2 iPad2,3
  5 iPad2,4
```

Friendly Names Example:
``` bash
A total of 3513 iOS downloads were requested from the Caching Server yesterday consisting of:
 A total of 4 Apple TV downloads
 A total of 417 iPad downloads
 A total of 3075 iPhone downloads
 A total of 17 iPod downloads
  4 5th Generation Apple TVs
  5 iPad 2nd Generation [M2012 Wifi Revision]
  2 iPad 2nd Generation [Wifi + CDMA]
  7 iPad 2nd Generation [Wifi + GSM]
  4 iPad 2nd Generation [Wifi]
```

### No Standard output
By default, Cacher will print the results to standard out. To skip this use the `--nostdout` option.

`cacher.py --nostdout`

### Server alert
By default, Cacher will __no longer__ send a server alert. To send a server alert, use the `--serveralert` option.

Please note that this option requires root/sudo level permissions.

`sudo cacher.py --serveralert`

If you attempt to use this option without elevated permissions, Cacher will write the following note to standard out.

`Did not send serverAlert - requires root`

### Slack alert
By default, Cacher will not send a server alert. To send a server alert, use the `--slackalert` option.

The slack alert __requires__ two other options to be passed:
- `--slackchannel`
- `--slackwebhook`

#### Username or Channel
You can pass both an username or channel via the `--slackchannel` option:
Examples:
- `@erik`
- `#cacher`

#### Slack webhook
A slack webhook must be created. To create a webhook, please go [here](https://my.slack.com/services/new/incoming-webhook/)

``` bash
cacher.py --slackalert \
--slackchannel "@egomez" \
--slackwebhook "https://hooks.slack.com/services/YOURURL"``
```

## Screenshots

### Slack Small
![Cacher Slack Example Small](/images/CacherSlack_Small.png?raw=true)

### Slack Large
![Cacher Slack Example Large](/images/CacherSlack_Large.png?raw=true)

### Original Server Alert
![Cacher Server Alert Example](/images/CacherServerAlert.png?raw=true)
