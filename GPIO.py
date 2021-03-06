# GPIO simulator
import time

BCM = 1
BOARD = 2
IN = 0
OUT = 1
HIGH = 1
LOW = 0
RISING = 1
FALLING = 0
BOTH = 2
PUD_DOWN = 1
PUD_UP = 0

def setmode(mode):
    if mode == BCM:
        print("Mode set to BCM numbers")
    elif mode == BOARD:
        print("Mode set to BOARD numbers")


def setup(pin, mode, pull_up_down=None):
    print(f"Set pin {pin} to {'input' if mode == IN else 'output'}")


def input(pin, value=1):
    print(f"Reading pin {pin}, value is {value}")
    return value


def output(pin, state):
    print(f"Setting value of pin {pin} to {'low' if state == LOW else 'high'}")


def add_event_detect(pin, direction, callback, bouncetime):
    print(f"Added threaded listener for {pin} on {'RISING' if direction == RISING else 'FALLING'} edge. Callback"
          f"function: {callback}")


def wait_for_edge(pin, direction):
    print(f"Simulating waiting for {'RISING' if direction == RISING else 'FALLING'} edge on pin {pin}...")
    time.sleep(0.2)


def cleanup():
    print("Cleaning up all GPIO assignments.")

