import time
import RPi.GPIO as GPIO

class StepperMotor:
    def __init__(self, dir_pin, step_pin, steps_per_position=32, total_time=1.0):
        """
        Inicializa el motor paso a paso con un controlador A4988.
        :param dir_pin: Pin GPIO para la dirección.
        :param step_pin: Pin GPIO para los pulsos de paso.
        :param steps_per_position: Número de pasos necesarios para recorrer una posición discreta.
        :param total_time: Tiempo total para cada movimiento, incluyendo reposo (en segundos).
        """
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.steps_per_position = steps_per_position
        self.total_time = total_time
        self.current_position = 0  # Posición actual (0-20)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

    def cleanup(self):
        """Limpia los pines GPIO al finalizar."""
        GPIO.cleanup()

    def move_to(self, target_position):
        """
        Mueve el motor a la posición objetivo y respeta el tiempo fijo t.
        :param target_position: Posición objetivo (0-20).
        """
        # Calcula la cantidad de pasos a mover
        steps_to_move = (target_position - self.current_position) * self.steps_per_position
        direction = GPIO.HIGH if steps_to_move > 0 else GPIO.LOW
        steps_to_move = abs(steps_to_move)

        # Configura la dirección del motor
        GPIO.output(self.dir_pin, direction)

        # Divide el tiempo disponible entre los pasos
        move_time = self.total_time / 2  # Tiempo para moverse (t/2)
        delay_per_step = move_time / (steps_to_move or 1)

        # Genera los pulsos para mover el motor
        for _ in range(steps_to_move):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay_per_step / 2)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay_per_step / 2)

        self.current_position = target_position  # Actualiza la posición actual

        # Reposo durante t/2 en la posición objetivo
        time.sleep(move_time)

    def follow_positions(self, positions):
        """
        Sigue una lista de posiciones discretas.
        :param positions: Lista de posiciones a seguir (0-20).
        """
        for target_position in positions:
            self.move_to(target_position)

if __name__ == "__main__":
    try:
        # Pines GPIO para el controlador A4988
        dir_pin = 5  # Pin de dirección
        step_pin = 6  # Pin de paso (STEP)

        # Inicializa el motor
        motor = StepperMotor(dir_pin, step_pin, steps_per_position=32, total_time=1.0)

        # Lista de posiciones a seguir (0-20)
        positions = [5, 1, 19, 8, 2, 1, 14]  # Ejemplo de lista de 100 posiciones
        motor.follow_positions(positions)

    except KeyboardInterrupt:
        print("Ejecución interrumpida.")
    finally:
        motor.cleanup()