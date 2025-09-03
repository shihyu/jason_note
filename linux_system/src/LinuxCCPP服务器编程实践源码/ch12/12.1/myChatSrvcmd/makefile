GCC ?= gcc
CCMODE = PROGRAM
INCLUDES =  -I/usr/include/mysql
CFLAGS =  -Wall $(MACRO) 
TARGET = gameSrv
SRCS := $(wildcard *.c)   
LIBS = -lmysqlclient



ifeq ($(CCMODE),PROGRAM)
$(TARGET): $(LINKS) $(SRCS) 
	$(GCC) $(CFLAGS) $(INCLUDES) -o $(TARGET)  $(SRCS) $(LIBS)
	@chmod +x $(TARGET)
	@echo make $(TARGET) ok.
clean:
	rm -rf $(TARGET)
endif

 
 

