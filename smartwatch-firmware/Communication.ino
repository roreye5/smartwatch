/*
 * 0 == Serial, 1 == Bluetooth
 */

#define USE_BT 0


#if USE_BT
  #include "BluetoothSerial.h"
  BluetoothSerial BTSerial;     
  #define Ser BTSerial          
#else
  #define Ser Serial            
#endif

/*
 * Initialize the communication protocol (either HW Serial or BT)
 */
void setupCommunication() {
  #if USE_BT
    Ser.begin("Roberto_ESP32"); 
  #else
    Ser.begin(115200);
  #endif
}

/*
 * Receive a message one character at a time, stopping at a newline ('\n')
 */
String receiveMessage() {
  String message = "";
  if (Ser.available() > 0) {
    while (true) {
      char c = Ser.read();
      if (c != char(-1)) {
        if (c == '\n')
          break;
        message += c;
      }
    }
  }
  return message;
}

/*
 * Send a message over the communication protocol
 */
void sendMessage(String message) {
  Ser.println(message);
}
