#ifndef MANMOVE_HPP
#define MANMOVE_HPP

#include <wiringPi.h>
#include <softPwm.h>
#include <iostream>
#include <termios.h>
#include <unistd.h>

// Motor control pins
#define IN1 13
#define IN2 12
#define ENA 6
#define IN3 21
#define IN4 20
#define ENB 26

class ManualMovement {
public:
    ManualMovement();
    ~ManualMovement();

    void moveForward();
    void moveBackward();
    void turnLeft();
    void turnRight();
    void stopBot();
    void increaseSpeed();
    void decreaseSpeed();

private:
    int speed;
    char getKeyPress(); // Function to read keyboard input
};

#endif // MANMOVE_HPP
