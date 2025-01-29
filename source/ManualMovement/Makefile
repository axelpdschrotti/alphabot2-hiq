# Compiler
CXX = g++
CXXFLAGS = -Wall -lwiringPi

# Executable name
TARGET = alphabot_control

# Source files
SRCS = main.cpp ManualMovement.cpp
OBJS = $(SRCS:.cpp=.o)

# Default rule
all: $(TARGET)

# Build the executable
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

# Compile object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f $(TARGET) $(OBJS)
