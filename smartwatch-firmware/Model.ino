String theHeartRate = ""; // for heart rate display
static String theSteps = ""; // for steps display
String theTime = ""; // for time display
String theDate = ""; // for date display
String theWeather = ""; // for weather display

static String prevHeartRate = "";
static String prevSteps = "";
static String prevTime = "";
static String prevDate = "";
static String prevWeather = "";


// This function will parse the message received from the PC
// and update the display information accordingly.
void parseMessage(String message) {
  // check that message is in expected format before updating values
  if(!(message.startsWith("a,") or message.startsWith("i,"))){
    return;
  }
  
  int index1, index2, index3, index4, index5;
  String key1, key2, key3, key4, key5;
  
  key1 = ",hr: ";
  key2 = ",steps: ";
  key3 = ",time: ";
  key4 = ",date: ";
  key5 = ",weather: ";
  index1 = message.indexOf(key1);
  index2 = message.indexOf(key2);
  index3 = message.indexOf(key3);
  index4 = message.indexOf(key4);
  index5 = message.indexOf(key5);

  theHeartRate = message.substring(index1 + key1.length(), index2); // all characters beween "...,hr:" and ",steps..."
  theSteps = message.substring(index2 + key2.length(), index3); // all characters beween "...,steps:" and ",time:..."
  theTime = message.substring(index3 + key3.length(), index4); // all characters beween "...,time:" and ",date..."
  theDate = message.substring(index4 + key4.length(), index5); // all characters beween "...,date:" and ",weather..."
  theWeather = message.substring(index5 + key5.length()); // goes to end of str
}

bool isIdle(String message) {
  return message[0] == 'i'; // Check if the first character indicates idle state
}


String getHR(){
  return theHeartRate;
}

String getSteps(){
  return theSteps;
}

String getTime(){
  return theTime;
}

String getDate(){
  return theDate;
}

String getWeather(){
  return theWeather;
}

// function to update previous values for display
void updatePreviousValues() {
  prevHeartRate = theHeartRate;
  prevSteps = theSteps;
  prevTime = theTime;
  prevDate = theDate;
  prevWeather = theWeather;
}



