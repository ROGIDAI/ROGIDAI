
CXX = g++
CXXFLAGS = -std=c++17

all: task3.exe

task3.exe: task3.o functions.o
	$(CXX) task3.o functions.o -o task3.exe

task3.o: task3.cpp functions.h
	$(CXX) $(CXXFLAGS) -c task3.cpp -o task3.o

functions.o: functions.cpp functions.h
	$(CXX) $(CXXFLAGS) -c functions.cpp -o functions.o

aux: functions.o


clean:
	powershell.exe -NoProfile -Command "Remove-Item -Path *.o,task3.exe -Force -ErrorAction SilentlyContinue"

.PHONY: all aux clean
