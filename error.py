import RPi.GPIO as GPIO
import time
	
class Led():
	def __init__(self, pin):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(18, 0)
		#self._thread=Thread(target=self._blink)
	
	def blink(self, count, delay):
		for _ in range(0,count*2):
			input_state=GPIO.input(18)
			GPIO.output(18, 1-input_state)
			time.sleep(delay)
			
		
def main():
	status_led=Led(18)
	
	while True:
		status_led.blink(1,1)

if __name__ == "__main__":
	main()
