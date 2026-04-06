import time
from gpiozero import LED

if __name__ == "__main__":
  laser = LED(4, initial_value=False)

  try:
    while True:
      laser.on()
      time.sleep(2)
      laser.off()
      time.sleep(2)
    
  finally:
    laser.off()
