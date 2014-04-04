Digital Horyzon
===============


Abstract
===============


Internet of things: set of phyton scripts for collecting data from raspberryPi
by external sensors (e.g. temperature, humidity and light). Additionaly it contains
set of scripts to monitor bitcoin mining hardware through munin on external server. 


#Table of contents: 
## 1. Introduction 
### 1.1. Preface
##   2. Installation 
###  2.1. Hardware Requirements
###  2.2. Software Requirements
###  2.3. Configuration
#### 2.3.1. munin/bitcurex.py
#### 2.3.2. munin/polmine
#### 2.3.3. munin/cgminer
#### 2.3.4. readtemp.py
#### 2.3.5. munin/DHT11
#### 2.3.6. munin/lightlevel
#### 2.3.7. munin/noise
#### 2.3.8. munin/environmental
## 3. Development information
### 3.1. Introduction
### 3.2. Known bugs
### 3.3. Changelog

------------------------------------------------------------------------------

# 1. Introduction
----
## 1.1. Preface
    Internet of things: set of phyton scripts for collecting data from raspberryPi
    by external sensors (e.g. temperature, humidity and light). Additionaly it contains
    set of scripts to monitor bitcoin mining hardware through munin on external server. 
    ...

# 2. Installation 
   Among several ways to install there are some basic requirements described below.

## 2.1. Hardware Requirements
   Raspberry Pi, solderless board, 2x 4k7 resistors, DHT11, DS18B20.
## 2.2. Software Requirements
   Each script has different dependencies. 
* readtemp.py - python2-serial python2-daemon It's supported on python2.x 
  tested at the moment only on python2.7
* lightlevel - wiringPi
* DHT11 - adafruit DHT11 driver
      
## 2.3. Configuration
  
  ...
  *TODO*

### 2.3.1. munin/bitcurex.py

   *bitcurex.pl* python script is a munin script used for drawing munin charts of BTC
   currency from well-known polish bitcoin stock. No configuration provided at the moment.

### 2.3.2. munin/polmine

   *polmine* script to graph polmine statistics like hashrate

### 2.3.3. munin/cgminer
  *cgminer* is a python script which draws munin charts of cgminer and tools which
  support JSON API of cgminer or tools derived from cgminer e.g. bfgminer. There are
  two configuration options available: *rpc_port* and *rpc_host*. There's no need to
  configure these options in munin-node.conf in that case default values are:
  ```
  [cgminer]
  rpc_port 4028
  rpc_host 127.0.0.1
  ```
  script itself supports (except standard ones) additional command line options: test
  When cgminer is run with a test option it connects to given *rpc_host* on a given *rpc_port*
  and prints all variables available.

### 2.3.4. readtemp.py
  *readtemp.py* is a python script which runs on python 2.x version 3.x is not supported 
  at the moment. Application reads data in form variable=value <space> ...
  Then it sends all collected data to thingspeak web service via HTTP.
  It accepts following command line arguments:
* -d|--debug       Activates debugging mode.
* -A|--apikey      API key for thingspeak.
* -S|--serial_port path to serial device.
* -h|--help        Show usage messaga.

###  2.3.5. munin/DHT11
   *DHT11* is a python script used for drawing munin charts of humidity percentage from
   DHT11 sensor connected to raspberryPi (for details inspect fritzing sketch included in
   git repository and distribution pack).  The sensor itself can read also temperature,
   however so far it is not supported. Script depends on DHT11 driver developed by
   adafruit and available in git repository. Also script has to be runned by root (as munin does)
   or at least with suid. To run script as root following munin configuration
   has to be added in /etc/munin/munin-node.conf file:
```
   [DHT11]
   user root 
```
   
###  2.3.6. munin/lightlevel
   *lightlevel* script uses PCF8591 to access analog input where photoresistor is hooked. 
   It has to be runned with root privileges
```
[lightlevel]
user root
```
###  2.3.7. munin/noise
   *noise* script uses PCF8591 to access analog input where microphone is hooked. It graphs
   data gathered through microphone. It has to be runned with root privileges
```
[noise]
user root
```
###  2.3.8. munin/environmental
   *environmental* is a shell script to draw munin graphs of DS18B20 1-Wire thermometrs.
   It uses simply procfs to access 1-Wire devices. There are several variables possibles
   to customize charts. There are no software limits for graphed devices.
   ```
   
   ```



# 3. Development information
  	After this chapter you're supposed to be fluent with project development environment its
  cycle and milestones. Also you're going to be familiar with our needs and direction where it goes.

##  3.1. Introduction
	Project is under a constant development both (even) from conceptual part and implementation.
  Software disribution is splitted into two parts: mining scripts and monitoring of environment which
  sometimes corresponts in some subtle aspects. The biggest and more complex part of the software pack
  is weather/environment monitoring.

##  3.2. Known bugs
###   3.2.1. Reading 1byte from serial (readtemp.py)
         In case of connecting arduino for sensors script readtemp.py reads
         1byte in from serial making too much of overload in communication making the
         whole script "stressing" CPU time.  The possible solution is 

###  3.3. Changelog
```
   .--------------------------------------.
   | Fri Apr  4 23:11:13 CEST 2014        |
   `--------------------------------------'
   * First pre-release
   
```
