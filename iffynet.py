from threading import Thread
import time, sys, signal

def clean_up(sig, frame):

    # TODO: This feels out of place, look for better location

    ifn.stop()
    gpio.cleanup()  # cleanup all GPIO

    print("Finished.")


class Clock(Thread):

    def __init__(self, gpio_clock_pin, clock_rate = 2):
        Thread.__init__(self)
        self.__clock_pin = gpio_clock_pin
        self.__rate = clock_rate
        gpio.setup(self.__clock_pin, gpio.OUT)
        self.__running = True

    def run(self):
        # TODO: Look for nicer way to end the thread so that it's less messy
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

    # Declare constants for GPIO BCM pin numbers
    CLOCK = 18
    DATA_R = 23
    DATA_W = 24
    USE_R = 27
    USE_W = 22


    def __init__(self, master=False, clock_rate=2):

        self.__master = master
        self.__clock = None
        self.__running = True

        if master:
            # initialise clock
            self.__clock = Clock(IffynetController.CLOCK, clock_rate)
            self.__clock.start()
        else:
            # Need to put into slave state, syncing to clock and starting communications
            gpio.setup(IffynetController.CLOCK, gpio.IN)
            gpio.add_event_detect(IffynetController.CLOCK, gpio.RISING, callback=IffynetController.clock_respond,
                                  bouncetime=100)
            signal.pause()

    def stop(self):
        if self.__clock:
            self.__clock.stop()
            time.sleep(self.__clock.interval)

        self.__running = False

    def clock_respond(self):
        print (f"Clock {'HIGH' if gpio.input(IffynetController.CLOCK) else 'LOW'}")


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

    if "-clock" in sys.argv:
        i = sys.argv.index("-clock")
        clock_rate = int(sys.argv[i + 1])

    if "-master" in sys.argv:
        master = True

    if "-dev" in sys.argv:
        import GPIO as gpio
    else:
        import RPi.GPIO as gpio


    gpio.setmode(gpio.BCM)
    signal.signal(signal.SIGINT, clean_up)

    ifn = IffynetController(master=master, clock_rate=clock_rate)