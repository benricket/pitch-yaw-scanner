#include <Servo.h>

// Test script to get servos moving

Servo pitch_servo;
Servo yaw_servo;

int posA = 0;
int posB = 0;
int pos = 0;

// Specify pins for pitch and yaw servos
int PITCH_PIN = 5;
int YAW_PIN = 6;
int SENSOR_PIN = A0;

// Specify ranges and intervals of servo movement
float PITCH_MIN = 0; 
float PITCH_MAX = 90;
float PITCH_STEP = 5;
float YAW_MIN = 0;
float YAW_MAX = 90;
float YAW_STEP = 5;

int LOW_READ_THRESHOLD = 80;
int READ_ATTEMPTS = 10;

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
  // Sweep across pitch
  for (float pitch = PITCH_MIN; pitch <= PITCH_MAX; pitch += PITCH_STEP) {
    pitch_servo.write(pitch);
    for (float yaw = YAW_MIN; yaw <= YAW_MAX; yaw += YAW_STEP) {
      yaw_servo.write(yaw);
      int sensor_read = analogRead(SENSOR_PIN);
      int attempts = 1;
      while (sensor_read < LOW_READ_THRESHOLD && attempts < READ_ATTEMPTS) {
        sensor_read = analogRead(SENSOR_PIN);
      }

      if (attempts < READ_ATTEMPTS) {
        writeToSerial(pitch,yaw,sensor_read);
      }
    }
  }
  writeToSerial(-1,-1,-1);
}