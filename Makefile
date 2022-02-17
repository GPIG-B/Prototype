SHELL=/bin/sh
MAKE=make
SUBDIRS=datagen/ common/ sensor_service/ drone_scheduling/ dashboard/
.PHONY: clean


all: $(SUBDIRS)
	@for i in $(SUBDIRS); do \
        echo "make all in '$$i'..."; \
        (cd $$i; $(MAKE) $(MFLAGS) all); done

clean: $(SUBDIRS)
	@for i in $(SUBDIRS); do \
        echo "make clean in '$$i'..."; \
        (cd $$i; $(MAKE) $(MFLAGS) clean); done
