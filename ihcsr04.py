import RPi.GPIO as GPIO
import time
import threading
from PyQt5 import QtCore


class IHCSR04(QtCore.QThread):    
    def __init__(self, trig, echo, delay=0.7, timeout=1.5, max_distance=300, _round_=True, callback=None, *args, **kwargs):
        super(IHCSR04, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.trig = trig
        self.echo = echo
        self.delay = delay # SN
        self.timeout = timeout # SN
        self.max_distance = max_distance
        self.callback = callback
        self.is_round = _round_

        self.__pulse_start = None
        self.__pulse_end = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.echo, GPIO.FALLING, 
            callback=self.distance_handler, bouncetime=1)

    def distance_handler(self, channel):
        if GPIO.input(channel) == 0 and self.__pulse_start:
            self.__pulse_end = time.time()
            distance = (self.__pulse_end - self.__pulse_start)*17500
            if distance > 2 and distance < self.max_distance:
                self.distance = distance if not self.is_round else round(distance,2)
                if self.callback: self.callback(self.distance)
            else:
                self.distance = 0

    def stop(self):
        self._stop_event.set()

    def is_running(self):
        return not self._stop_event.is_set()

    def measure_init(self):
        GPIO.output(self.trig, False)
        time.sleep(0.1)
    def measure_pulse(self):
        GPIO.output(self.trig, True)
        time.sleep(1e-5)
        GPIO.output(self.trig, False)
    def measure_signal(self):
        self.measure_init()
        self.measure_pulse()

    def run(self):
        while not self._stop_event.is_set():
            # Start
            self.measure_signal()
            alert_begin = time.time()
            while GPIO.input(self.echo) == 0:
                if time.time() - alert_begin > self.timeout:
                    self.measure_signal()
                    alert_begin = time.time()
                #print(GPIO.input(self.echo), end='') ##For signal stream
                self.__pulse_start = time.time()
            time.sleep(self.delay)
            __pulse_start = None

def myCallback(x:float):
    print("My Distance:", x)
        
if __name__ == '__main__':
    TRIG = 23
    ECHO = 24

    hcsr04 = IHCSR04(trig=TRIG, echo=ECHO, delay=0.1, timeout=0.1, max_distance=100, callback=myCallback)
    hcsr04.start()

    print("Threading Test")
    print(hcsr04.is_running())

    time.sleep(10)
    hcsr04.stop()