#!/bin/sh
MAIN_LED_GPIO=24
G_STATE="valid"

init_led () {
	[ -x /usr/local/bin/gpio ] && /usr/local/bin/gpio export ${1:-24}  out
}

set_led () {
	lfunc="${1:?too few arguments}"

	case ${lfunc} in
		up)
			echo 1 > /sys/class/gpio/gpio24/value
			;;
		down)
			echo 0 > /sys/class/gpio/gpio24/value
			;;
		blink)
			n=10
			while [ $n -ge 0 ]; 
			do
				echo 1 > /sys/class/gpio/gpio24/value
				sleep 1
				echo 0 > /sys/class/gpio/gpio24/value
				sleep 1
				: $((n=n-1))
			done
			;;
	esac
}

set_state () {
	lstate=${1:-unknown}
	case ${lstate} in
		valid)
			G_STATE="valid"
			set_led up;
			;; 
		error)
			G_STATE="error"
			set_led blink;
			return 0
			;;
		*)
			G_STATE="${lstate}"
			set_led down;
			echo "unknown led state specified\"${lstate}\""|logger 
			return 0
			;;

	esac
	return 1;
}

check_ds18b20 () {
	ds18_cnt=$(egrep -c '28-[a-fA-F0-9]*' /sys/bus/w1/devices/w1_bus_master1/w1_master_slaves )
	if [ $ds18_cnt -lt 3 ]; then
		return 0;
	fi
	return 1;
}

check_inet () {
	if ! ping -W 1 -c 4 10.8.0.1 > /dev/null 2>&1; then
		return 0;
	fi
	return 1;	
}

do_stdtest () {

	set_state "valid";
	if check_ds18b20; then
		echo 'problem with i2c bus' | logger 
		set_state "error";
	fi
	if check_inet; then
		echo 'problem with internet connection' | logger
		set_state "error";
	fi
}

do_init () {
	echo 'initialization of leds' | logger 
	init_led;
}

#########################################################################
# main
######

cmd=${1:-stdtest}
case ${cmd} in
	init)
		do_init;
		;;
	stdtest)
		do_stdtest;
		;;
	shutdown)
		set_state shutdown;
		;;
	*)
		echo "usage: $0 [stdtest|shutdown|init]"
		exit 64
		;;
esac
