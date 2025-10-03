
CC = gcc
CFLAGS = -O2 -Wall -Wextra

all: master

master: master.c
	$(CC) $(CFLAGS) -o master master.c

clean:
	rm -f master

