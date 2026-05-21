
from smartwatchlib.Communication import Communication
from smartwatchlib.CircularList import CircularList
from matplotlib import pyplot as plt
import smartwatchlib.DSP as filt
from time import time
import numpy as np

class IdleDetector:
    __l1 = None        # CircularList containing L1-norm
    __filtered = None  # CircularList containing filtered signal
    __thresh_low = 1.45   
    __thresh_high = 14 
    __new_samples = 0  # new samples to process

    # constructor:
    #def __init__(self, port, baudrate, num_samples=250, refresh_time=0.1, sample_size=100, top_threshold = 1972, btm_threshold = 1964.5, last_state =0, data = None):
    def __init__(self, num_samples=250, fs =50, data = None, refresh_time=0.1, sample_size=100, top_threshold = 1972, btm_threshold = 1964.5, last_state =0): 
        self.num_samples = num_samples
        self.refresh_time = refresh_time
        self.sample_size = sample_size
        self.times = CircularList([], num_samples)
        self.ax = CircularList([], num_samples)
        self.ay = CircularList([], num_samples)
        self.az = CircularList([], num_samples)
        self.__l1 = CircularList(data, num_samples)
        self.__filtered = CircularList([], num_samples)
        self.myList = CircularList([], num_samples)
        self.top_threshold = top_threshold
        self.btm_threshold = btm_threshold
        self.active = 0    
        self.current_state = 0     #0=idle & 1=active
        self.last_state = last_state  
        #self.comms = Communication(port, baudrate)
        self.current_time = time()
        #self.comms.clear()
        #self.comms.send_message("wearable")


    def add(self, ax, ay, az):
        l1 = filt.l1_norm(ax, ay, az)
        if isinstance(ax, int):
            num_add = 1
        else:
            num_add = len(ax)
            l1 = l1.tolist()

        self.__l1.add(l1)
        self.__new_samples += num_add

    def run(self):
        # Grab only the new samples into a NumPy array
        x = np.array(self.__l1[ -self.__new_samples: ])

        # Filter the signal (detrend, LP, MA, etc…)
        ma = filt.moving_average(x, 15)         
        dt = filt.detrend(ma)                  
        bl, al = filt.create_filter(3, 2, "lowpass", 50)   # Low-pass Filter Design
        lp = filt.filter(bl, al, dt)                       # Low-pass Filter Signal
        grad = filt.gradient(lp)
        ma_grad = filt.moving_average(grad, 15)

        x = ma_grad
      

        # Store the filtered data
        self.__filtered.add(x.tolist())

        # Count the number of peaks in the filtered data
        count, peaks = filt.count_peaks(x,self.__thresh_low,self.__thresh_high)

        # reset new sample count
        self.__new_samples = 0

        # return true(active) if steps counted & false(idle) if no steps
        if count > 0:
           return True
        else:
           return False
          


    # stream data method
    def __stream_and_plot(self):
        self.comms.clear()                   # just in case any junk is in the pipes
        self.comms.send_message("wearable")  # begin sending data

        try:
            previous_time = 0
            while(True):
                message = self.comms.receive_message()
                if(message != None):
                    try:
                        (m1, m2, m3, m4) = message.split(',')
                    except ValueError:        # if corrupted data, skip the sample
                        continue


                    # add the new values to the circular lists
                    self.times.add(int(m1))
                    self.ax.add(int(m2))
                    self.ay.add(int(m3))
                    self.az.add(int(m4))

                    # if enough time has elapsed, clear the axis, and plot az
                    self.current_time = time()
                    if (self.current_time - previous_time > self.refresh_time):
                        previous_time = self.current_time
                        plt.clf()
                        
                        # Plot Raw Data
                        plt.subplot(311)
                        plt.plot(self.ax)
                        plt.ylabel('ax')

                        plt.subplot(312)
                        plt.plot(self.ay)
                        plt.ylabel('ay')

                        plt.subplot(313)
                        plt.plot(self.az)
                        plt.ylabel('az')

                        plt.show(block=False)
                        plt.pause(0.001)
        except(Exception, KeyboardInterrupt) as e:
            print(e)                     # Exiting the program due to exception
        finally:
            self.comms.send_message("sleep")  # stop sending data
            self.comms.close()



    # detect activity method
    def __detect_active(self):
        # compute transformed (average of x/y/z-axis)
        if len(self.ax) >= self.sample_size:
          ax_sample = self.ax[-self.sample_size:]
          average_Xvalue = np.mean(ax_sample)
          ay_sample = self.ay[-self.sample_size:]
          average_Yvalue = np.mean(ay_sample)
          az_sample = self.az[-self.sample_size:]
          average_Zvalue = np.mean(az_sample)

          average_value = (average_Xvalue + average_Yvalue +average_Zvalue)/3
          #print(average_value)
          self.myList.add(average_value)

        if len(self.myList) >= 200: 
          list_sample = np.array(self.myList[-30:])
          if np.any((list_sample > self.top_threshold)) or np.any((list_sample < self.btm_threshold)):
            self.current_state = 1
            active_start = 0
            if ((self.last_state == 0) & (self.current_state ==1)):
              active_start = time()
              self.active = 1
            if (self.current_time - active_start) >= 1:
              self.comms.send_message("active")
              #print("active")
        
          else:
            self.current_state = 0
            idle_start = 0
            if ((self.last_state == 1) & (self.current_state == 0)):
              #start tracking time
              idle_start = time()
              self.active = 0
            if (self.current_time - idle_start) >= 5:
              self.comms.send_message("idle")
              #print("idle")
        self.last_state = self.current_state




    def stream_plot_detect(self):
       self.comms.clear()                   # just in case any junk is in the pipes
       self.comms.send_message("wearable")  # begin sending data

       try:
          previous_time = 0
          while(True):
             current_time = time()
             message = self.comms.receive_message()
             if(message != None):
                try:
                   (m1, m2, m3, m4) = message.split(',')
                except ValueError:
                   continue

                # add the new values to the circular lists
                self.times.add(int(m1))
                self.ax.add(int(m2))
                self.ay.add(int(m3))
                self.az.add(int(m4))

                self.__detect_active()

                # if enough time has elapsed, clear the axis, and plot az
                current_time = time()
                if (current_time - previous_time > self.refresh_time):
                    previous_time = current_time
                    plt.clf()

                    plt.plot(self.myList)
                    plt.ylabel('transformed')

                    plt.show(block=False)
                    plt.pause(0.001)
       except(Exception, KeyboardInterrupt) as e:
            print(e)                     # Exiting the program due to exception
       finally:
            self.comms.send_message("sleep")  # stop sending data
            self.comms.close()        



                
       
