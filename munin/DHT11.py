#!/usr/bin/env /usr/bin/python2.7
# -*- coding:utf-8 -*-

import os, sys, string, glob, socket, json
import dhtreader

DHT11 = 11
#DHT22 = 22
#AM2302 = 22



plugin_name = list(os.path.split(sys.argv[0]))[1]

arg = sys.argv[1] if len(sys.argv) == 2 else None
if arg == "config":
	print("graph_title Humidity/temperature from DHT11");
	print("graph_vlabel %");
	print("graph_category environmental");
	print("h.label humidity");
	print("h.draw AREA");
else:
	dhtreader.init()
	t, h = dhtreader.read(11, 25)
	print("h.value {0}".format(h))
	
	
sys.exit(0)

dhtpin = int(sys.argv[2])
if dhtpin <= 0:
    print("invalid GPIO pin#")
    sys.exit(3)

print("using pin #{0}".format(dhtpin))
if t and h:
    print("Temp = {0} *C, Hum = {1} %".format(t, h))
else:
    print("Failed to read from sensor, maybe try again?")
