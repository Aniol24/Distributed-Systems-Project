CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra

# Executable name
TARGET := program.exe

SRC_DIRS := Client Master Message
SRCS := $(wildcard $(addsuffix /*.cpp, $(SRC_DIRS))) main.cpp
OBJS := $(SRCS:.cpp=.o)


all: $(TARGET)

$(TARGET): $(OBJS)
	@echo "Linking $@ ..."
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS)
	@echo "Build complete!"

%.o: %.cpp
	@echo "Compiling $< ..."
	$(CXX) $(CXXFLAGS) -c $< -o $@

run-server: $(TARGET)
	./$(TARGET) server 12345

run-client: $(TARGET)
	./$(TARGET) client 127.0.0.1 12345 rw

clean:
	@echo "Cleaning object files..."
	rm -f $(OBJS)

fclean: clean
	@echo "Removing binary..."
	rm -f $(TARGET)

re: fclean all

.PHONY: all clean fclean re run-server run-client
