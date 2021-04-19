# CIPC
Small script for managing configurations on Cisco ios devices via Telnet.
It was only tested to telnet to devices trough terminal server, but in theory it can work using ordinary Telnet connection.

This repo highly relies on netmiko library which is licensed under the MIT License
https://github.com/ktbyers/netmiko

## Usage

```
Usage:   python3 CIPC_cli.py mode device_names
Example: python3 CIPC_cli.py r    S1 S2 R2 S8 S3 R4

Modes:
    r       read configurations - reads configurations from devices and saves them to corresponding configuration txt files
            note that encrypted passwords will be read and saved in encrypted form
    u       update configurations - reads configurations from txt files and applies them to devices
            without clearing previous configurations
    e       erase configurations - erases configurations from devices
    w       write configurations - reads configurations from files and applies them to devices
            erasing previous configurations
    с       alternative usage, for one device with custom passwords (if there is no password type "n")

            Usage:   python3 CIPC_cli.py c mode device_name user_EXEC_password priv_EXEC_password
            Example: python3 CIPC_cli.py c e    S1          n                  cllass

You can use "all" as a device name to order handle all devices in its device list
Example: python3 CIPC_cli.py r all
```
