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
    DATA = 23
    DATA_W = 24
    USE_R = 27
    USE_W = 22

    def __init__(self):

        self.__running = False
        self.__transmitting = False
        self.__receiving = False

        gpio.setmode(gpio.BCM)

        gpio.setup(IffynetController.CLOCK, gpio.IN)
        #gpio.add_event_detect(IffynetController.CLOCK, gpio.BOTH, self.clock_edge_detected)

        gpio.setup(IffynetController.DATA, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.add_event_detect(IffynetController.DATA, gpio.RISING, self.receive_byte)

        gpio.setup(IffynetController.DATA, gpio.OUT)
        gpio.output(IffynetController.DATA, gpio.LOW)

        #self.__clock_rate = IffynetController.determine_clock_rate()


    def stop(self):
        self.__running = False

    @staticmethod
    def byte_to_bits(byte):

        if type(byte) != int:

            i = int.from_bytes(byte)

        else:
            i = byte

        bits = list(bin(i)[2:].zfill(8))

        bits = map(int, bits)

        return list(bits)

    def transmit(self, data:bytearray):

        self.__transmitting = True

        for byte in data:
            bits_to_transmit = self.byte_to_bits(byte)
            print(f"{byte}: {bits_to_transmit}")

            # Send start condition by going from low to high whilst clock is high
            gpio.wait_for_edge(IffynetController.CLOCK, gpio.RISING)
            gpio.output(IffynetController.DATA, GPIO.HIGH)

            for bit in bits_to_transmit:
                # Transmit each bit by setting the output pin to the low or high when the clock is low
                gpio.wait_for_edge(IffynetController.CLOCK, gpio.FALLING)
                gpio.output(IffynetController.DATA, bit)
                print(f"Transmitted {bit}")

            # Send stop condition
            gpio.wait_for_edge(IffynetController.CLOCK, gpio.FALLING)
            gpio.output(IffynetController.DATA, GPIO.LOW)

        self.__transmitting = False

    def receive_byte(self, channel):

        # This method is triggered on CLOCK HIGH

        if self.__transmitting or self.__receiving: return

        gpio.output(IffynetController.DATA, gpio.LOW)

        # Check for start condition, which is that the DATA pin should go from LOW to HIGH whilst the CLOCK pin is
        # HIGH
        if gpio.input(IffynetController.CLOCK) == gpio.HIGH:

            self.__receiving = True

            received_bits = []

            for i in range(8):
                gpio.wait_for_edge(IffynetController.CLOCK, gpio.RISING)
                received_bits.append(gpio.input(IffynetController.DATA))
                print(f"Received {gpio.input(IffynetController.DATA)}")

            self.__receiving = False

            bit_string = ""
            for bit in received_bits:
                bit_string += str(bit)

            try:

                i = int(bit_string, 2)

                print(f"Received bits: {received_bits}, Value: {i} ({chr(i)})")

                return i

            except ValueError:
                return None


    @staticmethod
    def determine_clock_rate():

        high_times = []
        intervals = []

        print("Determining clock rate...")

        for i in range(10):
            gpio.wait_for_edge(IffynetController.CLOCK, gpio.RISING)
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

    def clock_edge_detected(self, channel):
        if gpio.input(IffynetController.CLOCK) == 1:
            print("CLOCK HIGH detected!")
        else:
            print("CLOCK LOW detected!")


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

    signal.signal(signal.SIGINT, clean_up)

    ifn = IffynetController()

    if "-send" in sys.argv:

        while True:
            d = int(input("Enter value to transmit\n> "))
            if d == -1:
                break
            ifn.transmit([d])

    signal.pause()  # Pause the main program, allowing the edge detection threads to continue running
