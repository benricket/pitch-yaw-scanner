#include <Servo.h>

// Test script to get servos moving

Servo a;
Servo b;

int posA = 0;
int posB = 0;
int pos = 0;

void setup() {
  a.attach(6);
  b.attach(5);
}

void loop() {
  for (pos = 0; pos < 180; pos ++) {
    posA = pos;
    posB = pos;
    a.write(posA);
    a.write(posB);
    delay(15);
  }
  for (pos = 180; pos > 0; pos--) {
    posA = pos;
    posB = pos;
    a.write(posA);
    a.write(posB);
    delay(15);
  }

}