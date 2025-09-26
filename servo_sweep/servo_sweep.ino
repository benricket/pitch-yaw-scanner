#include <Servo.h>

/*
Arduino script to sweep two servos across given angles when reading
data from a distance sensor. Works in conjunction with a Python 
script to listen to the data relayed over serial and send commands
over serial instructing the servos to begin movement.

Written by Ben Ricket and Nathaniel Banse
*/ 

Servo pitch_servo;
Servo yaw_servo;

// Specify pins for pitch and yaw servos
int PITCH_PIN = 5;
int YAW_PIN = 6;
int SENSOR_PIN = A0;

// Specify intervals of servo movement
float PITCH_STEP = 1;
float YAW_STEP = 1;

int LOW_READ_THRESHOLD = 80; // Ignore points worse than this
int READ_ATTEMPTS = 10; // attempts to give reading > threshold

int MS_PER_ITER = 20; // Delay on pitch movement
int MS_PER_ITER_LARGE = 300; // Delay on yaw movement

int pitch_min;
int pitch_max;
int yaw_min;
int yaw_max;

// Passed by Python script, determines if scan should be running
int run_servos = 0;

// Commands passed by Python script to instruct servo behavior
enum RunCommand {SERVO_STOP = 1, SERVO_HORIZONTAL_START = 2, SERVO_VERTICAL_START = 3, SERVO_BOTH_START = 4, CALIBRATE = 5};

void writeToSerial(float pitch_in, float yaw_in, int reading_in) {
  // Write the servo position and distance sensor information on serial
  // Pitch, yaw, and the analog input are passed with commas as delimeter
  // Newline delineates end of a single measurement
  Serial.print(pitch_in);
  Serial.print(",");
  Serial.print(yaw_in);
  Serial.print(",");
  Serial.println(reading_in);
}

void setup() {
  long baudRate = 9600; 
  Serial.begin(baudRate);
  pitch_servo.attach(PITCH_PIN);
  yaw_servo.attach(YAW_PIN);
  pinMode(SENSOR_PIN, INPUT);
}

void loop() {
  // Attempt to read serial data from Python script
  unsigned long current_time;
  int serial_read;
  if (Serial.available() > 0) {
    serial_read = Serial.parseInt();
    switch (serial_read) {
      // Declare movement limits based on command
      case SERVO_STOP:
        run_servos = 0;
        break;
      case SERVO_HORIZONTAL_START:
        pitch_min = 105;
        pitch_max = 105;
        yaw_min = 65;
        yaw_max = 115;
        run_servos = 1;
        break;
      case SERVO_VERTICAL_START:
        pitch_min = 80;
        pitch_max = 130;
        yaw_min = 90;
        yaw_max = 90;
        run_servos = 1;
        break;
      case SERVO_BOTH_START:
        pitch_min = 80;
        pitch_max = 130;
        yaw_min = 65;
        yaw_max = 115;
        run_servos = 1;
        break;
      case CALIBRATE:
        // Take a single measurement for calibration
        pitch_min = 120;
        pitch_max = 120;
        yaw_min = 45;
        yaw_max = 45;
        run_servos = 1;
        break;
      default:
        break;
    }
  }
  if (run_servos) {
    // Sweep across pitch
    for (float yaw = yaw_min; yaw <= yaw_max; yaw += YAW_STEP) {
      current_time = millis();
      yaw_servo.write(yaw);

      // Delay to allow servo time to fully move
      while (millis() - current_time < MS_PER_ITER_LARGE) {
        delay(1);
      }

      for (float pitch = pitch_min; pitch <= pitch_max; pitch += PITCH_STEP) {
        current_time = millis();

        // After writing servo position, wait for it to finish moving
        // Moving back from max pitch to min pitch takes more time 
        pitch_servo.write(pitch);
        yaw_servo.write(yaw);

        // Delay to allow servo time to fully move
        if (pitch == pitch_min) {
          while (millis() - current_time < MS_PER_ITER_LARGE) {
            delay(1);
          }
        } else {
          while (millis() - current_time < MS_PER_ITER) {
            delay(1);
          }
        }

        // Attempt reading the sensor data
        int sensor_read = analogRead(SENSOR_PIN);
        int attempts = 1;

        // Values less than LOW_READ_THRESHOLD are not valid measurements
        // Give finite attempts to read valid measurement; give up if not
        while (sensor_read < LOW_READ_THRESHOLD && attempts < READ_ATTEMPTS) {
          sensor_read = analogRead(SENSOR_PIN);
          attempts++;
        }

        // Only write out if measurement was valid
        if (attempts < READ_ATTEMPTS) {
          writeToSerial(pitch,yaw,sensor_read);
        }
      }
    }
    // -1 tells Python script scan is finished
    writeToSerial(-1,-1,-1);
    run_servos = 0;
  }
}