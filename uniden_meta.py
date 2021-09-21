import serial
import time
import requests
import config as config

ser = serial.Serial(config.serial_port, config.serial_baud, timeout=config.serial_timeout)

serial_buffer = ''
next_char = b''
rec_status = 'GLG\r\n'
TGIDold = 0
TGID = ''
metadata = ''
scan_status = 0


def get_data():
    global serial_buffer, next_char
    serial_buffer = ''
    next_char = b''
    ser.write(rec_status.encode())


def rec_data():
    if ser.inWaiting() > 0:
        global serial_buffer, next_char
        while next_char != b'\r':
            next_char = ser.read(1)
            serial_buffer += next_char.decode()
        # print(serial_buffer)


def parse_data():
    parsed = serial_buffer.split(",")
    stringtest = parsed[0]
    global TGIDold, TGID, metadata, scan_status
    if stringtest == "GLG":
        length = len(parsed)
        if length >= 10:  # check list length so we don't get exception 10 for BCT15, 13 for BC886XT
            TGID = parsed[1]
            SYSNAME = parsed[5]
            GROUP = parsed[6]
            TG = parsed[7]
        if TGID.find('.') != -1:  # check to see if a trunked or conventional system and get FREQuency
            FREQ = TGID.lstrip('0')  # remove leading 0 if present
            if (FREQ[-1] == '0'):  # remove trailing 0 if present
                FREQ = FREQ[:-1]
        else:
            FREQ = 0
        if TGID != TGIDold and TGID != '':  # check if group change or scanner not receiving
            if FREQ == 0:  # for a trunked system
                metadata = ((SYSNAME) + " " + (TGID) + " " + (TG))
            else:  # for a conventional system
                metadata = ((FREQ) + " " + (SYSNAME) + " " + (GROUP) + " " + (
                    TG))  # User can delete/rearrange items to update
        elif TGID == TGIDold and TGID != '':
            metadata = ''
        else:
            metadata = 'Scanning...'


def update_icecast():
    global TGID, TGIDold, metadata, scan_status
    if metadata != 'Scanning...' and metadata != '':
        print(metadata)
        TGIDold = TGID
        metadata_formatted = metadata.replace(" ", "+")  # add "+" instead of " " for icecast2
        for s in config.icecast_servers:
            if config.icecast_servers[s]["https"] == 1:
                base_url = "https://" + config.icecast_servers[s]["host"] + "/admin/metadata?mount=/" + \
                       config.icecast_servers[s]["mount"] + "&mode=updinfo&song="
            else:
                base_url = "http://" + config.icecast_servers[s]["host"] + "/admin/metadata?mount=/" + \
                           config.icecast_servers[s]["mount"] + "&mode=updinfo&song="

            push_data = base_url + metadata_formatted
            r = requests.get(push_data,
                             auth=(config.icecast_servers[s]["username"], config.icecast_servers[s]["password"]))
            status = r.status_code
            scan_status = 0
            print("Talk Update" + " Icecast Server:" + str(s) + " " + config.icecast_servers[s]["host"])
            if status == 200:
                print("Icecast Update OK")
            else:
                print("Icecast Update Error", status)

    elif metadata == 'Scanning...' and scan_status == 0:
        metadata_formatted = "Scanning...".replace(" ", "+")  # add "+" instead of " " for icecast2
        TGIDold = ''
        for s in config.icecast_servers:
            if config.icecast_servers[s]["https"] == 1:
                base_url = "https://" + config.icecast_servers[s]["host"] + "/admin/metadata?mount=/" + \
                           config.icecast_servers[s]["mount"] + "&mode=updinfo&song="
            else:
                base_url = "http://" + config.icecast_servers[s]["host"] + "/admin/metadata?mount=/" + \
                           config.icecast_servers[s]["mount"] + "&mode=updinfo&song="
            push_data = base_url + metadata_formatted
            r = requests.get(push_data,
                             auth=(config.icecast_servers[s]["username"], config.icecast_servers[s]["password"]))
            status = r.status_code
            scan_status = 1
            print("Scan Update" + " Icecast Server:" + str(s) + " " + config.icecast_servers[s]["host"])
            if status == 200:
                print("Icecast Update OK")
            else:
                print("Icecast Update Error", status)


while True:
    get_data()
    rec_data()
    parse_data()
    update_icecast()
    time.sleep(.5)
