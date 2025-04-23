// Include Libraries
#include <esp_now.h>
#include <WiFi.h>
#define company_number "RN11" // 要改
char sendMsg[32];


// Callback function executed when data is received
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&sendMsg, incomingData, sizeof(sendMsg));
  Serial.print(company_number);
  Serial.print(" ");
  Serial.println(sendMsg);
}

void setup() {
  // Set up Serial Monitor
  Serial.begin(115200);
  
  // Set ESP32 as a Wi-Fi Station
  WiFi.mode(WIFI_STA);

  // Initilize ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  
  // Register callback function
  esp_now_register_recv_cb(OnDataRecv);
}
 
void loop() 
{
}