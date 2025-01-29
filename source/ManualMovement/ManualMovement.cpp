#include "ManualMovement.hpp"

// Constructor: Initialize GPIO and motors
ManualMovement::ManualMovement() {
    wiringPiSetupGpio();  // Initialize WiringPi using GPIO numbering

    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(ENA, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
    pinMode(ENB, OUTPUT);

    // Set initial PWM speed (50%)
    speed = 50;
    softPwmCreate(ENA, speed, 100);
    softPwmCreate(ENB, speed, 100);
}

// Destructor: Stop motors on exit
ManualMovement::~ManualMovement() {
    stopBot();
}

// Move Forward
void ManualMovement::moveForward() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
}

// Move Backward
void ManualMovement::moveBackward() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
}

// Turn Left
void ManualMovement::turnLeft() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
}

// Turn Right
void ManualMovement::turnRight() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
}

// Stop Motors
void ManualMovement::stopBot() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
}

// Increase Speed
void ManualMovement::increaseSpeed() {
    if (speed < 100) speed += 10;
    softPwmWrite(ENA, speed);
    softPwmWrite(ENB, speed);
    std::cout << "Speed increased to " << speed << "%" << std::endl;
}

// Decrease Speed
void ManualMovement::decreaseSpeed() {
    if (speed > 10) speed -= 10;
    softPwmWrite(ENA, speed);
    softPwmWrite(ENB, speed);
    std::cout << "Speed decreased to " << speed << "%" << std::endl;
}

// Function to read single key press
char ManualMovement::getKeyPress() {
    struct termios oldt, newt;
    char ch;
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    ch = getchar();
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    return ch;
}
