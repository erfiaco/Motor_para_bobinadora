import RPi.GPIO as GPIO
import time

class Nema17Motor:
    def __init__(self, step_pin, dir_pin, steps_per_rev=200, max_delay=0.01, min_delay=0.001):
        """
        Clase para controlar un motor NEMA 17.

        :param step_pin: Pin GPIO para STEP.
        :param dir_pin: Pin GPIO para DIR.
        :param steps_per_rev: Número de pasos por revolución.
        :param max_delay: Retardo máximo entre pasos (velocidad mínima).
        :param min_delay: Retardo mínimo entre pasos (velocidad máxima).
        """
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.steps_per_rev = steps_per_rev
        self.max_delay = max_delay
        self.min_delay = min_delay

        # Configuración de los pines GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

    def move_continuous(self, direction=True):
        """
        Mueve el motor de forma continua con incremento de velocidad desde 0% hasta 100%.

        :param direction: Dirección del giro (True = horario, False = antihorario).
        """
        GPIO.output(self.dir_pin, direction)

        try:
            step = 0
            while True:
                # Calcular retardo dinámico basado en el progreso
                progress = (step % self.steps_per_rev) / self.steps_per_rev
                step_delay = self.max_delay - progress * (self.max_delay - self.min_delay)

                # Generar pulso
                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(step_delay)  # Tiempo en HIGH
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(step_delay)  # Tiempo en LOW

                step += 1  # Incrementar el conteo de pasos

        except KeyboardInterrupt:
            print("\nMovimiento interrumpido por el usuario.")

    def cleanup(self):
        """Limpia los pines GPIO."""
        GPIO.cleanup()


class UserInputHandler:
    @staticmethod
    def get_direction():
        """Solicita la dirección del giro al usuario."""
        while True:
            direction = input("Ingrese la dirección (horario/antihorario): ").strip().lower()
            if direction in ["horario", "antihorario"]:
                return True if direction == "horario" else False
            else:
                print("Por favor, ingrese 'horario' o 'antihorario'.")


# Función principal
def main():
    # Crear instancia del motor
    motor = Nema17Motor(step_pin=17, dir_pin=27)

    try:
        # Solicitar datos al usuario
        print("Configuración del movimiento continuo del motor:")
        direction = UserInputHandler.get_direction()

        print(f"Iniciando movimiento continuo en dirección: {'Horario' if direction else 'Antihorario'}...")
        motor.move_continuous(direction=direction)

    except KeyboardInterrupt:
        print("\nMovimiento interrumpido por el usuario.")

    finally:
        motor.cleanup()
        print("GPIO limpio. Programa terminado.")


if __name__ == "__main__":
    main()
