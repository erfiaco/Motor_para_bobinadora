import RPi.GPIO as GPIO
import time

# Pines para el motor paso a paso
PINS = [4, 17, 27, 22]  # Conecta estos pines al ULN2003 (Board: 7 11 13 15)

# Secuencia para el motor paso a paso (8 pasos)
STEP_SEQUENCE = [
    [1, 0, 0, 0],  # Paso 1
    [1, 1, 0, 0],  # Paso 2
    [0, 1, 0, 0],  # Paso 3
    [0, 1, 1, 0],  # Paso 4
    [0, 0, 1, 0],  # Paso 5
    [0, 0, 1, 1],  # Paso 6
    [0, 0, 0, 1],  # Paso 7
    [1, 0, 0, 1],  # Paso 8
]

def setup():
    """
    Configura los pines GPIO.
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PINS, GPIO.OUT)
    GPIO.output(PINS, GPIO.LOW)

def endavant(t):
    """
    Hace girar el motor en un sentido durante `t` segundos.
    """
    start_time = time.time()
    while time.time() - start_time < t:
        for step in STEP_SEQUENCE:
            for pin, value in zip(PINS, step):
                GPIO.output(pin, value)
            time.sleep(0.1)  # Delay entre pasos

def apagar_motor():
    """
    Apaga el motor liberando los pines.
    """
    GPIO.output(PINS, GPIO.LOW)

# Flujo principal
setup()
try:
    endavant(5)  # Gira durante 5 segundos
finally:
    apagar_motor()
    GPIO.cleanup()
