#if defined(ARDUINO_ARCH_ESP8266)
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#define GET_CHIPID()  (ESP.getChipId())
#elif defined(ARDUINO_ARCH_ESP32)
#include <WiFi.h>
#include <SPIFFS.h>
#include <HTTPClient.h>
#define GET_CHIPID()  ((uint16_t)(ESP.getEfuseMac()>>32))
#endif
#include <PubSubClient.h>
#include <AutoConnect.h>

#if defined(ARDUINO_ARCH_ESP8266)
typedef ESP8266WebServer  WiFiWebServer;
#elif defined(ARDUINO_ARCH_ESP32)
typedef WebServer WiFiWebServer;
#endif


ESP8266WebServer server;
AutoConnect portal(server);
AutoConnectConfig config;
AutoConnectAux Input;
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

const static char InputPage[] PROGMEM = R"r(
{
  "title": "Database",
  "uri": "/input", 
  "menu": true, 
  "element": [
    { 
      "name": "username", 
      "type": "ACInput", 
      "label": "User" 
    },
    { 
      "name": "password", 
      "type": "ACInput", 
      "label": "Pass" 
    },
    { 
      "name": "host_ip", 
      "type": "ACInput", 
      "label": "Host" 
    },
    { 
      "name": "database", 
      "type": "ACInput", 
      "label": "Name" },
    {
      "name": "save",
      "type": "ACSubmit",
      "value": "SAVE",
      "uri": "/"
    }
  ]
}
)r";


bool mqttConnect() {
  String value1 = Input["host_ip"].value;

  static const char alphanum[] = "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz";  // For random generation of client ID.
  char    clientId[9];
  
  uint8_t retry = 3;
  while (!mqttClient.connected()) {
    if (value1.length() <= 0)
      break;

    mqttClient.setServer(value1.c_str(), 1883);
    Serial.println(String("Attempting MQTT broker:") + value1);

    for (uint8_t i = 0; i < 8; i++) {
      clientId[i] = alphanum[random(62)];
    }
    clientId[8] = '\0';

    if (mqttClient.connect(clientId)) {
      Serial.println("Established:" + String(clientId));
      return true;
    }
    else {
      Serial.println("Connection failed:" + String(mqttClient.state()));
      if (!--retry)
        break;
      delay(3000);
    }
  }
  return false;
}


// An on-page handler for '/' access
void onRoot() {
  String  content =
  "<html>"
  "<head><meta name='viewport' content='width=device-width, initial-scale=1'></head>"
  "<body><div>Username: {{value1}} | Password: {{value2}} | Host IP: {{value3}} | Database: {{value4}}</div></body>"
  "</html>";

  Input.fetchElement();    // Preliminary acquisition

  // For this steps to work, need to call fetchElement function beforehand.
  String value1 = Input["username"].value;
  String value2 = Input["password"].value;
  String value3 = Input["host_ip"].value;
  String value4 = Input["database"].value;
  content.replace("{{value1}}", value1);
  content.replace("{{value2}}", value2);
  content.replace("{{value3}}", value3);
  content.replace("{{value4}}", value4);
  server.send(200, "text/html", content);
}

void mqttPublish(String msg) {
  String path = String("channels");
  Serial.print('Sending to...');
  Serial.println(path);
  mqttClient.publish(path.c_str(), msg.c_str());
}

int Motion(){
  int motionsense_int;
  String motionsense_str;
  char motion[2];
  
  motionsense_int = digitalRead(13);                  // Read motion sensor value as int
  motionsense_str = String(motionsense_int);          // Convert int to String
  motionsense_str.toCharArray(motion, 2);             // Convert String to Char

  Serial.print(motion);
    
// return motion                                      // Return motion as char.
                                                      // I get an error here... invalid conversion from char to int...
}

int Light(){
  int pVolt = analogRead(A0);                         // Read Light sensor value as int
  String volt_str = String(pVolt);                    // Convert int to String
  int volt_len = volt_str.length() + 1;               // Get length of string plus one
  char volt[volt_len];                                // Create char buffer
  volt_str.toCharArray(volt, volt_len);               // Covert String to char
  Serial.print(volt);
  
  // return volt                                       // Return volt as char
                                                       // I get an error here... invalid conversion from char to int...
  }
  
void reconnect() {
  // Loop until we're reconnected
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      mqttClient.publish("channels", "hello world");
      // ... and resubscribe
      mqttClient.subscribe("commands");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  // Switch on the LED if an 1 was received as first character
  if ((char)payload[0] == '1') {
    digitalWrite(BUILTIN_LED, LOW);   // Turn the LED on (Note that LOW is the voltage level
    // but actually the LED is on; this is because
    // it is active low on the ESP-01)
  } else {
    digitalWrite(BUILTIN_LED, HIGH);  // Turn the LED off by making the voltage HIGH
  }

}

void maintain_connection(){
  // Maintain connection to Internet and Mosquitto Broker
  if (WiFi.status() == WL_CONNECTED) {                                                                    // If Wifi is connected
    if (!mqttClient.connected()) {                                                                          // If mosquitto broker is not connected 
      mqttConnect();                                                                                        // Connect to mosquitto broker
      reconnect();                                                                                          // Reconnect and subscribe
    }
    mqttPublish("Im alive!");                                                                               // Publish alive status
    mqttClient.loop();

  }
}
void setup() {
  // Setup Function. 
  Serial.begin(115200);                                                                                     // Start Serial at baud 115200
  config.ota = AC_OTA_BUILTIN;                                                                              // Enable OTA browser updates
  portal.config(config);
  Input.load(InputPage);                                                                                    // Load custom page to AutoConnect
  portal.join(Input);                                                                                       // Bind custom page to Menu
  server.on("/", onRoot);                                                                                   // Register the on-page handler                                                  
  portal.begin();                                                                                           // Start AutoConnect
  String value1 = Input["username"].value;                                                                  // Get Username for testing purposes
  mqttClient.setCallback(callback);                                                                         // Set up mosquitto callback
  Serial.println("SETUP");                                                                                 
  Serial.println(value1);
  
}


void loop() {
  maintain_connection();
  portal.handleClient();

  String value1 = Input["username"].value;
  String value2 = Input["password"].value;
  String value3 = Input["host_ip"].value;
  String value4 = Input["database"].value;
  Serial.println(value1);
  Serial.println(value2);
  Serial.println(value3);
  Serial.println(value4);
  mqttPublish(value1);
  mqttPublish(value2);
  mqttPublish(value3);
  mqttPublish(value4);

  delay(1000);

}
