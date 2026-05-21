
from smartwatchlib.CircularList import CircularList
import smartwatchlib.DSP as filt
import numpy as np
import matplotlib as plt
import pickle
import glob

# The GMM Import
from sklearn.mixture import GaussianMixture as GMM

"""
A class to enable a simple heart rate monitor
"""
class HRMonitor:
    """
    Encapsulated class attributes (with default values)
    """
    __hr = 0           # the current heart rate
    __time = None      # CircularList containing the time vector
    __ppg = None       # CircularList containing the raw signal
    __filtered = None  # CircularList containing filtered signal
    __num_samples = 0  # The length of data maintained
    __new_samples = 0  # How many new samples exist to process
    __fs = 0           # Sampling rate in Hz
    __thresh = 0.6     
    __webcam_thresh = 0.75     
    __gmm = None

    """
    Initialize the class instance
    """
    def __init__(self, num_samples, fs, times=[], data=[]):
        self.__hr = 0
        self.__num_samples = num_samples
        self.__fs = fs
        self.__time = CircularList(data, num_samples)
        self.__ppg = CircularList(data, num_samples)
        self.__filtered = CircularList([], num_samples)

    """
    Add new samples to the data buffer
    Handles both integers and vectors
    """
    def add(self, t, x):
        if isinstance(t, np.ndarray):
            t = t.tolist()
        if isinstance(x, np.ndarray):
            x = x.tolist()

        if isinstance(x, int):
            self.__new_samples += 1
        else:
            self.__new_samples += len(x)

        self.__time.add(t)
        self.__ppg.add(x)

    """
    Compute the average heart rate 
    """
    def compute_heart_rate(self, peaks):
        t = np.array(self.__time)
        return 60 / np.mean(np.diff(t[peaks]))
    

    """
    Process the new data to update step count
    """
    def process(self):
        # Grab only the new samples into a NumPy array
        x = np.array(self.__ppg[ -self.__new_samples: ])

        # Filter the signal 
        x = filt.detrend(x, 25)
        x = filt.moving_average(x, 5)
        x = filt.gradient(x)
        x = filt.moving_average(x, 3)
        x = filt.normalize(x)


        # Store the filtered data
        self.__filtered.add(x.tolist())

        # Find the peaks in the filtered data
        _, peaks = filt.count_peaks(self.__filtered, self.__thresh, 1)

        # Update the step count and reset the new sample count
        self.__hr = self.compute_heart_rate(peaks)
        self.__new_samples = 0

        # Return the heart rate, peak locations, and filtered data
        return self.__hr, peaks, np.array(self.__filtered)
    
    """
    Process the new data 
    """
    def online_process(self):
        # Grab only the new samples into a NumPy array
        x = np.array(self.__ppg[ -self.__new_samples: ])

        # Filter the signal 
        x = filt.detrend(x, 25)
        x = filt.moving_average(x, 5)
        x = filt.gradient(x)
        x = filt.moving_average(x, 3)
        x = filt.normalize(x)



        # Store the filtered data
        self.__filtered.add(x.tolist())

        # Return filtered data
        return np.array(self.__filtered)
    


    """
    Process the new webcam data to update step count
    """
    def webcam_process(self):
        # Grab only the new samples into a NumPy array
        x = np.array(self.__ppg[ -self.__new_samples: ])

        # Filter the signal 
        x = filt.detrend(x, 25)
        x = filt.moving_average(x, 10)
        x = filt.normalize(x)


        # Store the filtered data
        self.__filtered.add(x.tolist())

        # Find the peaks in the filtered data
        _, peaks = filt.count_peaks(self.__filtered, self.__webcam_thresh, 1)

        # Update the step count and reset the new sample count
        self.__hr = self.compute_heart_rate(peaks)
        self.__new_samples = 0

        # Return the heart rate, peak locations, and filtered data
        return self.__hr, peaks, np.array(self.__filtered)
    

    """
    Clear the data buffers and step count
    """
    def reset(self):
        self.__hr = 0
        self.__time.clear()
        self.__ppg.clear()
        self.__filtered.clear()

    def predict(self):
        x = np.array(self.__filtered[ -len(self.__filtered): ])

        labels = self.__gmm.predict(x.reshape(-1,1))
        hr_est, peaks = self.__estimate_hr(labels, len(x), self.__fs)
        return hr_est, peaks

    # Retrieve a list of the names of the subjects
    def __get_subjects(self, directory):
        filepaths = glob.glob(directory + "/*")
        return [filepath.split("/")[-1] for filepath in filepaths]
    

    # Retrieve a data file, verifying its FS is reasonable
    def __get_data(self, directory, subject, trial, fs):
        search_key = "%s/%s/%s_%02d_*.csv" % (directory, subject, subject, trial)
        filepath = glob.glob(search_key)[0]
        t, ppg = np.loadtxt(filepath, delimiter=',', unpack=True)
        t = (t-t[0])/1e3
        hr = self.__get_hr(filepath, len(ppg), fs)

        fs_est = self.__estimate_fs(t)
        if(fs_est < fs-1 or fs_est > fs):
            print("Bad data! FS=%.2f. Consider discarding: %s" % (fs_est,filepath))

        return t, ppg, hr, fs_est
    

    # Estimate the heart rate from the user-reported peak count
    def __get_hr(self, filepath, num_samples, fs):
        count = int(filepath.split("_")[-1].split(".")[0])
        seconds = num_samples / fs
        return count / seconds * 60 

    # Estimate the sampling rate from the time vector
    def __estimate_fs(self, times):
        return 1 / np.mean(np.diff(times))
    
    # Estimate the heart rate given GMM output labels
    def __estimate_hr(self, labels, num_samples, fs):
        peaks = np.diff(labels, prepend=0) == 1
        count = sum(peaks)
        #print('peaks: ', peaks)     #for testing
        #print('peak count: ', count) #for testing
        seconds = num_samples / fs
        hr = count / seconds * 60 
        return hr, peaks

    # Filter the signal 
    def __process_ppg(self, x):

        x = filt.detrend(x, 25)
        x = filt.moving_average(x, 5)
        x = filt.gradient(x)
        x = filt.moving_average(x, 4)
        return filt.normalize(x)
    

    # train data
    def train(self):
        fs = 50
        directory = "./data"
        subjects = self.__get_subjects(directory)

        # Leave-One-Subject-Out-Validation
        for exclude in subjects:
            print("Training - excluding subject: %s" % exclude)
            train_data = np.array([])
            for subject in subjects:
                for trial in range(1,6):
                    t, ppg, hr, fs_est = self.__get_data(directory, subject, trial, fs)

                    if subject != exclude:
                        train_data = np.append(train_data, self.__process_ppg(ppg)) 

            # Train the GMM
            train_data = train_data.reshape(-1,1) # convert from (N,1) to (N,) vector
            self.__gmm = GMM(n_components=2).fit(train_data)

            # Test the GMM on excluded subject
            # print("Testing - all trials of subject: %s" % exclude)
            # for trial in range(1,6):
            #     t, ppg, hr, fs_est = self.__get_data(directory, exclude, trial, fs)
            #     test_data = self.__process_ppg(ppg)

            #     labels = self.__gmm.predict(test_data.reshape(-1,1))

            #     hr_est, peaks = self.__estimate_hr(labels, len(ppg), fs)

            #     print("File: %s_%s: HR: %3.2f, HR_EST: %3.2f" % (exclude,trial,hr,hr_est))
        
    def save_gmm(self, filename="gmm_model.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.__gmm, f)

    def load_gmm(self, filename="gmm_model.pkl"):
        with open(filename, "rb") as f:
            self.__gmm = pickle.load(f)