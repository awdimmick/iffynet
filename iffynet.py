from threading import Thread
import time, sys, signal, math

import GPIO


def clean_up(sig, frame):

    gpio.cleanup()  # cleanup all GPIO
    print("Finished.")


class IffynetController():

    # Declare constants for GPIO BCM pin numbers
    CLOCK = 18
    DATA_R = 23
    DATA_W = 24
    USE_R = 27
    USE_W = 22

    def __init__(self):

        self.__running = False

        gpio.setup(IffynetController.CLOCK, gpio.IN)

        self.__clock_rate = IffynetController.determine_clock_rate()

        #signal.pause()  # Pause the main program, allowing the edge detection threads to continue running

    def stop(self):
        self.__running = False

    @staticmethod
    def determine_clock_rate():

        high_times = []
        intervals = []

        print("Determining clock rate...")

        for i in range(10):
            gpio.wait_for_edge(IffynetController.CLOCK, GPIO.RISING)
            high_times.append(time.time())

        for i in range(len(high_times) - 1):
            intervals.append(high_times[i+1] - high_times[i])

        average_interval = sum(intervals) / len(intervals)

        clock_rate = round(1 / average_interval, 5)

        variance = (max(intervals) - min(intervals)) / average_interval

        print(f"Clock rate detected: {clock_rate:0.3f}Hz (variance {variance * 100:0.2f}%)")

        return clock_rate


    @staticmethod
    def clock_respond(channel):
        # TODO: Modify this function to test for start condition and then fill buffer with data until stop condition
        #  is met. Seems to reliably read data at up to 100Hz.

        if gpio.input(IffynetController.CLOCK) == gpio.HIGH:
            now = time.time()
            IffynetController.clock_interval = now - IffynetController.last_clock_high
            IffynetController.last_clock_high = now

        print (f"Clock {'HIGH' if gpio.input(IffynetController.CLOCK) else 'LOW'}. Time since last HIGH: {IffynetController.clock_interval}s. "
               f"Detected clock rate: {1/IffynetController.clock_interval:0.3f}Hz")

    @staticmethod
    def do_nothing(self):
        pass

    def detect_clock_rise(self):
        self.__clock_high_detection_times.append(time.time())





if __name__ == "__main__":
    # Check arguments and adjust RPi library

    if "-dev" in sys.argv:
        import GPIO as gpio
    else:
        import RPi.GPIO as gpio

    gpio.setmode(gpio.BCM)
    signal.signal(signal.SIGINT, clean_up)

    ifn = IffynetController()