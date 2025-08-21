unsigned long sampleTime = 0, currentTime = 0, inactiveStart = 0; // Time of last sample (in Sampling tab)
int ax = 0, ay = 0, az = 0; // for accelerometer
int button = 0, button_data = 0; // button states: 0 (off), 1 (press), 2 (hold)
int ppg = 0; // reading from photosensor
bool start = false;

enum iStates {Sleep, Idle, Menu, Ped, HR, TimeWeather};
iStates currentState = Menu;
iStates previousState = Ped; // to keep track of previous state

int selectedState = 0; // for Menu state, cycling through options
int prevSelectedState = 0;


void setup() {
  setupButton();
  setupPhotoSensor();
  setupAccelSensor();
  setupCommunication();
  setupDisplay();
}
void loop() {
  currentTime = millis();
  
  String message = receiveMessage();
  parseMessage(message);
  updateState();

  // if isIdle is true and previousState is not Idle or Sleep, set currentState to Idle
  if(message.startsWith("a,") or message.startsWith("i,")){
    // Track inactivity based on messages starting with 'i'
    if (isIdle(message)) {
      if (inactiveStart == 0) {
        inactiveStart = currentTime; // Start inactivity timer
      }
      // Transition to Sleep after 10 seconds of inactivity
      if (currentState != Sleep && (currentTime - inactiveStart > 10000)) {
        currentState = Sleep;
      }
      // Transition to Idle after 20 seconds of inactivity (10 more seconds after Sleep)
      if (currentState == Sleep && (currentTime - inactiveStart > 20000)) {
        currentState = Idle;
      }
    } else {
      // Reset inactivity timer if activity detected
      inactiveStart = 0;
      if (currentState == Sleep || currentState == Idle) {
        currentState = Menu; // or previousState, depending on desired behavior
      }
    }
    // if (isIdle(message) && previousState != Idle && currentState != Sleep && previousState != Sleep) {
    //   inactiveStart = currentTime; // reset inactive timer everytime data_processing reports idle and not already Idle or Sleep state
    // }
  }

  // // Sleep state after inactive for 1 minute
  // if (inactiveStart != 0 and currentState != Sleep and currentTime - inactiveStart > 10000){ 
  //   currentState = Sleep;
  // }

  // // Idle state after inactive for 2 minutes
  // if (currentState == Sleep && (currentTime - inactiveStart >= 20000)) { // 2 minutes in milliseconds
  //   currentState = Idle;
  // }

  if (sampleSensors()) { // constantly send data from sensors to pc while active
    // "t ppg ax ay az button" will be the format it sends out
    String response = String(currentTime) + " " + String(ppg) + " " + String(ax) + " " + String(ay) + " " + String(az) + " " + String(button_data);
    sendMessage(response);
  }
  

  switch(currentState){
    case Sleep:
      displayOff();
      break;
    case Idle:
      displayAlert();
      break;
    case Menu:
      displayMenu(selectedState);
      break;
    case Ped:
      displaySteps(getSteps());
      break;
    case HR:
      displayHR(getHR());
      break;
    case TimeWeather:
      displayTime(getTime(), getDate(), getWeather());
      break;

  }

  previousState = currentState; // update previous state for next loop
  updatePreviousValues(); // update previous values for display
}