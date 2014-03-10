#!/usr/bin/env /usr/bin/python2.7
##########################################################################
# $Id: readtemp.py,v 1.3 2014/03/10 13:35:15 root Exp root $
##
##########################################################################
import os,sys,time
import grp
import signal

import syslog
import glob
import traceback

import serial
import httplib
import string
import daemon
import lockfile

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
     
pidfile = '/var/run/readtemp.pid'
base_dir = '/sys/bus/w1/devices/'
serial_port = serial.Serial();
serial_port.port = "/dev/ttyACM0";
serial_port.baudrate = 57600;
serial_port.timeout=0;
apikey='24S5R8E6GGJJRMT0'
#device_folder = glob.glob(base_dir + '28*')[0]
#28-0000052cec2c/w1_slave  28-0000052e21ac/w1_slave
inside_temp = base_dir + '28-0000052cec2c'  + '/w1_slave'
outside_temp = base_dir + '28-0000052e21ac'  + '/w1_slave'
DEBUG_MODE = 0;

def program_cleanup():
	pass;
def initial_program_setup():
	global pidfile;
	if os.path.isfile(pidfile):
		#pass
		logit( "%s already exists, exiting" % pidfile)
		sys.exit();
	else:
		try:
			pidf = open(pidfile, 'a+')
			mypid = os.getpid();
			pidf.write(str(mypid));
			pidf.flush();

			pidf.close();
		except Exception as e:
			logit("Pidfile creation exception: \"%s\"" %(e));

def debug_print(msg):
	if DEBUG_MODE >= 1:
		print("DEBUG %s:" %(msg));
	if DEBUG_MODE >= 2:
		syslog.syslog(syslog.LOG_DEBUG, "DEBUG %s:" %(msg));

def logit(msg, prio=syslog.LOG_ERR):
	syslog.syslog(prio, msg);
	     


def update_thingspeak(apikey, fields):
        """"
            This routine sends val as fieldno  which is a current temperature
            read from serial to thingspeak
        """
        conn = httplib.HTTPConnection("api.thingspeak.com")
        querybuf = '/update?key=%s' %(apikey);
        for fieldnam in fields:
            ffmt = '%2.2f' % (fields[fieldnam])
            querybuf = querybuf + '&' + fieldnam + '=' + ffmt;
        try:
            conn.request("GET", querybuf)
        except httplib.HTTPException as httpexpt:
            logit("HTTP connection problem %s" % (httpexpt));
        except:
            logit( "unknown exception");
            debug_print(traceback.print_exc());
            pass
        r1 = conn.getresponse()
        logit("          \t`->%s, %s" %(r1.status, r1.reason), prio=syslog.LOG_INFO);
        conn.close()

    


def serial_read_values(s_port):
    """
        read temperature from serial
    """
    global nprobes;
    tempbuf = "";

 
    while True:
        try:
            ch = s_port.read(1)
        except Exception, msg:
            logit("read error! %s" %(msg));
            break;
        if ch == '\r':
            pass
        elif ch == '\n':
            break;
            tempbuf = "";
        else:
            tempbuf += ch
    #global nprobes
    if len(tempbuf) <= 0:
        return;
    if nprobes > 0 and tempbuf[0] != "#":
        temps = tempbuf.split("\t");
        if len(temps) == 1:
            try:
                light = float(temps[0]);
            except Exception as msg:
                logit("conversion failure \"%s\"" %(msg))
            else:
                #print "%10.d) temperatura %4.4f %4.4f %4.4f"%(nprobes, temp0, temp1, light)
                print("%10.d) light level %d" %(nprobes, light));
    		nprobes+=1
		return (light)
                
    elif tempbuf[0] == "#":
        debug_print("DEBUG: %s" %(tempbuf));
    else:
        debug_print("DEBUG (unknown output): %s" %(tempbuf));
    nprobes+=1



def read_temp_raw(device_file):
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

# device_file = Path to device.
# fieldno = Name of URL parameter "field". Limited to number.
def read_temp(device_file):
	lines = read_temp_raw(device_file)
	debug_print(lines[1]);
	while lines[1].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw(device_file)
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos+2:]
			temp_c = float(temp_string) / 1000.0
			#temp_f = temp_c * 9.0 / 5.0 + 32.0
			#update_thingspeak(temp_c, fieldno);
			return temp_c
		else:
			return "failure"


def read_loop():
	global serial_port
	global apikey
	tempin = read_temp(inside_temp)
	tempout = read_temp(outside_temp)
	light = 0.00;
	if serial_port != False:
		light = serial_read_values(serial_port)[1];
		update_thingspeak(apikey, dict(field5=light, field3=tempin, field1=tempout));
	else:
		update_thingspeak(apikey, dict(field3=tempin, field1=tempout));
	logit("inside %f, outside %f" %(tempin, tempout), prio=syslog.LOG_INFO)



def do_main_program():

	initial_program_setup()
	global serial_port;

    	try:
		serial_port.open();
	except Exception, msg:
		logit("Serial open exception: %s for %s" % (msg,serial_port.name));
		serial_port = False;
	else:
		logit("-> Opened serial port %s" %(serial_port.name), prio=syslog.LOG_INFO);

	if serial_port != False:
		serial_port.flushOutput()
	
	while True:
		read_loop()
		time.sleep(1)
	# endless
	logit("program shutting down!", prio=syslog.LOG_INFO);
	sys.exit(3);


###
# main
#
context = daemon.DaemonContext(
	working_directory='/var/www',
#	pidfile=lockfile.FileLock('/var/run/readtemp.pid'),
	)

context.signal_map = {
	signal.SIGTERM: program_cleanup,
	signal.SIGHUP: 'terminate',
	}

if __name__ == "__main__":
	from readtemp import (
		initial_program_setup,
		do_main_program,
		program_cleanup,
	)
	with context:
		do_main_program()
		

