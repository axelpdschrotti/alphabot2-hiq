# alphabot2-hiq
Codebase for internal training project at HiQ with an alphabot2-pi


Authors:
Idris Sahil
Axel Schrotti


Packages required:

Python:
RPi.GPIO
tkinter
math
time
threading
keyboard


C++:
wiringPi
iostream
termios
unistd

If there is trouble when building the manual control executable for c++, try suing this: g++ -o alphabot_control main.cpp ManualMovement.cpp -I/usr/local/incl
ude -L/usr/local/lib -lwiringPi