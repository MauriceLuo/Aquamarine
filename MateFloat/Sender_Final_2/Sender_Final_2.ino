// Include Libraries
// 需更改company number，depth buffer, boundary, case1 以及depth 位置
#include <esp_now.h>
#include <esp_wifi.h>
#include <WiFi.h>
#include <time.h>
#include <ESP32Time.h>
#include <Wire.h>
#include "MS5837.h"

MS5837 sensor;
ESP32Time rtc(0);

// MAC Address of responder - edit as required
uint8_t broadcastAddress[] = { 0xF4, 0x65, 0x0B, 0xE9, 0x94, 0xE4 };
// uint8_t broadcastAddress[] = { 0x30, 0xAE, 0xA4, 0x5B, 0x40, 0xCC };  //for testing

int relay1 = 26;
int relay2 = 25;
esp_now_peer_info_t peerInfo;
#define goal_depth 0.8  //in m
float upper_boundary = goal_depth + 0.5;
float lower_boundary = goal_depth - 0.5;
float depth_buffer = 0.2;
int count_time = 0;
int oldtime = 0;
int state = 0;
// char sendMsg[16];
char msgPacket[200][32];
int pointer = 0;
int send_pointer = 0;
String sendTime;
float depth;
int profile_time = 0;
bool sendSuccess = false;

unsigned long previousMillis = 0;

void pull() {
  // Pull back
  digitalWrite(relay1, LOW);   // turn relay 1 ON
  digitalWrite(relay2, HIGH);  // turn relay 2 OFF
}
void push() {
  // Push forward
  digitalWrite(relay1, HIGH);  // turn relay 1 OFF
  digitalWrite(relay2, LOW);   // turn relay 2 ON
}
void stop() {
  // stop the actuator
  digitalWrite(relay1, HIGH);  // turn relay 1 OFF
  digitalWrite(relay2, HIGH);  // turn relay 2 OFF
}

// Callback function called when data is sent
void OnDataSent(const uint8_t* mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
  sendSuccess = (status == ESP_NOW_SEND_SUCCESS);
}

void setup() {
  // Set up Serial Monitor
  Serial.begin(115200);
  Wire.begin();
  sensor.init();
  sensor.setModel(MS5837::MS5837_02BA);
  sensor.setFluidDensity(997);  // kg/m^3 (997 for freshwater, 1029 for seawater)

  WiFi.mode(WIFI_STA);

  int8_t power = 80;  // 80 * 0.25 = 20 dBm
  esp_wifi_set_max_tx_power(power);
  esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_LR);

  // Initilize ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  // Register the send callback
  esp_now_register_send_cb(OnDataSent);

  // Register peer
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  // Add peer
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add peer");
    return;
  }
  pinMode(relay1, OUTPUT);  // set pin as output for relay 1
  pinMode(relay2, OUTPUT);  // set pin as output for relay 2

  stop();
  delay(1000);

  while (pointer <= 5) {
    sensor.read();
    depth = sensor.depth() + 0.09 - 0.41;
    sendTime = String(rtc.getTime(/*%A, %B %d %Y */ "%H:%M:%S"));
    snprintf(msgPacket[pointer], sizeof(msgPacket[pointer]), "%s %.2fm", sendTime, depth);
    esp_err_t result = esp_now_send(broadcastAddress, (uint8_t*)&msgPacket[pointer], sizeof(msgPacket[pointer]));
    Serial.println(msgPacket[pointer]);
    if (sendSuccess == true) {
      pointer++;
    }
    delay(1000);
  }
}

void loop() {
  sensor.read();
  depth = sensor.depth() - 0.41 + 0.09;
  if (profile_time < 2) {
    switch (state) {
      case 0:
        if (depth < goal_depth - depth_buffer) {
          pull();
        };
        if (depth > goal_depth + depth_buffer) {
          push();
        };
        if (depth > goal_depth - depth_buffer && depth < goal_depth + depth_buffer) {
          stop();
        };
        if (depth < upper_boundary && depth > lower_boundary) {
          count_time += millis() - oldtime;
        };
        if (count_time >= 45000) {
          state = 1;
          count_time = 0;
        };

        oldtime = millis();
        Serial.print("count time:  ");
        Serial.println(count_time);
        break;

      case 1:
        if (depth >= 0.2) {
          push();
        } else {
          strncpy(msgPacket[pointer + 1], "done", sizeof(msgPacket[pointer + 1]));
          state = 2;
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
          delay(1000);
        };
        state = 0;
        profile_time += 1;
        send_pointer += 1;
        break;
    };

    unsigned long currentMillis = millis();
    if (state != 2 && currentMillis - previousMillis >= 5000) {
      previousMillis = currentMillis;  // Remember the time
      sendTime = String(rtc.getTime(/*%A, %B %d %Y */ "%H:%M:%S"));
      // sprintf(sendMsg, "%s  %.2f", sendTime, depth);
      snprintf(msgPacket[pointer], sizeof(msgPacket[pointer]), "%s %.2fm %dms", sendTime, depth, count_time);
      pointer += 1;
    };
    Serial.print("depth:  ");
    Serial.println(depth);
    Serial.print("time:  ");
    Serial.println(sendTime);
    // snprintf(msgPacket[pointer], sizeof(msgPacket[pointer]), "%s %.2fm %dms", sendTime, depth, count_time);
    // esp_err_t result = esp_now_send(broadcastAddress, (uint8_t*)&msgPacket[pointer], sizeof(msgPacket[pointer]));
  } else {
    stop();
  }
}