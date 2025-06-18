#include <ESP32Servo.h>  // Use ESP32Servo library instead of regular Servo

Servo myServo;
int pos = 0;

// ESP32 has different pin numbering - GPIO pins
const int servoPin = 2;  // You can use GPIO13 as an example servo pin on ESP32

void setup() {
  // Higher baud rate for ESP32 is common
  Serial.begin(115200);
  
  // ESP32 specific servo setup
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  
  // Standard 50Hz PWM for servos
  myServo.setPeriodHertz(50);
  
  // Attach the servo to the specified pin
  myServo.attach(servoPin, 500, 2400); // min/max pulse width in microseconds
  
  // Initialize position
  myServo.write(0);
  
  Serial.println("ESP32 Servo Control Ready");
}

void loop() {
  // Serial.println("Enter position (0-180): ");    
  // while (Serial.available() == 0) {
  //   delay(10);  // Small delay to prevent hogging CPU
  // }        
  pos += 20;  
  myServo.write(pos); 
  delay(10000);
  // pos += 20;  
  // delay(20000);
  // Serial.read(); // Clear any remaining characters (like newline)
  
  // if (pos >= 0 && pos <= 180) {
  //    myServo.write(pos);
  //    Serial.print("Turned to ");                   
  //    Serial.println(pos);
  //    Serial.flush();               
  // }
  // else {
  //    Serial.println("Invalid position (0-180 only)");
  // }
}