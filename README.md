## Depth Scanner

This project implements a simple depth scanner using an Arduino Uno, two servos, an IR depth scanner, and a Python script running on the host machine for data processing and visualization. This was developed as the second mini-project for the Principals of Integrated Engineering (PIE) class.

Python code, Arduino code, and the CAD for the sensor mount are included in the repository.

### Requirements

Python requirements can be installed via the requirements.txt file with ```pip -r requirements.txt```.
The Python script requires a serial connection be established to a microcontroller board running the given Arduino C++ code, with connections to two servos, each providing an axis of rotation, and an analog distance sensor.  