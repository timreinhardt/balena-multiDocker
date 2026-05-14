APP := c-demo

CC := gcc

SRC_DIR := .
BUILD_DIR := build

SRCS := $(SRC_DIR)/main.c
OBJS := $(BUILD_DIR)/main.o

CFLAGS := -Wall -Wextra -Werror -std=c11 -O2
CPPFLAGS := -DAPP_NAME=\"$(APP)\"
LDFLAGS :=

.PHONY: all clean run

all: $(APP)

$(APP): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

$(BUILD_DIR)/main.o: $(SRC_DIR)/main.c | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

run: $(APP)
	./$(APP)

clean:
	rm -rf $(BUILD_DIR) $(APP)

test:
	./test.sh
