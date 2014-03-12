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
#device_folder = glob.glob(base_dir + '28*')[0]
#28-0000052cec2c/w1_slave  28-0000052e21ac/w1_slave
# XXX 
inside_temp = base_dir + '28-0000052cec2c'  + '/w1_slave'
outside_temp = base_dir + '28-0000052e21ac'  + '/w1_slave'

# DEBUG_MODE = 0
# * Brak debug mode
# DEBUG_MODE = 1
# * Podstawowe informacje
# DEBUG_MODE = 2
# * 
# DEBUG_MODE = 3
# * Informacje w postaci raw

APIKEY=''
DEBUG_MODE = 2;
NPROBES = 0;

def program_reload():
	global serial_port;
	if not os.path.isfile(pidfile):
		try:
			pidf = open(pidfile, 'a+')
			mypid = os.getpid();
			pidf.write(str(mypid)+"\n");
			pidf.flush();

			pidf.close();
		except Exception as e:
			logit("Pidfile re-creation exception: \"%s\"" %(e));

	logit("Reloading serial port", prio=syslog.LOG_INFO);
	if serial_port == False:
		serial_port = serial.Serial();

		serial_port.flushOutput()
		serial_port.port = "/dev/ttyACM0";
		serial_port.baudrate = 57600;
		serial_port.timeout=0;
		try:
			serial_port.open()
		except Exception as msg:
			logit("Cannot reopen serial port");

	return 0;

def program_cleanup():
	global pidfile;
	logit("End of work", prio=syslog.LOG_INFO);
	debug_print("Unlinking pidfile=\"%s\"" % (pidfile));
	try:
		os.unlink(pidfile);
	except Exception as msg:
		debug_print("Problem with unlinking pidfile=\"%s\" : %s" %(pidfile, msg));
	return 0;

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
			sys.exit(3);

def debug_print(msg, mode=0):
	if DEBUG_MODE >= 1 or mode >= 1:
		print("DEBUG %s:" %(msg));
	if DEBUG_MODE >= 2 or mode >= 2:
		syslog.syslog(syslog.LOG_DEBUG, "%s" %(msg));
	if DEBUG_MODE >= 3 or mode >= 3:
		syslog.syslog(syslog.LOG_DEBUG, "%s" %(msg));
	

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
	global NPROBES;
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
	#global NPROBES
	if len(tempbuf) <= 0:
		logit("tempbuf lenght too short")
		return (0,);
	if NPROBES > 0 and tempbuf[0] != "#":
		temps = tempbuf.split("\t");
		if len(temps) == 1:
			try:
				light = float(temps[0]);
			except Exception as msg:
				logit("conversion failure \"%s\"" %(msg))
				NPROBES+=1;
			else:
                		logit("Light level %f" %(NPROBES, light),prio=syslog.LOG_INFO);
    			NPROBES+=1
		return (light,)
	elif tempbuf[0] == "#":
		debug_print("DEBUG: %s" %(tempbuf));
	else:
		debug_print("DEBUG (unknown output): %s" %(tempbuf));
	NPROBES+=1;
	return ()
    



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
	temp_c = False;
	while lines[1].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw(device_file)
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos+2:]
			try:
				temp_c = float(temp_string) / 1000.0
			except Exception:
				logit("conversion failure!")


			#temp_f = temp_c * 9.0 / 5.0 + 32.0
			#update_thingspeak(temp_c, fieldno);
			return temp_c
		else:
			return "failure"


def read_loop():
	global serial_port
	global APIKEY
	thingsfld = {};
	tempin = read_temp(inside_temp)
	tempout = read_temp(outside_temp)
	s_port_vals = False;

	if tempin != False:
		thingsfld.update({"field3":tempin});
	else:
		logit("Read failure for internal temperature sensor!")
	if tempout != False:
		thingsfld.update({"field1":tempout});
	else:
		logit("Read failure for outside temperature sensor!")
	if serial_port != False:
		s_port_vals = serial_read_values(serial_port);
		if len(s_port_vals) >=  1:
			thingsfld.update({"field5":s_port_vals[0]});
		else:
			s_port_vals = False;
			logit("Read failure from serial port!");
	else:
		debug_print("Serial port disabled! Not reading", mode=3);

	if tempin != False or tempout != False or values !=
			update_thingspeak(APIKEY, dict(field5=values[0], field3=tempin, field1=tempout));
	elif tempin != False and tempout != False:
		update_thingspeak(APIKEY, dict(field3=tempin, field1=tempout));
	elif tempin != False and tempout == False:
		update_thingspeak(APIKEY, dict(field3=tempin));
	elif tempin == False and tempout != False:
		update_thingspeak(APIKEY, dict(field3=tempin));
		logit("inside %f, outside %f" %(tempin, tempout), prio=syslog.LOG_INFO)
	elif tempin == False and tempout == False:



def do_main_program():
	initial_program_setup()
	global serial_port;
	global MAIN_LOOP;

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
	logit("Program shutting down!", prio=syslog.LOG_INFO);



###
# main
#
context = daemon.DaemonContext(
	working_directory='/var/www',
#	pidfile=lockfile.FileLock('/var/run/readtemp.pid'),
	)

context.signal_map = {
	signal.SIGTERM: program_cleanup,
	signal.SIGHUP:  program_reload,
	}

# XXX #########################################
# Add support for getopt(3)
################################################

APIKEY=os.getenv('APIKEY');
if __name__ == "__main__":
	from readtemp import (
		initial_program_setup,
		do_main_program,
		program_cleanup,
		program_reload,
	)
	with context:
		do_main_program()
		

