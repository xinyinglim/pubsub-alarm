from time import sleep
from gpiozero import DistanceSensor, LED

house_boundary = 15 # in cm
alarm_led = LED (13) #red led

sensor = DistanceSensor(echo = 19, trigger = 26)
 
while True:
    distance = sensor.distance * 100
    print('Distance: ', distance)
    if distance < house_boundary:
        if not alarm_led.is_lit:
            alarm_led.on()
    else :
        alarm_led.off()

    sleep(1)