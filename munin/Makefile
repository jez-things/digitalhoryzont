
all: 
	@echo "Development environment"
	@echo "usage: make [cgconfig|cgtest|install]"

cgconfig: cgminer
	@./cgminer config |sed -e 's/^pga/\t\\--&/g' |sed -e 's/^graph/\t| &/g'
	@echo '.============================================='
	@echo '|> Checking values:'
	@echo '`============================================='
	@echo ''
	@./cgminer|sed -e 's/^pga/\t\\--&/g' |sed -e 's/^graph/\t| &/g'
	#(./cgminer config && ./cgminer) | awk '/^multigraph/{print "\tmulti";next;} {print $$1"="$$2;} '


install: cgminer
	@echo "Installing $<"
	@install -C -m 755 -o root -b $< /etc/munin/plugins/$< 
