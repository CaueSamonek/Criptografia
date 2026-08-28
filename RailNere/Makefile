HEADER_DIR = headers/
SOURCE_DIR = src/

CC = gcc
CFLAGS = -Wall -Wextra -g --pedantic -I $(HEADER_DIR)

EXEC = railnere
MAIN = railnere.c
OBJS = 

all: $(EXEC) clean

$(EXEC): $(SOURCE_DIR)$(MAIN) $(OBJS)
	$(CC) $(CFLAGS) -o $@ $< $(OBJS)

%.o: $(SOURCE_DIR)%.c $(HEADER_DIR)%.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS)

purge: clean
	rm -f $(EXEC)
