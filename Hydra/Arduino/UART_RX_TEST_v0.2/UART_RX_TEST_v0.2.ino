#include <SoftwareSerial.h>  //Software Serial library
#include <PololuMaestro.h>   //Pololu Maestro Library

//*****RS485 setup BEGIN*****
#define RS485_RX 10  //Arduino Mega RX
#define RS485_TX 11  //Arduino Mega TX

SoftwareSerial rs485Serial(10, 11);  // RX, TX
//*****RS485 setup END*****


//*****Maestro setup BEGIN*****
#define Maestro_RX 13                  //arduino's I/O 50 is the RX, connects to TX of maestro
#define Maestro_TX 12                  //arduino's I/O 51 is the TX, connects to RX of maestro
SoftwareSerial maestroSerial(13, 12);  //sets up this UART serial port

MiniMaestro maestro(maestroSerial);  //defines the maestro as an object
//*****Maestro setup END*****


#define maniLeftBase 0
#define maniLeftArm 1
#define maniLeftWrist 2
#define maniLeftClaw 3

#define maniRightBase 4
#define maniRightArm 5
#define maniRightWrist 6
#define maniRightClaw 7

#define rovFrontLeft 8
#define rovFrontRight 9
#define rovRearLeft 10
#define rovRearRight 11

#define vertFrontLeft 12
#define vertFrontRight 13
#define vertRearLeft 14
#define vertRearRight 15


#define tick 5  //ms

const int ACCEL[16] = { 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15 };
const int SPEED[16] = { 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10 };


const int maxValues = 13;  // Hard limit to 13 sets of 4-digit numbers
int values[maxValues];     // Array to store the converted integers

char* formatFloatArray(float arr[], int size, char* output, int buffSize) {
  output[0] = '\0';  // Ensure empty string
  for (int i = 0; i < size; i++) {
    char temp[10];
    dtostrf(arr[i], 0, 2, temp);  // Convert float to string
    strcat(output, temp);
    if (i < size - 1) {
      strcat(output, ",");
    }
  }
  return output;
}

int PWM[13];  // Array to store the 13 PWM as integers
String output = "";

void setup() {

  Serial.begin(115200);
  rs485Serial.begin(57600);
  Serial.println("Ready to communicate in rs485");


  maestroSerial.begin(115200);
  Serial.println("Ready to use Pololu Maestro");

  Serial.println("Ready to use 10 axis IMU");

  rs485Serial.listen();

  for (int i = 0; i < 16; i++) {
    maestro.setAcceleration(i, 20);
    maestro.setSpeed(i, 100);
  }
}



void loop() {


  maestroSerial.stopListening();

  if (rs485Serial.available()) {

    String input = rs485Serial.readStringUntil('\n');
    input.trim();
    Serial.println(input);

    rs485Serial.println(input);

    if (input.length() == 52) {

      for (int i = 0; i < 13; i++) {
        String substring = input.substring(i * 4, (i + 1) * 4);  // Extract 4 characters at a time
        PWM[i] = substring.toInt();                              // Convert the substring to an integer
      }
    }

    maestro.setTarget(5, PWM[0]);
    maestro.setTarget(1, PWM[1]);
    maestro.setTarget(6, PWM[2]);
    maestro.setTarget(2, PWM[3]);

    maestro.setTarget(0, PWM[4]);
    maestro.setTarget(3, PWM[4]);
    maestro.setTarget(4, PWM[4]);
    maestro.setTarget(7, PWM[4]);

    for(int i = 5; i < 13; i++){
        maestro.setTarget((i+3), PWM[i]);
    }
  }

  //output = String("1243,1434,5212,2354");




  /*
  maestro.setAcceleration(8, 15);
  maestro.setSpeed(8, 20);
  maestro.setTarget(8, 6000);


  maestro.setAcceleration(9, 15);
  maestro.setSpeed(9, 20);
  maestro.setTarget(9, 8000);*/

  delay(tick);
  Serial.println();
}