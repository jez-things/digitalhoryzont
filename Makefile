
install: /usr/local/sbin/readtemp.py /etc/init.d/readtemp
	@echo "installing"
	install -m 755 readtemp.py /usr/local/sbin/readtemp.py
	install -o root -g root -m 755 misc/readtemp /etc/init.d/readtemp

/usr/local/sbin/readtemp:
	@echo "Installing readtemp script"
	install -m 755 readtemp.py /usr/local/sbin/readtemp.py

/etc/init.d/readtemp: /usr/local/sbin/readtemp
	@echo "Installing readtemp init script"
	@install -o root -g root -m 755 misc/readtemp /etc/init.d/readtemp

clean:
	@echo "Cleaning"


