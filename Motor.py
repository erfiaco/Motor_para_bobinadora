import RPi.GPIO as GPIO
import time

EN = 4
IN1 = 17
IN2 = 27

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([EN, IN1, IN2], GPIO.OUT)

def endavant(t):
    GPIO.output(EN, GPIO.HIGH)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    time.sleep(t)

def stop(t):
    GPIO.output(EN, GPIO.LOW)
    time.sleep(2)

try:
    setup()
    t = float(input("Introduce el tiempo en segundos para el movimiento: "))
    endavant(t)
    stop(t)
finally:
    GPIO.cleanup()
    print("Limpieza de GPIO completada.")