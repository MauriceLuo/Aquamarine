#include <SoftwareSerial.h>  //Software Serial library
#include <PololuMaestro.h>   //Pololu Maestro Library
#include "IOI2C.h"
#include "wit_c_sdk.h"
#include <PID_v1.h>


// IMU相关变量
#define ACC_UPDATE 0x01
#define GYRO_UPDATE 0x02
#define ANGLE_UPDATE 0x04
#define MAG_UPDATE 0x08
#define READ_UPDATE 0x80
static volatile char s_cDataUpdate = 0;

static void CmdProcess(void);
static void AutoScanSensor(void);
static void CopeSensorData(uint32_t uiReg, uint32_t uiRegNum);
static void Delayms(uint16_t ucMs);

#define SensorPin A0         //pH meter Analog output to Arduino Analog Input 0
#define Offset 0.15          //deviation compensate
unsigned long int avgValue;  //Store the average value of the sensor feedback

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


// 以下保持原有IMU处理函数不变
static void CopeSensorData(uint32_t uiReg, uint32_t uiRegNum) {
  int i;
  for (i = 0; i < uiRegNum; i++) {
    switch (uiReg) {
        //            case AX:
        //            case AY:
      case AZ:
        s_cDataUpdate |= ACC_UPDATE;
        break;
        //            case GX:
        //            case GY:
      case GZ:
        s_cDataUpdate |= GYRO_UPDATE;
        break;
        //            case HX:
        //            case HY:
      case HZ:
        s_cDataUpdate |= MAG_UPDATE;
        break;
        //            case Roll:
        //            case Pitch:
      case Yaw:
        s_cDataUpdate |= ANGLE_UPDATE;
        break;
      default:
        s_cDataUpdate |= READ_UPDATE;
        break;
    }
    uiReg++;
  }
}

static void AutoScanSensor(void) {
  int i, iRetry;

  for (i = 0; i < 0x7F; i++) {
    WitInit(WIT_PROTOCOL_I2C, i);
    iRetry = 2;
    do {
      s_cDataUpdate = 0;
      WitReadReg(AX, 3);
      delay(5);
      if (s_cDataUpdate != 0) {
        Serial.print("find ");
        Serial.print(i);
        Serial.print(" addr sensor");
        return;
      }
      iRetry--;
    } while (iRetry);
  }
  Serial.println("can not find sensor\r\n");
  Serial.println("please check your connection\r\n");
}

static void Delayms(uint16_t ucMs) {
  delay(ucMs);
}


void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(115200);
  rs485Serial.begin(57600);
  Serial.println("Ready to communicate in rs485");


  maestroSerial.begin(115200);
  Serial.println("Ready to use Pololu Maestro");

  Serial.println("Ready to use 10 axis IMU");

  rs485Serial.listen();


  // 初始化IMU
  IIC_Init();
  WitInit(WIT_PROTOCOL_I2C, 0x50);
  WitI2cFuncRegister(IICwriteBytes, IICreadBytes);
  WitRegisterCallBack(CopeSensorData);
  WitDelayMsRegister(Delayms);
  AutoScanSensor();
  delay(500);
  Serial.println("welcome to use!");


  for (int i = 0; i < 16; i++) {
    maestro.setAcceleration(i, 20);
    maestro.setSpeed(i, 100);
  }
}




void loop() {

  maestroSerial.stopListening();

  static float fAngle[3];

  // 读取IMU数据
  WitReadReg(AX, 12);

  if (s_cDataUpdate & ANGLE_UPDATE) {
    for (int i = 0; i < 3; i++) {
      fAngle[i] = sReg[Roll + i] / 32768.0f * 180.0f;
    }
    // inputRoll = fAngle[0];
    // inputPitch = -fAngle[1];

    int buf[30];  //buffer for read analog
    avgValue = 0;
    for (int i = 0; i < 30; i++)  //Get 10 sample value from the sensor for smooth the value
    {
      buf[i] = analogRead(SensorPin);
      avgValue += buf[i];
      // delay(10);
    }
    float phValue = (float)avgValue * 5.0 / 1024 / 30;  //convert the analog into millivolt
    //phValue=3.5*phValue+Offset;                      //convert the millivolt into pH value
    phValue = 14 - 5.122 * (phValue - 1.758) + Offset;

    // char output[50];
    // snprintf(output, sizeof(output), "%.2f,%.2f,%.2f", fAngle[0], fAngle[1], fAngle[2]);
    // Serial.print(fAngle[0]);
    // Serial.print(",");
    // Serial.print(fAngle[1]);
    // Serial.print(",");
    // Serial.print(fAngle[2]);
    // Serial.print(",");
    // Serial.print(output);
    // Serial.println();

    // if (rs485Serial.available()) {

    String input = rs485Serial.readStringUntil('\n');
    input.trim();
    Serial.println(input);

    rs485Serial.print(fAngle[0]);
    rs485Serial.print(",");
    rs485Serial.print(fAngle[1]);
    rs485Serial.print(",");
    rs485Serial.print(fAngle[2]);
    rs485Serial.print(",");
    rs485Serial.print(phValue);
    rs485Serial.println();

    if (input.length() == 52) {

      for (int i = 0; i < 13; i++) {
        String substring = input.substring(i * 4, (i + 1) * 4);  // Extract 4 characters at a time
        PWM[i] = substring.toInt();                              // Convert the substring to an integer
      }


      maestro.setTarget(5, PWM[0]);
      maestro.setTarget(1, PWM[1]);
      maestro.setTarget(6, PWM[2]);
      maestro.setTarget(2, PWM[3]);

      maestro.setTarget(0, PWM[4]);
      maestro.setTarget(3, PWM[4]);
      maestro.setTarget(4, PWM[4]);
      maestro.setTarget(7, PWM[4]);

      for (int i = 5; i < 13; i++) {
        maestro.setTarget((i + 3), PWM[i]);
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
    s_cDataUpdate &= ~ANGLE_UPDATE;
    // }
  }
}