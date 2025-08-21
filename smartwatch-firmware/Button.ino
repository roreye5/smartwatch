const int buttonPin = 21;
unsigned long last_button_time = 0;
int prev_b;
bool button_pressed = false, holding_button = false, timing_hold;

void setupButton() {
  pinMode(buttonPin, INPUT);
}

int readButton() { // read button input, return 1 means button was released, return 2 means 3 second hold
  if (digitalRead(buttonPin) == HIGH && !holding_button) { // read from button
    holding_button = true;
    button_pressed = true;
    last_button_time = millis();
    // Serial.println("button read");
  }
  else if (digitalRead(buttonPin) == LOW) {
    // Serial.println("button release");
    holding_button = false;
  }
  if (holding_button && button_pressed && currentTime - last_button_time >= 2000) { // 2 second hold time
    // Serial.println("held");
    button_data = 2;
    button_pressed = false; 
    return 2;
  }
  else if (button_pressed && !holding_button) {
    // Serial.println("button press");
    button_pressed = false;
    button_data = 1;
    return 1;
  }
  else {
    button_data = 0;
    return 0;
  }
}

// int readButton(){
//   int b_state = digitalRead(buttonPin);
//   if(prev_b == LOW and b_state == HIGH){
//     button_data = 1;
//     return 1;
//   }

//   int prev_b = b_state;
// }

