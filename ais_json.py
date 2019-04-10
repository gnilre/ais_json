#!/usr/bin/python

from settings import URL, NAME, LOGFILE
import json
import ais.stream
import socket
import datetime
import requests

IP = '127.0.0.1'
PORT = 6000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

def stripPadding(theString):
  return theString.rstrip('@')

while True:

  for msg in ais.stream.decode(sock.makefile('r'),keep_nmea=True):
    rxtime =  datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S") #YYYYMMDDHHMMSS
    parsed = json.loads(json.dumps(msg))
    
    ais = {
            'msgtype': parsed['id'],
            'mmsi': parsed['mmsi'],
            'rxtime': rxtime
            }

    if 'x' in parsed:
      ais['lon'] = parsed['x']
    if 'y' in parsed:
      ais['lat'] = parsed['y']
    if 'sog' in parsed:
      ais['speed'] = parsed['sog']
    if 'cog' in parsed:
      ais['course'] = parsed['cog']
    if 'true_heading' in parsed:
      ais['heading'] = parsed['true_heading']
    if 'nav_status' in parsed:
      ais['status'] = parsed['nav_status']
    if 'type_and_cargo' in parsed:
      ais['shiptype'] = parsed['type_and_cargo']
    if 'part_num' in parsed:
      ais['partno'] = parsed['part_num']
    if 'callsign' in parsed:
      parsed['callsign'] = stripPadding(parsed['callsign'])
      ais['callsign'] = parsed['callsign']
    if 'name' in parsed:
      parsed['name'] = stripPadding(parsed['name'])
      ais['shipname'] = parsed['name']
    if 'vendor_id' in parsed:
      parsed['vendor_id'] = stripPadding(parsed['vendor_id'])
      ais['vendorid'] = parsed['vendor_id']
    if 'dim_a' in parsed:
      ais['ref_front'] = parsed['dim_a']
    if 'dim_c' in parsed:
      ais['ref_left'] = parsed['dim_c']
    if 'draught' in parsed:
      ais['draught'] = parsed['draught']
    if 'length' in parsed:
      ais['length'] = parsed['length']
    if 'width' in parsed:
      ais['width'] = parsed['width']
    if 'destination' in parsed:
      parsed['destination'] = stripPadding(parsed['destination'])
      ais['destination'] = parsed['destination']
    if 'persons' in parsed:
      ais['persons_on_board'] = parsed['persons']

    path = { 
            "name": NAME, 
            "url": URL }

    groups = { 
            "path": [path], 
            "msgs":[ais] }
    
    output = {
            "encodetime": rxtime,
            "protocol": 'jsonais',
            "groups":  [groups]
            }
    
    with open(LOGFILE, "a") as logfile:
      tstamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") 
      logfile.write(tstamp + json.dumps(parsed) + "\n")

    post = json.dumps(output)
    try:

      r = requests.post(URL, files={'jsonais': (None, post)})

      if 'shipname' in ais:
        print 'Message type: ' + str(ais['msgtype']) + ' mmsi: ' + str(ais['mmsi']) + ' name: ' + ais['shipname']
      else:
        print 'Message type: ' + str(ais['msgtype']) + ' mmsi: ' + str(ais['mmsi'])


      #dump non common packets for debugging
      #if parsed['id'] not in (1,2,3,4):
      #  print '---'
      #  print 'NMEA:', parsed['nmea']
      #  print 'Parsed:', parsed
      #  print 'Post:', post
      #  print 'Result:', json.loads(r.text)['description']
    except requests.exceptions.RequestException as e:
      print e
    except Exception as e:
      print e
