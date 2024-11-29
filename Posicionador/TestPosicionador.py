import time
import RPi.GPIO as GPIO


class StepperMotor:
    def __init__(self, dir_pin, step_pin, total_time=1.0):
        """
        Inicializa el motor paso a paso con un controlador A4988.
        :param dir_pin: Pin GPIO para la dirección.
        :param step_pin: Pin GPIO para los pulsos de paso.
        :param total_time: Tiempo total para el movimiento (en segundos).
        """
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.total_time = total_time

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

    def cleanup(self):
        """Limpia los pines GPIO al finalizar."""
        GPIO.cleanup()

    def move(self, steps, direction=GPIO.HIGH):
        """
        Mueve el motor generando pulsos en el pin STEP.
        :param steps: Número de pasos a realizar.
        :param direction: Dirección del movimiento (GPIO.HIGH o GPIO.LOW).
        """
        GPIO.output(self.dir_pin, direction)

        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(0.001)  # Ajusta el tiempo entre pulsos para la velocidad
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(0.001)


if __name__ == "__main__":
    try:
        # Pines GPIO para el controlador A4988
        dir_pin = 5  # Pin de dirección
        step_pin = 6  # Pin de paso (STEP)

        # Inicializa el motor
        motor = StepperMotor(dir_pin, step_pin)

        print("Moviendo motor en dirección HORARIA...")
        motor.move(200, GPIO.HIGH)  # 200 pasos en sentido horario
        time.sleep(2)

        print("Moviendo motor en dirección ANTIHORARIA...")
        motor.move(200, GPIO.LOW)  # 200 pasos en sentido antihorario

    except KeyboardInterrupt:
        print("Ejecución interrumpida.")
    finally:
        motor.cleanup()
