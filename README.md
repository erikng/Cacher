# Cacher
Cacher is a python script that will parse the OS X Caching Server debug logs and present you (to the best of its abilities) serving statistics.

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

## Server support
Cacher currently supports Server 5.2 and higher.

- For Server 4 please see [this commit](https://github.com/erikng/Cacher/commit/17903d2dd29886c0dfc16054ae39b89f25581f79))
- For Server 5-5.1 please see [this commit](https://github.com/erikng/Cacher/commit/57ea9c3c80c17bb29d4deb89cb07a2ae841613d9)

## Usage
```python
Usage: Cacher [options]

Options:
  -h, --help            show this help message and exit
  --targetdate=TARGETDATE
                        Optional: Date to parse. Example: 2017-01-15.
  --logpath=LOGPATH     Optional: Caching Log Path. Defaults to:
                        /Library/Server/Caching/Logs
  --deviceids           Optional: Use Device IDs (Ex: iPhone7,2). Defaults to:
                        False
  --nostdout            Optional: Do not print to standard out
  --configureserver     Optional: Configure Server to log Client Data
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

### Configure Caching service logging
By default, the Caching service will not log the model and iOS/OS X version. In order to get true results from this script, run the following command (as root):

`sudo Cacher --configureserver`

If successful, you will see the following output:

`Caching Server settings are now: caching:LogClientIdentity = yes`

### Target date
By default, Cacher will use look for logs from the previous date. To target logs from a custom date, use the `--targetdate` option.

`Cacher --targetdate "2016-11-28"`

### Log path
By default, Cacher will use look for logs from in /Library/Server/Caching/Logs. To target logs in a custom path, use the `--logpath` option.

`Cacher --logpath "/path/to/logs"`

### DeviceIDs
By default, Cacher will use the "Friendly Names" for iOS devices. To use the model Device ID, use the `--deviceids` option.

`Cacher --deviceids`

Friendly Names Example:
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

Device IDs Example:
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
By default, Cacher will print the results to standard out. To skip this use the `--notstdout` option.

`Cacher --notstdout`

### Server alert
By default, Cacher will __no longer__ send a server alert. To send a server alert, use the `--serveralert` option.

Please note that this option requires root/sudo level permissions.

`sudo Cacher --serveralert`

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
Cacher --slackalert \
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
