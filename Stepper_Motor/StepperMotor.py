import RPi.GPIO as GPIO
import time

class StepperMotor:
    def __init__(self, pins, step_sequence):
        """
        Inicializa el motor paso a paso.
        :param pins: Lista de pines GPIO conectados al motor.
        :param step_sequence: Secuencia de pasos para el motor.
        """
        self.pins = pins
        self.step_sequence = step_sequence
        self.setup()

    def setup(self):
        """
        Configura los pines GPIO.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pins, GPIO.OUT)
        GPIO.output(self.pins, GPIO.LOW)

    def move_forward(self, duration, delay=0.001):
        """
        Hace girar el motor hacia adelante durante un tiempo dado.
        :param duration: Tiempo en segundos para girar el motor.
        :param delay: Tiempo entre pasos (control de velocidad).
        """
        start_time = time.time()
        while time.time() - start_time < duration:
            for step in self.step_sequence:
                for pin, value in zip(self.pins, step):
                    GPIO.output(pin, value)
                time.sleep(delay)

    def move_backward(self, duration, delay=0.001):
        """
        Hace girar el motor hacia atrás durante un tiempo dado.
        :param duration: Tiempo en segundos para girar el motor.
        :param delay: Tiempo entre pasos (control de velocidad).
        """
        start_time = time.time()
        while time.time() - start_time < duration:
            for step in reversed(self.step_sequence):  # Secuencia invertida
                for pin, value in zip(self.pins, step):
                    GPIO.output(pin, value)
                time.sleep(delay)

    def stop(self):
        """
        Apaga el motor liberando los pines.
        """
        GPIO.output(self.pins, GPIO.LOW)

    def cleanup(self):
        """
        Limpia la configuración de GPIO.
        """
        GPIO.cleanup()

# Flujo principal
if __name__ == "__main__":
    # Pines GPIO y secuencia de pasos
    PINS = [4, 17, 27, 22]
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

    # Crear instancia del motor
    motor = StepperMotor(PINS, STEP_SEQUENCE)

    try:
        motor.move_forward(5)  # Gira hacia adelante durante 5 segundos
        #motor.move_backward(5)  # Gira hacia atrás durante 5 segundos
    finally:
        motor.stop()
        motor.cleanup()
