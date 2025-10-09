# Compiler
CXX = g++
# Compiler flags
CXXFLAGS = -Wall -std=c++17
# Target executable
TARGET = main
# Source files
SRCS = main.cpp Counter.cpp
# Object files
OBJS = $(SRCS:.cpp=.o)

all: 