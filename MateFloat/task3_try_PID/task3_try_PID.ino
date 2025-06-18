#include <Wire.h>
#include "MS5837.h"
#include <esp_now.h>
#include <WiFi.h>
#include <ESP32Time.h>
#include <ESP32Servo.h>

Servo myServo;
MS5837 sensor;
ESP32Time rtc(0);

//variables for PID
float Kp = 30, Ki = 0, Kd = 5.0;
float integral = 0, lastError = 0;
unsigned long lastTime = 0;
unsigned long now;
//float PID_goal = 1.25;
float dt, error, proportional, derivative, output;


#define goal_depth 2.5  //in m
int old_time = 0;
int state = 0;
int pointer = 0;
int send_pointer = 0;
int profile_time = 0;
bool sendSuccess = false;
int angle = 9;
int servoPin = 2;
unsigned long previousMillis = 0;
unsigned long float_count_time = 0;


// Variables for sending data
#define company_no "R01"
float depth;
String sendTime;
int count_time = 0;
char msgPacket[200][32];

uint8_t broadcastAddress[] = { 0xF4, 0x65, 0x0B, 0xE8, 0x2C, 0xC4 };
esp_now_peer_info_t peerInfo;

// Callback function called when data is sent
void OnDataSent(const uint8_t* mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
  sendSuccess = (status == ESP_NOW_SEND_SUCCESS);
}

void setup() {
  Serial.begin(115200);
  //init depth sensor
  Wire.begin();
  sensor.init();
  sensor.setModel(MS5837::MS5837_02BA);
  sensor.setFluidDensity(997);  // kg/m^3 (997 for freshwater, 1029 for seawater)

  WiFi.mode(WIFI_STA);

  // // ESP32 specific servo setup
  // ESP32PWM::allocateTimer(0);
  // ESP32PWM::allocateTimer(1);
  // ESP32PWM::allocateTimer(2);
  // ESP32PWM::allocateTimer(3);

  // Standard 50Hz PWM for servos
  myServo.setPeriodHertz(50);

  // Attach the servo to the specified pin
  myServo.attach(servoPin, 500, 2400);  // min/max pulse width in microseconds


  //init esp_now
  esp_now_init();
  // if (esp_now_init() != ESP_OK) {
  //   Serial.println("Error initializing ESP-NOW");
  //   while (1);
  //   return;
  // }

  // Register the send callback
  esp_now_register_send_cb(OnDataSent);

  // Register peer
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;



  // Add peer
  esp_now_add_peer(&peerInfo);
  // if (esp_now_add_peer(&peerInfo) != ESP_OK) {
  //   Serial.println("Failed to add peer");
  //   return;
  // }
  myServo.write(0);

  while (pointer <= 5) {
    // Initialize position
    myServo.write(0);
    sensor.read();
    depth = sensor.depth() + 0.09;
    sendTime = String(rtc.getTime(/*%A, %B %d %Y */ "%H:%M:%S"));
    snprintf(msgPacket[pointer], sizeof(msgPacket[pointer]), "%s %.2fm", sendTime, depth);
    esp_err_t result = esp_now_send(broadcastAddress, (uint8_t*)&msgPacket[pointer], sizeof(msgPacket[pointer]));
    Serial.println(msgPacket[pointer]);
    if (sendSuccess == true) {
      pointer++;
    }
    delay(1000);
  }
  delay(1000);
  float_count_time = millis();
}
void loop() {

  sensor.read();
  depth = sensor.depth() + 0.08;

  if (profile_time < 2) {
    switch (state) {
      case 0:
        if (depth < goal_depth - 0.3 || depth > goal_depth + 0.3) {
          now = millis();
          dt = (now - lastTime) / 1000.0;
          lastTime = now;

          // 误差计算（实际深度 - 目标深度）
          error = depth - goal_depth;

          // PID 计算
          proportional = Kp * error;
          integral += Ki * error * dt;
          derivative = Kd * (error - lastError) / dt;
          lastError = error;

          // 积分限幅
          integral = constrain(integral, -200, 200);

          // 总控制量
          output = proportional + integral + derivative;

          // 映射到舵机角度（正输出 → 上浮）
          angle = constrain(output, -100, 100);
          angle = map(angle, 100, -100, 0, 100);  // 确保方向正确
          angle = constrain(angle, 0, 100);
        } else {
          angle = 50;
        }

        if (depth >= goal_depth - 0.5 && depth <= goal_depth + 0.5) {
          count_time += millis() - old_time;
        }
        if (count_time > 50000) {
          state = 1;
          count_time = 0;
        }

        break;
      case 1:
        angle = 0;  //push the piston
        myServo.write(0);
        if (depth >= 0.5) {
          angle = 0;
        } else {
          strncpy(msgPacket[pointer + 1], "done", sizeof(msgPacket[pointer + 1]));
          state = 2;
          float_count_time = 0;
        };
        break;

      case 2:
        while (send_pointer < pointer && strcmp(msgPacket[send_pointer], "done") != 0) {
          Serial.print("msgPacket: ");
          Serial.println(msgPacket[send_pointer]);
          // Send message via ESP-NOW
          esp_err_t result = esp_now_send(broadcastAddress, (uint8_t*)&msgPacket[send_pointer], sizeof(msgPacket[send_pointer]));
          if (sendSuccess) {
            send_pointer++;
            sendSuccess = !sendSuccess;
          }
          delay(100);
        };
        integral = 0;
        lastError = 0;
        myServo.write(9);
        delay(500);
        lastTime = millis();
        state = 0;
        profile_time += 1;
        send_pointer += 1;
        float_count_time = 0;

        break;

      case 3:
        while (depth >= 0.5) {
          myServo.write(0);
        }
        state = 2;
        strncpy(msgPacket[pointer + 1], "done", sizeof(msgPacket[pointer + 1]));
        break;
    }
    myServo.write(angle);

    unsigned long currentMillis = millis();
    if (state != 2 && state != 4 && currentMillis - previousMillis >= 5000) {
      previousMillis = currentMillis;  // Remember the time
      sendTime = String(rtc.getTime("%H:%M:%S"));
      // sprintf(sendMsg, "%s  %.2f", sendTime, depth);
      snprintf(msgPacket[pointer], sizeof(msgPacket[pointer]), "%s %.2fm %dms", sendTime, depth, count_time);
      pointer += 1;
    };

    float_count_time += millis() - float_count_time;
    float_count_time = millis();

    if (float_count_time >= 360000) {
      myServo.write(0);
      state = 3;
    }
    old_time = millis();
    // Serial.print("SendTime:");
    // Serial.println(sendTime);
    Serial.print("depth:");
    Serial.println(depth);
    // Serial.print("count_time:");
    // Serial.println(count_time);
    Serial.print("angle:");
    Serial.println(angle);
    // Serial.print("float_count_time: ");
    // Serial.println(float_count_time);
    // Display Results on Serial Monitor
    // Serial.print("error: ");
    // Serial.print(error);
    // Serial.print(" ");
    // Serial.print("proportional:");
    // Serial.print(proportional);
    // Serial.print(" ");
    // Serial.print("integral:");
    // Serial.print(integral);
    // Serial.print(" ");
    // Serial.print("derivative:");
    // Serial.println(derivative);
  } else {
    myServo.write(9);
  }
}
