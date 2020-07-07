import RPi.GPIO as GPIO
import time
import threading

class HCSR04(threading.Thread):
    def __init__(self, trig, echo, delay=0.1, timeout=0.1, max_distance=300, callback=None, *args, **kwargs):
        super(HCSR04, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.trig = trig
        self.echo = echo
        self.delay = delay
        self.max_distance = max_distance
        self.callback = callback

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
    
    def stop(self):
        self._stop_event.set()

    def is_running(self):
        return not self._stop_event.is_set()

    def measure(self, event):
        self.pulse_duration = None
        try:
            while GPIO.input(self.echo) == 0 and not event.is_set():
                pulse_start = time.time()
            

            while GPIO.input(self.echo) == 1 and not event.is_set():
                pulse_end = time.time()
        
            if event.is_set(): 
                self.pulse_duration = None
            else:
                self.pulse_duration = pulse_end - pulse_start
        except:
            event.set()
    
    def run(self):
        while not self._stop_event.is_set():
            GPIO.output(self.trig, False)
            time.sleep(self.delay)

            GPIO.output(self.trig, True)
            time.sleep(1e-5)
            GPIO.output(self.trig, False)
            
            event = threading.Event()
            threading.Thread(target=self.measure, args=(event,)).start()
            # Wait to timeout.
            time.sleep(self.delay)
            if self.pulse_duration == None:
                event.set()
            
            else:    
                pulse_duration = self.pulse_duration
                # multiply with the sonic speed (34300 cm/s)
                # and divide by 2, because there and back
                distance = pulse_duration * 17150
                distance = round(distance, 2)

                if distance > 2 and distance < self.max_distance:
                    self.distance = distance
                else:
                    self.distance = 0
                
                if self.callback:
                    self.callback(self.distance)
            
            del event

def myCallback(x:int):
    print("My Distance:", x)

if __name__ == '__main__':
    TRIG = 23
    ECHO = 24

    hcsr04 = HCSR04(trig=TRIG, echo=ECHO, delay=0.1, timeout=0.1, max_distance=100, callback=myCallback)
    hcsr04.start()

    print("Threading Test")
    print(hcsr04.is_running())

    time.sleep(10)
    hcsr04.stop()


    