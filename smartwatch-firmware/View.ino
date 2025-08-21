#include "U8x8lib.h"
#include "Wire.h"

U8X8_SSD1306_128X32_UNIVISION_HW_I2C oled(U8X8_PIN_NONE);

const int MAX_REFRESH = 1000;
unsigned long lastClear = 0;

void setupDisplay() {
  oled.begin();
  oled.setPowerSave(0);
  oled.setFont(u8x8_font_amstrad_cpc_extended_r);
  oled.setCursor(0, 0);
}

void writeDisplay(String message, int row, bool erase) {
  unsigned long now = millis();
  if(erase && (millis() - lastClear >= MAX_REFRESH)) { // only clears screen at most every MAX_REFRESH milliseconds
    oled.clearDisplay();
    lastClear = now;
  }
  oled.setCursor(0, row);
  oled.print(message);
}

void writeDisplayCSV(String message, int commaCount) {
  int startIndex = 0;
  for(int i = 0; i <= commaCount; i++) {
    int index = message.indexOf(',', startIndex);
    String subMessage = message.substring(startIndex, index);
    startIndex = index + 1;
    writeDisplay(subMessage.c_str(), i, false);
  }
}

void displayOff() {
  writeDisplay("Display Off", 0, true);
  // oled.clearDisplay();
  // oled.setCursor(0, 0);
  // oled.print("Display Off");
}

void displayMenu(int selectedState) {
  // writeDisplay("Menu:", 0, true);
  if (prevSelectedState != selectedState or currentState != previousState){
    oled.clearDisplay();
    oled.setCursor(0, 0);
    oled.print("Menu:");
    
    switch(selectedState) {
      case 0:
        // writeDisplay("> Steps", 1, true);
        // writeDisplay("  Heart Rate", 2, true);
        // writeDisplay("  Time & Weather", 3, true);
        oled.setCursor(0, 1);
        oled.print("> Steps");
        oled.setCursor(0, 2);
        oled.print("  Heart Rate");
        oled.setCursor(0, 3);
        oled.print("  Time & Weather");
        break;
      case 1:
        // writeDisplay("  Steps", 1, true);
        // writeDisplay("> Heart Rate", 2, true);
        // writeDisplay("  Time & Weather", 3, true);
        oled.setCursor(0, 1);
        oled.print("  Steps");
        oled.setCursor(0, 2);
        oled.print("> Heart Rate");
        oled.setCursor(0, 3);
        oled.print("  Time & Weather");
        break;
      case 2:
        // writeDisplay("  Steps", 1, true);
        // writeDisplay("  Heart Rate", 2, true);
        // writeDisplay("> Time & Weather", 3, true);
        oled.setCursor(0, 1);
        oled.print("  Steps");
        oled.setCursor(0, 2);
        oled.print("  Heart Rate");
        oled.setCursor(0, 3);
        oled.print("> Time & Weather");
        break;
      default:
        break;
    }
  }
  prevSelectedState = selectedState;
}

void displayAlert() {
  // writeDisplay("Idle Alert", 0, true);
  // writeDisplay("Press button to", 1, true);
  // writeDisplay("wake up.", 2, true);
  oled.clearDisplay();
  oled.setCursor(0, 0);
  oled.print("Idle Alert");
  oled.setCursor(0, 1);
  oled.print("Press button to");
  oled.setCursor(0, 2);
  oled.print("wake up.");
}

void displaySteps(String steps) {
  // only update display if relevant values or state has changed
  if (steps != prevSteps or currentState != previousState) { 
    oled.clearDisplay();
    oled.setCursor(0, 0);
    oled.print("Steps: ");
    oled.print(steps);
  }
}

void displayHR(String heartRate) {
  // writeDisplay("Heart Rate: ", 0, true);
  // writeDisplay(heartRate + " BPM", 1, true);
  if (heartRate != prevHeartRate or currentState != previousState){
    oled.clearDisplay();
    oled.setCursor(0, 0);
    oled.print("Heart Rate: ");
    oled.setCursor(0, 1);
    oled.print(heartRate);
    oled.print(" BPM");
  }
}

void displayTime(String time, String date, String weather) {
  // writeDisplay("Time: " + time, 1, true);
  // writeDisplay("Date: " + date, 2, true);
  // writeDisplay("Weather: " + weather, 3, true);
  if(time!=prevTime or date!=prevDate or weather!=prevWeather or currentState != previousState){
    oled.clearDisplay();
    oled.setCursor(0, 0);
    oled.print("Time: ");
    oled.print(time);
    oled.setCursor(0, 1);
    oled.print("Date: ");
    oled.print(date);
    oled.setCursor(0, 2);
    oled.print("Weather: ");
    oled.print(weather);
  }
}