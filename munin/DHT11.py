#!/usr/bin/env /usr/bin/python2.7
# -*- coding:utf-8 -*-

import os, sys, string, glob, socket, json
import syslog
import dhtreader

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
	read_loop = True
	while read_loop:
		try:
			t, h = dhtreader.read(11, 25)
		except Exception as e:
			syslog.syslog(syslog.LOG_ERR, "read exception: %s" %(e));
		else:
			read_loop = False
	print("h.value {0}".format(h))
	
	
sys.exit(0)
