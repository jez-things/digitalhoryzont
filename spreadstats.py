#!/usr/bin/env /usr/bin/python2.7
##########################################################################
# $Id: spreadstats.py,v 1.3 2014/03/10 13:35:15 root Exp root $
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
import getopt

import mosquitto

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

dodaemon = True
exitprobes = -1
pidfile = '/var/run/spreadstats.pid'
#base_dir = '/sys/bus/w1/devices/'
serial_port = serial.Serial();
serial_port.port = "/dev/ttyACM0";
serial_port.baudrate = 115200;
serial_port.timeout=0;
#device_folder = glob.glob(base_dir + '28*')[0]
#28-0000052cec2c/w1_slave  28-0000052e21ac/w1_slave
# XXX 
#inside_temp = base_dir + '28-0000052cec2c'  + '/w1_slave'
#outside_temp = base_dir + '28-0000052e21ac'  + '/w1_slave'

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
		serial_port.baudrate = 115200;
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
	if DEBUG_MODE >= 1 and mode <= 1:
		print("DEBUG %s:" %(msg));
	if DEBUG_MODE >= 2 and mode <= 2:
		syslog.syslog(syslog.LOG_DEBUG, "%s" %(msg));
	if DEBUG_MODE >= 3 and  mode <= 3:
		syslog.syslog(syslog.LOG_DEBUG, "%s" %(msg));
	

def logit(msg, prio=syslog.LOG_ERR):
	syslog.syslog(prio, msg);
	     

def mosquitto_init(host):
    client = mosquitto.Mosquitto("stary");
    client.connect(host);
    return (client);


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
        logit("%s >%s, %s" %(querybuf, r1.status, r1.reason), prio=syslog.LOG_INFO);
        conn.close()

    


def serial_read_values(s_port):
	"""
        read temperature from serial
	"""
	global NPROBES;
	tempbuf = "";
        irms=0;
        apppower=0;
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
                debug_print("got values: %s" %(temps[0]));
		if len(temps) == 2: # count of expected probes
			try:
				irms = float(temps[1]);
				apppower = float(temps[0]);
			except Exception as msg:
				logit("conversion failure \"%s\"" %(msg))
			else:
                                debug_print("apparent power %f Irms:%f" %(apppower, irms));
                		logit("irms %f" %(irms),prio=syslog.LOG_INFO);
		return (apppower, irms)
        elif NPROBES <= 0:
		debug_print("skipping first line %s" %(tempbuf));
	elif tempbuf[0] == "#":
		debug_print("DEBUG: %s" %(tempbuf));
	else:
		debug_print("DEBUG (unknown output): %s" %(tempbuf));
	return ()
    



def read_temp_raw(device_file):
	try:
		f = open(device_file, 'r')
	except IOError as e:
		logit("Couldn't read device file in path \"%s\":%s" % (device_file, e.strerror))
		return None;
	else:
		lines = f.readlines()
		f.close()
	return lines

# device_file = Path to device.
# fieldno = Name of URL parameter "field". Limited to number.
def read_temp(device_file):
	lines = read_temp_raw(device_file)
	if lines == None:
		return None;
	debug_print(lines[1], mode=3);
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
			return temp_c
		else:
			return "failure"


def read_loop():
	global serial_port,NPROBES
	thingsfld = {};
	s_port_vals = (False,False,);


	if serial_port != False:
		s_port_vals = serial_read_values(serial_port);
                NPROBES+=1;
		if len(s_port_vals) >=  1:
                        debug_print("%d) got >= 1 value %d" %(NPROBES, s_port_vals[0]));
			#thingsfld.update({"field5":s_port_vals[0]});
		else:
			s_port_vals = (False,False,);
			logit("Read failure from serial port!");
	else:
		debug_print("Serial port disabled! Not reading", mode=3);

        return s_port_vals;
	#if tempin != False or tempout != False or s_port_vals != False:
	#	update_thingspeak(APIKEY, thingsfld);



def do_main_program():
	global serial_port;
	global MAIN_LOOP;
        global exitprobes;
	initial_program_setup()
        client = mosquitto_init("horyzont.bzzz.net");

    	try:
		serial_port.open();
	except Exception, msg:
		logit("Serial open exception: %s for %s" % (msg,serial_port.name));
		serial_port = False;
	else:
		logit("-> Opened serial port %s" %(serial_port.name), prio=syslog.LOG_INFO);

	if serial_port != False:
		serial_port.flushOutput()
	
        print("exit after %d probes" %(exitprobes));
	while True:
		vls = read_loop()
                if (exitprobes != -1 and NPROBES >= exitprobes):
                    sys.exit(3);
                client.loop();
		time.sleep(1)
                if len(vls) >= 2:
                    client.publish("sopot13/electrocity", str(vls[1]), 1);
                    print("%d/%d" %(vls[0], vls[1]));
	# endless
	logit("Program shutting down!", prio=syslog.LOG_INFO);



###
# main
#
context = daemon.DaemonContext(
	working_directory='/var/www',
#	pidfile=lockfile.FileLock('/var/run/spreadstats.pid'),
	)

context.signal_map = {
	signal.SIGTERM: program_cleanup,
	signal.SIGHUP:  program_reload,
	}

# XXX #########################################
# Add support for getopt(3)
################################################
def usage():
	print "usage: spreadstats.py -d [debug_level] "


APIKEY=os.getenv('APIKEY');
if __name__ == "__main__":
	try:
                opts, args = getopt.getopt(sys.argv[1:], 'fhd:S:vA:n:', ["foreground", "help", "debug=","serial_port=", "apikey=", "nprobes="])
	except getopt.GetoptError as err:
		print str(err);
		usage();
		sys.exit(64);
	for o, a in opts:
		if o == "-v":
			verbose = True;
		elif o in ("-S", "--serial_port"):
			serial_port = a;
		elif o in ("-d", "--debug"):
			DEBUG_MODE = int(a);
		elif o in ("-n", "--nprobes"):
                        print('exit probes option %d' %(int(a)));
			exitprobes = int(a);
		elif o in ("-A", "--apikey"):
			APIKEY = a;
		elif o in ("-h", "--help"):
			usage();
			sys.exit(64);
		elif o == "-f":
			dodaemon = False;
		else:
			assert False, "Unhandled option"
	from spreadstats import (
		initial_program_setup,
		do_main_program,
		program_cleanup,
		program_reload,
	)
	if dodaemon:
		with context:
			do_main_program()
	else:
		do_main_program()
		

