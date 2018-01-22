
CC      = gcc
CFLAGS  = -g -O2 -fno-strict-aliasing -pipe -Wall -W -Wold-style-definition -D_FORTIFY_SOURCE=2 -DNO_XFS -D_LARGEFILE64_SOURCE -D_GNU_SOURCE
LDFLAGS =

FSX = fsx-linux

all: $(FSX)

$(FSX): $(FSX).c
	$(CC) $(FSX).c $(CFLAGS) -o $(FSX) $(LDFLAGS)

install:
	cp -av $(FSX) $(VIRTUAL_ENV)/bin/

clean:
	rm -rf $(FSX) $(FSX).o
