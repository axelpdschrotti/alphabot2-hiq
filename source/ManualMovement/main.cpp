#include "ManualMovement.hpp"

int main() {
    ManualMovement robot;
    wiringPiSetupGpio();

    std::cout << "Use 'w' for forward, 's' for backward, 'a' for left, 'd' for right, 'q' to stop, '+' to increase speed, '-' to decrease speed, and 'x' to exit." << std::endl;

    while (true) {
        char key;
        std::cin >> key; // Capture user input

        switch (key) {
            case 'w':
                std::cout << "Moving Forward" << std::endl;
                robot.moveForward();
                break;
            case 's':
                std::cout << "Moving Backward" << std::endl;
                robot.moveBackward();
                break;
            case 'a':
                std::cout << "Turning Left" << std::endl;
                robot.turnLeft();
                break;
            case 'd':
                std::cout << "Turning Right" << std::endl;
                robot.turnRight();
                break;
            case 'q':
                std::cout << "Stopping" << std::endl;
                robot.stopBot();
                break;
            case '+':
                robot.increaseSpeed();
                break;
            case '-':
                robot.decreaseSpeed();
                break;
            case 'x':
                std::cout << "Exiting program..." << std::endl;
                return 0;
            default:
                break;
        }
    }
}
