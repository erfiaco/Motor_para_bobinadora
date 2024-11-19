'''Añadimos que se apague después de 5seg en HIGH. Además añadimos el GPIO.Cleanup para que libere los pines'''

import RPi.GPIO as GPIO
import time

EN  = 4
IN1 = 17
IN2 = 27

def setup():
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([EN,IN1,IN2],GPIO.OUT)

def endavant(t):
    
    GPIO.output(EN, GPIO.HIGH)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    time.sleep(t)
    GPIO.output(EN, GPIO.LOW)
    
setup()
endavant(5)
GPIO.cleanup()