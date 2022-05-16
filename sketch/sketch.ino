#include <Servo.h>
int incomingByte;
Servo motor_L;
Servo motor_R;

void setup() {
  Serial.begin(9600);
  motor_L.attach(12, 1000, 2000);
  motor_R.attach(13, 1000, 2000);
}


void loop() {
  int value = analogRead(A0);
  Serial.println(value);
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    switch (incomingByte){
      case 'F':
        motor_L.write(180);
        motor_R.write(180);
        break;
      case 'B':
        motor_L.write(0);
        motor_R.write(0);
        break;
      case 'S':
        motor_L.write(90);
        motor_R.write(90);
        break;
      case 'L':
        motor_L.write(90);
        motor_R.write(180);
        break;
      case 'R':
        motor_L.write(180);
        motor_R.write(90); 
        break;
    }
    }
  }
