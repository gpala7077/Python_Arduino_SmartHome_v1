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

// ******************************************** AutoConnect Functions ************************************************//

const static char InputPage[] PROGMEM = R"r(
{
  "title": "Database",
  "uri": "/input", 
  "menu": true, 
  "element": [
    { 
      "name": "username", 
      "type": "ACInput", 
      "value": "Enter username" 
    },
    { 
      "name": "password", 
      "type": "ACInput",
      "apply": "password", 
    },
    { 
      "name": "host_ip", 
      "type": "ACInput", 
      "value": "Database Host IP Address" 
    },
    { 
      "name": "database", 
      "type": "ACInput", 
      "value": "Database Name" },
    {
      "name": "save",
      "type": "ACSubmit",
      "value": "SAVE",
      "uri": "/"
    }
  ]
}
)r";

// An on-page handler for '/' access
void onRoot() {
    String  content =                                // Define root page
        "<html>"
            "<head>"
                "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "</head>"

            "<body>"
                "<div>"
                    "| Username: {{value1}} | <br>"
                    "| Password: {{value2}} | <br>"
                    "| Maria IP: {{value3}} | <br>"
                    "| Database: {{value4}} |"
                "</div>"
            "</body>"

        "</html>";

  Input.fetchElement();                               // Get saved variables

  String value1 = Input["username"].value;            // Test print variables
  String value2 = Input["password"].value;
  String value3 = Input["host_ip"].value;
  String value4 = Input["database"].value;
  content.replace("{{value1}}", value1);              // Format root page
  content.replace("{{value2}}", value2);
  content.replace("{{value3}}", value3);
  content.replace("{{value4}}", value4);
  server.send(200, "text/html", content);
}
// ********************************************** Sensor Functions ***************************************************//

int Motion(){
    // Read Motion sensor value and return as char
  int motionsense_int;                                // Declare integer motionsense_int
  String motionsense_str;                             // Declare string motionsense_str
  char motion[2];                                     // Declare a char array
  
  motionsense_int = digitalRead(13);                  // Read motion sensor value as int
  motionsense_str = String(motionsense_int);          // Convert int to String
  motionsense_str.toCharArray(motion, 2);             // Convert String to Char

  Serial.print(motion);                               // Print motion value to serial
    
// return motion                                      // Return motion as char.
                                                      // I get an error here... invalid conversion from char to int...
}

int Light(){
    // Read LDR sensor value and return as char

  int pVolt = analogRead(A0);                         // Read Light sensor value as int
  String volt_str = String(pVolt);                    // Convert int to String
  int volt_len = volt_str.length() + 1;               // Get length of string plus one
  char volt[volt_len];                                // Create char buffer
  volt_str.toCharArray(volt, volt_len);               // Covert String to char
  Serial.print(volt);
  
  // return volt                                       // Return volt as char
                                                       // I get an error here... invalid conversion from char to int...
  }
// ********************************************* Mosquitto Functions *************************************************//

void mqttPublish(String msg, String path) {
    // Mosquitto broadcast wrapper function
  Serial.print("Sending ");                           // Inform Serial mqtt is about to send
  Serial.println(msg);                                // Print message to serial
  Serial.print(" to...");
  Serial.println(path);                               // Print channel to serial
  mqttClient.publish(path.c_str(), msg.c_str());      // Publish payload to topic
}

bool mqttConnect() {
    // Connect to Mosquitto broker if not connect. Returns True if Connected. False if not.

  String value1 = Input["host_ip"].value;             // get Mosquitto broker IP address

  static const char alphanum[] = "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz";                     // Used to Generate random Client IP
  char    clientId[9];

  uint8_t retry = 3;
  while (!mqttClient.connected()) {                   // Do while not connected to mosquitto broker
    if (value1.length() <= 0)
      break;

    mqttClient.setServer(value1.c_str(), 1883);       // Connect to mosquitto broker using IP address
    Serial.println(String("Attempting MQTT broker:") + value1);

    for (uint8_t i = 0; i < 8; i++) {                 // Generate random client ID
      clientId[i] = alphanum[random(62)];
    }
    clientId[8] = '\0';

    if (mqttClient.connect(clientId)) {               // Print to serial successful connection
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

void reconnect() {
    // Connect/ Reconnect to Mosquitto Broker.

    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";                // Create a random client ID
    clientId += String(random(0xffff), HEX);
    if (mqttClient.connect(clientId.c_str())) {        // Attempt to connect
      Serial.println("connected");
      mqttPublish("hello world", "channels");          // Once connected, publish an announcement...
      mqttClient.subscribe("commands");                // Resubscribe
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
}

void callback(char* topic, byte* payload, unsigned int length) {
    // Mosquitto Callback function. Receive messages from subscribes topics

  Serial.print("Message arrived [");                   // Announce message received
  Serial.print(topic);                                 // Print topic
  Serial.print("] ");
  for (int i = 0; i < length; i++) {                   // Iterate through payload
    Serial.print((char)payload[i]);
  }
  Serial.println();

}

// ******************************************** Connection Functions *************************************************//
void maintain_connection(){
  // Maintain connection to Internet and Mosquitto Broker
  if (WiFi.status() == WL_CONNECTED) {                // If Wifi is connected
    if (!mqttClient.connected()) {                    // If mosquitto broker is not connected
      mqttConnect();                                  // Connect to mosquitto broker
      reconnect();                                    // Reconnect and subscribe
    }
    mqttPublish("Im alive!", "channels");             // Publish alive status
    mqttClient.loop();

  }
}
// **************************************************** Setup ********************************************************//
void setup() {
  // Setup Function. 
  Serial.begin(115200);                              // Start Serial at baud 115200
  config.ota = AC_OTA_BUILTIN;                       // Enable OTA browser updates
  portal.config(config);
  Input.load(InputPage);                             // Load custom page to AutoConnect
  portal.join(Input);                                // Bind custom page to Menu
  server.on("/", onRoot);                            // Register the on-page handler
  portal.begin();                                    // Start AutoConnect
  String value1 = Input["username"].value;           // Get Username for testing purposes
  mqttClient.setCallback(callback);                  // Set up mosquitto callback
  Serial.println("SETUP");                                                                                 
  Serial.println(value1);
  
}

// ************************************************** Main Loop ******************************************************//

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
  mqttPublish(value1,"channels");
  mqttPublish(value2,"channels");
  mqttPublish(value3,"channels");
  mqttPublish(value4,"channels");

  delay(1000);

}
