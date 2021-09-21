# Uniden Metatags Script


### This script will get channel tags from Uniden scanners and update stream servers. 


## config.py
For each additional server add another array to icecast_servers 

serial_port = "/dev/ttyACM0"
serial_baud = 115200        
serial_timeout = 5

icecast_servers = {
    1: {
        "username": "source",
        "password": "broadcastifypass",
        "host": "broadcastify.com:80",
        "mount": "brodcastify-mount",
        "https": 0
    },
    2: {
        "username": "source",
        "password": "source_pass",
        "host": "example.com/stream",
        "mount": "scanner_stream",
        "https": 1
    },

}
