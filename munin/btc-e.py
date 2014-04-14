#!/usr/bin/env /usr/bin/python2.7
# Stick glue strictly to python2.7 version
import os, sys, string, glob, socket, json 
import httplib 
import urllib2

plugin_name=list(os.path.split(sys.argv[0]))[1]
plugin_version="3.0"

url = os.getenv("url", "")
url='/api/2/btc_usd/ticker'
# https://btc-e.com/api/2/btc_usd/ticker
def btce_rpc():
    conn = httplib.HTTPSConnection("btc-e.com")
    conn.request("GET", url);
    r1 = conn.getresponse()
    data1 = r1.read()
    conn.close()
    return json.loads(data1), None
    


try: 
    accs = btce_rpc()[0]['ticker'];
except Exception as e:
    print "json failure!", e
    
arg = sys.argv[1] if len(sys.argv) == 2 else None
if arg == "config":
    print('multigraph btce_sell_buy');
    print('graph_title btce BTC/EUR');
    print('graph_vlabel PLN');
    print('graph_category bitcoin');
    print('h.label BTC sell');
    print('h.draw AREA');
    print('h.type GAUGE');
    print('b.label BTC buy');
    print('b.type GAUGE');

    print('multigraph btce_vol');
    print('graph_title btce volume');
    print('graph_vlabel BTC');
    print('graph_category bitcoin');
    print('v.label Volume of BTC');
    print('v.draw AREA');
    print('v.type GAUGE');

    print('multigraph btce_high_low_avg');
    print('graph_title btce high/low/avg');
    print('graph_vlabel EUR');
    print('graph_category bitcoin');
    print('l.label Lowest price');
    print('l.draw AREA');
    print('l.type GAUGE');
    print('h.label Highest price');
    print('h.type GAUGE');
    print('a.label Average');
    print('a.type GAUGE');
elif arg == "test":
    print accs;
else:
    print('multigraph btce_sell_buy');
    print('h.value %f' %( float(accs['sell'])) );
    print('b.value %f' %( float(accs['buy'])) );
    print('multigraph btce_vol');
    print('v.value %f' %( float(accs['vol'])) );
    print('multigraph btce_high_low_avg');
    print('l.value %f' %( float(accs['low'])) );
    print('h.value %f' %( float(accs['high'])) );
    print('a.value %f' %( float(accs['avg'])) );
#else:
    #print('h.value %d' 


