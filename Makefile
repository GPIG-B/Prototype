SHELL=/bin/sh
MAKE=make
SUBDIRS=datagen/ manager/ sensor_service/ drone_scheduling/ dashboard/
CLI_FILES=$(shell find -name cli.py -not -path "./.*")
.PHONY: clean all


all: $(SUBDIRS)
	chmod +x $(CLI_FILES)
	@for i in $(SUBDIRS); do \
        echo "make all in '$$i'..."; \
        (cd $$i; $(MAKE) $(MFLAGS) all); done

clean: $(SUBDIRS)
	@for i in $(SUBDIRS); do \
        echo "make clean in '$$i'..."; \
        (cd $$i; $(MAKE) $(MFLAGS) clean); done
