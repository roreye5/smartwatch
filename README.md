# Smartwatch Project

A smartwatch prototype developed as part of my electrical engineering projects.  
This project demonstrates hardware and software integration, including Arduino firmware, data processing with Python, and basic machine learning.

---

## Project Overview

This smartwatch prototype includes the following features:

- **Pedometer and idle detection** using a 3-axis accelerometer  
- **Heart rate monitoring** via hardware sensor  
- **Time, date, and weather display** using Wi-Fi API requests  
- **Data processing and analysis** using Python tools, including a Gaussian Mixture Model (GMM)  

---

## System Architecture

```mermaid
flowchart LR
    subgraph Device["Smartwatch Device"]
        Sensors[<u><b>Sensors</b></u><br/>Accelerometer<br/>PPG Sensor]
        MCU[<u><b>MCU Firmware</b></u><br/>- Sensor acquisition<br/>- BLE / Serial communication<br/>- OLED updates]
        OLED["<u><b>OLED Display</b></u><br/>- Time/Date<br/>- Step count<br/>- Heart rate<br/>- Weather"]
    end

    subgraph Laptop["Laptop / Python Side"]
        Python["<u><b>Python Processing Script</b></u><br/>- Parse raw data<br/>- Filter signals<br/>- Step count logic<br/>- Heart rate detection"]
        Weather["<u><b>Weather API</b></u><br/>- Fetch weather data<br/>- Provide time info"]
    end

    Sensors -->|Raw readings| MCU
    MCU -->|BLE / Serial<br/>raw sensor data| Python
    Weather -->|weather/time data| Python
    Python -->|processed results| MCU
    MCU -->|step count, heart rate, weather| OLED
```

---


## Getting Started

### Arduino Firmware
1. Open the `.ino` files in the Arduino IDE.  
2. Select the correct board and port.  
3. Upload the code to the smartwatch hardware.  

### Python Tools
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run data processing script:
   ```bash
   python python-tools/process_data.py
   ```

---

## Notes

* Raw training data is not included to reduce repo size.
* The repository includes the pretrained GMM model (gmm_model.pkl) instead.