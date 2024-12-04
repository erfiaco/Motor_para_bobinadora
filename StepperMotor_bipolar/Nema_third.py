import RPi.GPIO as GPIO
import time
import argparse

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

    def move_smooth(self, revolutions, direction=True):
        """
        Mueve el motor suavemente aumentando la velocidad desde 0% hasta 100%.

        :param revolutions: Número total de revoluciones a realizar.
        :param direction: Dirección del giro (True = horario, False = antihorario).
        """
        total_steps = int(revolutions * self.steps_per_rev)

        # Configurar la dirección
        GPIO.output(self.dir_pin, direction)

        for step in range(total_steps):
            # Calcular retardo dinámico basado en el progreso
            progress = step / total_steps
            step_delay = self.max_delay - progress * (self.max_delay - self.min_delay)

            # Generar pulso
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(step_delay)  # Tiempo en HIGH
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(step_delay)  # Tiempo en LOW

    def cleanup(self):
        """Limpia los pines GPIO."""
        GPIO.cleanup()


# Función principal
def main():
    # Crear el parser de argumentos
    parser = argparse.ArgumentParser(description="Controlar un motor NEMA 17 con velocidad incremental.")
    parser.add_argument("revolutions", type=float, help="Número de revoluciones a realizar.")
    parser.add_argument("direction", type=str, choices=["horario", "antihorario"], help="Dirección del giro.")

    args = parser.parse_args()

    # Configuración de parámetros dinámicos
    revolutions = args.revolutions
    direction = True if args.direction == "horario" else False

    # Crear instancia del motor
    try:
        motor = Nema17Motor(step_pin=17, dir_pin=27)

        print(f"Iniciando movimiento: {revolutions} revoluciones, dirección: {'Horario' if direction else 'Antihorario'}...")
        motor.move_smooth(revolutions=revolutions, direction=direction)

    except KeyboardInterrupt:
        print("\nMovimiento interrumpido por el usuario.")

    finally:
        motor.cleanup()
        print("GPIO limpio. Programa terminado.")


if __name__ == "__main__":
    main()
