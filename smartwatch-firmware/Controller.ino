// extern int currentState;
// extern int selectedState;

void updateState() {
  int buttonState = readButton();

  if(buttonState == 2 and currentState != Menu) {
    currentState = Menu;
    return;
  }

  switch (currentState) {
    case Sleep:
      // if movement reported, currentState = TimeWeather
      // else if idle for 10 min, currentState = Idle
      break;
    case Idle:
      if (buttonState == 1){currentState == TimeWeather;}
      break;
    case Menu:
      if (buttonState == 1) {
        selectedState = (selectedState + 1) % 3; // cycle through states
      } else if (buttonState == 2) {
        switch (selectedState) {
          case 0: currentState = Ped; break; // Steps
          case 1: currentState = HR; break; // Heart Rate
          case 2: currentState = TimeWeather; break; // Time and Weather
        }
      }
      break;
    case Ped:
    case HR:
    case TimeWeather:
      break;
  }
}