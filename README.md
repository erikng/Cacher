# Cacher
Cacher is a script that will parse the OS X Caching Server debug logs and present you (to the best of its abilities) serving statistics. This script must be ran as root (currently) to unzip necessary logs and generate a server alert.

Some of the things Cacher can display:
- Total Bandwidth served to clients
- Total Bandwidth downloaded from Apple
- Total Peer Caching Servers bandwidth
- Total IP Addresses
- Total Unique IP Addresses.
- Total files downloaded
- Total Books
- Total iOS Apps
- Total Mac Apps
- Total Zip files
- Total Apple Server Registrations
- Total Unique files downloaded from Caching Server
- Total Unique Books
- Total Unique iOS Apps
- Total Unique Mac Apps
- Total Unique Zip files

In addition you will also get a detailed list of iOS / OS X versions and iOS models.

### Notes
By default, the Caching service will not log the model and iOS/OS X version. In order to get true results from this script, add this key to `/Library/Server/Caching/Config/Config.plist`.

You can edit the file manually or see below the correct command for your respective server version. To ensure proper logging, please restart the caching service after changing this value.
<key>LogClientIdentity</key>
<true/>

### Server 4
[This commit](https://github.com/erikng/Cacher/commit/17903d2dd29886c0dfc16054ae39b89f25581f79) is the last supported version for Server 4.
For extended logging, run the following command:
`sudo serveradmin settings caching:LogClientIdentity = 1`

## Server 5
For extended logging, run the following command:
`sudo serveradmin settings caching:LogClientIdentity = yes`

![Cacher Example](http://erikng.github.io/screenshots/Cacher_Example.png)



# TODO
Cleanup / Whatever else I think of
