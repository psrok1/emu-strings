CC = i686-w64-mingw32-gcc
OBJ =\
	log.o \
	bstr.o \
	bstrchain.o \
	bstrreport.o \
	main.o \
	bench.o

all: main

.c.o:
	$(CC) -c $(INCLUDES) $(CFLAGS) $<

main: $(OBJ)
	$(CC) $(OBJ) $(LIBS) -o winedrop.dll -shared -Wl,--kill-at
