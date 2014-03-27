#!/usr/bin/env /usr/bin/python2.7
# Stick glue strictly to python2.7 version
import os, sys, string, glob, socket, json 
import httplib 
import urllib2

plugin_name=list(os.path.split(sys.argv[0]))[1]
plugin_version="3.0"

url = os.getenv("url", "")
bitcurex_user = os.getenv("bitcurex_user", "")
url='/data/ticker.json'
bitcurex_user = 'jez'
#'https://pln.bitcurex.com/data/ticker.json'
def bitcurex_rpc():
    conn = httplib.HTTPSConnection("pln.bitcurex.com")
    conn.request("GET", url);
    r1 = conn.getresponse()
    data1 = r1.read()
    conn.close()
    return json.loads(data1), None
    


try: 
    accs = bitcurex_rpc()[0];
except Exception as e:
    print "json failure!", e
    
arg = sys.argv[1] if len(sys.argv) == 2 else None
if arg == "config":
    print('graph_title bitcurex BTC/PLN');
    print('graph_vlabel PLN');
    print('graph_category bitcoin');
    print('h.label BTC sell');
    print('h.draw AREA');
    print('h.type GAUGE');
    print('b.label BTC buy');
    print('b.type GAUGE');
elif arg == "test":
    print accs;
else:
    print('h.value %f' %(accs['sell']));
    print('b.value %f' %(accs['buy']));
#else:
    #print('h.value %d' 


