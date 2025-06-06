#include <SoftwareSerial.h>  //Software Serial library
#include <PololuMaestro.h>   //Pololu Maestro Library
#include "IOI2C.h"
#include "wit_c_sdk.h"
#include <PID_v1.h>

int vertThrustMax = 7100;
int vertThrustMin = 4800;

// PID参数（初始化）
//double Kp = 5.0, Ki = 0, Kd = 0;
double pidConst[3] = {5.0, 0, 0};
// double setpointRoll = 0, setpointPitch = 0;  // 水平状态目标值

// PID目标值改为动态设置
double setpointRoll, setpointPitch;

// PID输入输出变量
double inputRoll, inputPitch;
double outputRoll, outputPitch;

// 创建PID控制器实例
PID rollPID(&inputRoll, &outputRoll, &setpointRoll, pidConst[0] , pidConst[1], pidConst[2], DIRECT);
PID pitchPID(&inputPitch, &outputPitch, &setpointPitch, pidConst[0] , pidConst[1], pidConst[2], DIRECT);

// 新增初始角度存储变量
float angle_init[2] = { 0 };  // [0]: Roll初始值, [1]: Pitch初始值
bool isCalibrated = false;    // 校准完成标志

// 水平检测参数
#define LEVEL_THRESHOLD 1  // 单位：度

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

// 新增校准函数
void CalibrateInitialAngle() {
  float sumRoll = 0, sumPitch = 0;
  for (int i = 0; i < 30; i++) {
    WitReadReg(AX, 12);
    delay(10);
    sumRoll += sReg[Roll] / 32768.0f * 180.0f;
    sumPitch += sReg[Pitch] / 32768.0f * 180.0f;
  }
  setpointRoll = sumRoll / 31;
  setpointPitch = sumPitch / 31;

  Serial.print("Calibrated Initial Angle - Roll: ");
  Serial.print(setpointRoll);
  Serial.print("°, Pitch: ");
  Serial.println(setpointPitch);
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


  // 初始化PID
  rollPID.SetMode(AUTOMATIC);
  pitchPID.SetMode(AUTOMATIC);
  rollPID.SetOutputLimits(-100, 100);
  pitchPID.SetOutputLimits(-100, 100);
  rollPID.SetSampleTime(10);
  pitchPID.SetSampleTime(10);

  Serial.println("System Initialized");

  delay(1000);
  // 初始校准（新增部分）
  CalibrateInitialAngle();

  for (int i = 0; i < 16; i++) {
    maestro.setAcceleration(i, 20);
    maestro.setSpeed(i, 100);
  }
}


void loop() {

  maestroSerial.stopListening();

  static float fAngle[3];
  int Thruster[8];

  // 读取IMU数据
  WitReadReg(AX, 12);

  if (s_cDataUpdate & ANGLE_UPDATE) {
    for (int i = 0; i < 3; i++) {
      fAngle[i] = sReg[Roll + i] / 32768.0f * 180.0f;
    }
    inputRoll = -fAngle[0];
    inputPitch = -fAngle[1];

    // 首次运行自动校准（新增）
    if (!isCalibrated) {
      CalibrateInitialAngle();
      isCalibrated = true;
    }


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
    rs485Serial.print(",");

    if (input.length() == 53) {

      for (int i = 0; i < 13; i++) {
        String substring = input.substring(i * 4, (i + 1) * 4);  // Extract 4 characters at a time
        PWM[i] = substring.toInt();                              // Convert the substring to an integer
      }

      int pid_val[4];
      int isAutoLevelEnable = 0;
      String substring = input.substring(52, 53);
      isAutoLevelEnable = substring.toInt();

      for (int i = 0; i < 3; i++){
        String substring = input.substring(i * 3 + 53, (i + 1) * 3 + 53);
        pidConst[i] = substring.toInt()/10;
      }

      if (isAutoLevelEnable == 1) {
        rollPID.SetMode(AUTOMATIC);
        pitchPID.SetMode(AUTOMATIC);
        rollPID.Compute();
        pitchPID.Compute();
      } 
      else {
        rollPID.SetMode(MANUAL);
        pitchPID.SetMode(MANUAL);
        rollPID.SetTunings(pidConst[0] , pidConst[1], pidConst[2]);
        pitchPID.SetTunings(pidConst[0] , pidConst[1], pidConst[2]);
        outputPitch = 0;
        outputRoll = 0;
        for (int i; i < 4; i++) {
          pid_val[i] = 0;
        }
      }

      //pid(pid_val[4]);
      pid_val[0] = map(outputPitch + outputRoll, -100, 100, -1200, 1100);
      pid_val[1] = map(-outputPitch + outputRoll, -100, 100, -1200, 1100);
      pid_val[2] = map(-outputPitch - outputRoll, -100, 100, -1200, 1100);
      pid_val[3] = map(outputPitch - outputRoll, -100, 100, -1200, 1100);
/*
      int Thruster1 = constrain(PWM[4] + pid_val[0], vertThrustMin, vertThrustMax);
      int Thruster4 = constrain(PWM[4] + pid_val[1], vertThrustMin, vertThrustMax);
      int Thruster3 = constrain(PWM[4] + pid_val[2], vertThrustMin, vertThrustMax);
      int Thruster2 = constrain(PWM[4] + pid_val[3], vertThrustMin, vertThrustMax);
*/
      for (int i = 0; i < 4; i++){
        Thruster[i] = PWM[i];
        Thruster[i+4] = PWM[4] + pid_val[i];
      }

      Thruster[4] = map(Thruster[4],4000,8000,8000,4000);
      Thruster[6] = map(Thruster[6],4000,8000,8000,4000);

      for (int i = 0;i < 8; i++){
        Thruster[i] = constrain(Thruster[i], vertThrustMin, vertThrustMax);
      }
      
      int magic_thruster_index[8] = {5, 1, 6, 2, 0, 3, 7, 4};

      for ( int i = 0; i < 8; i++ ){
        maestro.setTarget(magic_thruster_index[i], Thruster[i]);
      }
/*
      maestro.setTarget(5, Thruster[0]);
      maestro.setTarget(1, Thruster[1]);
      maestro.setTarget(6, Thruster[2]);
      maestro.setTarget(2, Thruster[3]);

      maestro.setTarget(0, Thruster[4]);  //pid_val[0]
      maestro.setTarget(3, Thruster[5]);  //pid_val[1]
      maestro.setTarget(7, Thruster[6]);  //pid_val[2]
      maestro.setTarget(4, Thruster[7]);  //pid_val[3]
*/
      for (int i = 5; i < 13; i++) {
        maestro.setTarget((i + 3), PWM[i]);
      }

      rs485Serial.print(Thruster[4]);
      rs485Serial.print(",");
      rs485Serial.print(Thruster[5]);
      rs485Serial.print(",");
      rs485Serial.print(Thruster[7]);
      rs485Serial.print(",");
      rs485Serial.print(Thruster[6]);
      rs485Serial.print(",");
      rs485Serial.print(isAutoLevelEnable);
      rs485Serial.print(",");
      rs485Serial.print(outputRoll);
      rs485Serial.print(",");
      rs485Serial.print(outputPitch);
      rs485Serial.print(",");
      rs485Serial.print(setpointRoll);
      rs485Serial.print(",");
      rs485Serial.print(setpointPitch);
      rs485Serial.println();
    }

    delay(tick);
    Serial.println();
    s_cDataUpdate &= ~ANGLE_UPDATE;
    // }
  }
}
