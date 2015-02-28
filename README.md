# Cacher
This script will parse through OS X Caching Debug logs and generate a Server alert with the following information:

By default, Cache 4 will not log the model and iOS version. In order to get true results from this script, add this key to 
You can edit the file manually
/Library/Server/Caching/Config/Config.plist

	<key>LogClientIdentity</key>
	<true/>
Or run the command: sudo serveradmin settings caching:LogClientIdentity = true

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

# TODO
Cleanup / Whatever else I think of
