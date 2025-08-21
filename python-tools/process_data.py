from smartwatchlib.Communication import Communication
from smartwatchlib.CircularList import CircularList
from smartwatchlib.HRMonitor import HRMonitor
from smartwatchlib.Pedometer import Pedometer
from smartwatchlib.IdleDetector import IdleDetector
from matplotlib import pyplot as plt
from time import time
import numpy as np
from pyowm import OWM
from datetime import datetime
import os


if __name__ == "__main__":
    # parameters
    fs = 50  # sampling rate
    hr_num_samples = 500
    num_samples = 250  # 5 seconds @ 50 hz
    process_time = 2  # compute the HR every 1 seconds
    hr_prediction = 0

    # object declarations
    owm = OWM('49ba0e02d81f7b972a6ee0da933b3d4d').weather_manager()
    weather = owm.weather_at_place('San Diego,CA,US').weather
    hr = HRMonitor(hr_num_samples, fs)
    gmm_path = "gmm_model.pkl"
    if os.path.exists(gmm_path):
        hr.load_gmm(gmm_path)
        print("Pre-trained GMM model loaded successfully.")
    else:
        hr.train()
        hr.save_gmm(gmm_path)
        print("GMM model trained and saved successfully.")       
    # hr.train()
    ped = Pedometer(num_samples, fs, [])
    idle = IdleDetector(num_samples, fs, [])

    # bt connection
    # comms = Communication("/dev/cu.Roberto_ESP32", 115200)
    comms = Communication("/dev/cu.usbserial-0230F3FC", 115200)
    comms.clear()  # just in case any junk is in the pipes

    try:
        send_time = time()
        previous_time = time()


        # initialize circ lists for plotting mcu readings
        times = CircularList([], num_samples)
        samples = CircularList([], num_samples)
        ax = CircularList([], num_samples)
        ay = CircularList([], num_samples)
        az = CircularList([], num_samples)

        print('Starting data collection!')

        while (True):
            message = comms.receive_message()
            response = ''
            if (message != None):
                try:
                    # mcu sends 't ppg ax ay az'
                    (t, s, x, y, z, b) = message.split(' ')
                    t_sec = int(t) / 1000  # milliseconds -> seconds
                    # print(t_sec, s)

                    hr.add(float(t_sec), int(s))
                    ped.add(int(x), int(y), int(z))
                    idle.add(int(x), int(y), int(z))
    

                except TypeError as e:  # if corrupted data, skip the sample
                    print(e)
                    continue

                # if enough time has elapsed, process the data and plot it
                current_time = time()
                if (current_time - previous_time >= process_time):
                    watch_time = str(datetime.now().hour) + ':' + str(datetime.now().minute) + ':' + str(datetime.now().second)
                    watch_date = str(datetime.now().month) + '/' + str(datetime.now().day) + '/' + str(datetime.now().year)
                    previous_time = current_time

                    try:
                        data = hr.online_process() 
                    except:
                        continue

                    hr_prediction, peaks = hr.predict()

                    # plt.cla()
                    # plt.plot(data)
                    # plt.plot(peaks)
                    # plt.title("Heartbeat Count: %d" % sum(peaks))
                    # plt.show(block=False)
                    # plt.pause(0.001)

                    steps, _, ped_data = ped.process()
                    activity = idle.run()

                    plt.cla()
                    plt.plot(ped_data)
                    plt.show(block=False)
                    plt.pause(0.001)


                    temperature = str(round(weather.temperature('fahrenheit')['temp'])) + ' F'

                    # create response to allow mcu to print values and decide states
                    if activity:
                        response += 'a'
                    else:
                        response += 'i'
                    response += ',hr: '
                    if not 30 < hr_prediction < 300:  # ignore if hr too high or low
                        response += '0'
                    else:
                        response += f'{hr_prediction:.1f}'  # 1 decimal for hr prediction
                    response += ',steps: ' + str(steps)
                    response += ',time: ' + str(watch_time) + ',date: ' + str(watch_date) + ',weather: ' + str(temperature)

                    print(response)
                    comms.send_message(response)
    except(Exception, KeyboardInterrupt) as e:
        print(e)  # Exiting the program due to exception
        print(message)
    finally:
        comms.send_message("sleep")
        print("Closing connection.")
        comms.close()

