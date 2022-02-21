from threading import Thread
import time
import GPIO as gpio

gpio.setmode(gpio.BCM)


class Clock(Thread):

    def __init__(self, gpio_clock_pin, clock_rate = 2):
        Thread.__init__()
        self.__clock_pin = gpio_clock_pin
        self.__rate = clock_rate
        gpio.setup(self.__clock_pin, gpio.OUT)
        self.__running = True

    def run(self):
        while self.__running:
            # Set clock pin low/high at regular interval
            gpio.output(self.__clock_pin, gpio.HIGH)
            time.sleep(1/self.__rate)
            gpio.output(self.__clock_pin, gpio.LOW)
            time.sleep(1/self.__rate)

    def stop(self):
        self.__running = False

    @property
    def rate(self):
        return self.__rate

    @property
    def interval(self):
        return 1 / self.__rate


class IffynetController():
    def __init__(self, master=False, clock_rate=2):

        self.__master = master
        self.__clock = None

        if master:
            # initialise clock
            self.__clock = Clock(clock_rate)
            self.__clock.start()

    @property
    def master(self):
        return self.__master

    @property
    def clock_rate(self):
        if self.__clock:
            return self.__clock.rate
        else:
            return None
    