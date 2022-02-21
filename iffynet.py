from threading import Thread
import time, sys, signal


def clean_up(sig, frame):
    ifn.stop()
    gpio.cleanup()  # cleanup all GPIO
    #sys.exit(0)
    print("Finished.")


class Clock(Thread):

    def __init__(self, gpio_clock_pin, clock_rate = 2):
        Thread.__init__(self)
        self.__clock_pin = gpio_clock_pin
        self.__rate = clock_rate
        gpio.setup(self.__clock_pin, gpio.OUT)
        self.__running = True

    def run(self):
        try:
            while self.__running:
                # Set clock pin low/high at regular interval
                gpio.output(self.__clock_pin, gpio.HIGH)
                time.sleep(1/self.__rate)
                gpio.output(self.__clock_pin, gpio.LOW)
                time.sleep(1/self.__rate)

        finally:
            pass

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
            self.__clock = Clock(18, clock_rate)
            self.__clock.start()

    def stop(self):
        self.__clock.stop()

    @property
    def master(self):
        return self.__master

    @property
    def clock_rate(self):
        if self.__clock:
            return self.__clock.rate
        else:
            return None


if __name__ == "__main__":
    # Check arguments and adjust RPi library
    clock_rate = 2
    master = False

    if len(sys.argv) > 1:
        if "-pi" in sys.argv:
            import RPi.GPIO as gpio
        else:
            import GPIO as gpio

        if "-clock" in sys.argv:
            i = sys.argv.index("-clock")
            clock_rate = int(sys.argv[i + 1])

        if "-master" in sys.argv:
            master = True

    gpio.setmode(gpio.BCM)
    signal.signal(signal.SIGINT, clean_up)

    ifn = IffynetController(master=master, clock_rate=clock_rate)