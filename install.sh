#!/bin/sh -C


# Define variable SKIP_DEPENDENCIES=yes to omit installation of dependencies.
# In case of cloned/changed git URL You can define REPOSITORY_URL environment
# variable. Adding more dependencies is possible via DH_DEPS variable.
# To install/enable more plugins You have to redefine ENABLED_PLUGINS variable
# To increase debugging messages define environment variable DEBUG_MODE with
# value greater than 0.
: ${INSTALLDIR:=""}
: ${DEBUG_MODE:=0};
: ${ENABLED_PLUGINS:='cgminer bitcurex.py polmine'}
: ${REPOSITORY_URL:='https://github.com/jezjestem/digitalhoryzont.git'}
: ${DH_DEPS:='munin-node python'}

dprint () {
	[ "$DEBUG_MODE" -gt 0 ] && echo $@
}

munin_plugins () {
	if [ ! -d /etc/munin/plugins ] ; then
		echo "|==> munin-node is not installed!"
		return 0;
	fi
	for plugin in ${ENABLED_PLUGINS};
	do
		echo "|==> installing $plugin"
		dprint "install -b -v -m 755 -o root munin/$plugin /etc/munin/plugins/$plugin"
		install -b -v -m 755 -o root munin/$plugin /etc/munin/plugins/$plugin
	done
#cat <<- END
#END
}

install_dependencies () {
	echo "|==> Installing software dependencies (supported only on rasbian)"
	if ! which dpkg > /dev/null 2>&1; then
		echo 'dpkg is not available. Aborting dependency installation.'
		return 1;
	fi
	for dep in ${DH_DEPS};
	do
		dprint "|\`=> Checking $dep"
		if ! dpkg -l $dep > /dev/null 2>&1; then
			dprint "|===> $dep not installed!"
			apt-get install -y $dep
		fi
	done

}

###################################
# main
###

[ -z "${SKIP_DEPENDENCIES}" ] && install_dependencies;
#INSTALLDIR=$(mktemp -d '/tmp/digitalhoryzont.XXXXXXX') XXX

dprint "|> Installing digitalhoryzont"
echo "|> Installing munin plugins"
munin_plugins
exit 0; # XXX ugly hack

dprint "|=> Temporary directory \"$INSTALLDIR\""
#cd $INSTALLDIR
#git clone -q "${REPOSITORY_URL}"

if [ ! -d digitalhoryzont ]; then
	dprint "oops something went wrong. Directory \"digitalhoryzont\" does not exists!"
	exit 3
fi

cd digitalhoryzont
munin_plugins
cd ..


