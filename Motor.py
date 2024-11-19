'''Este código encenderá el motod en un sentido, y pondrá una pausa de 5 segundos. 
Antes de la pausa los pins estaban en alto, y obviamente seguirán en alto durante la pausa! 
Es decir, el motor nunca se apagará'''

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
    
setup()
endavant(5)