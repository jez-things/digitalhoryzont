#!/usr/bin/env /usr/bin/python2.7

import os, sys, string, glob, socket, json 
import httplib 
import urllib2

plugin_name=list(os.path.split(sys.argv[0]))[1]
plugin_version="3.0"

url = os.getenv("url", "")
polmine_apikey = os.getenv("polmine_apikey", "")
url='/?action=api&cmd=%s&asjsontype=1' % (polmine_apikey);
41321eb6535eb0f11d358a36bbe93194
def polmine_rpc():
    conn = httplib.HTTPSConnection("polmine.pl")
    conn.request("GET", url);
    r1 = conn.getresponse()
    data1 = r1.read()
    conn.close()
    return json.loads(data1[:-2]), None
    


try: 
    acctd = polmine_rpc()[0];
except Exception as e:
    print "json failure!", e
    
arg = sys.argv[1] if len(sys.argv) == 2 else None
if arg == "config":
    print('graph_title payout/balance');
    print('graph_vlabel BTC');
    print('graph_category polmine');
    print('graph_scale no');
    print('graph_order payout h');
    print('h.label balance');
    print('h.draw AREA');
    print('h.warning 0.0');
    print('h.min 0');
    print('h.max 2');
    print('payout.label payout');
    print('payout.min 0');
    print('payout.max 2');
    
else:
    print('h.value %f' %(float(acctd['balance'])) );
    print('payout.value %f' %(float(acctd['payout'])) );


