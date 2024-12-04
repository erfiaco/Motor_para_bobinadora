import RPi.GPIO as GPIO
import time

class Nema17Motor:
    def __init__(self, step_pin, dir_pin, steps_per_rev=200, max_delay=0.01):
        """
        Clase para controlar un motor NEMA 17.

        :param step_pin: Pin GPIO para STEP.
        :param dir_pin: Pin GPIO para DIR.
        :param steps_per_rev: Número de pasos por revolución.
        :param max_delay: Retardo máximo entre pasos (velocidad mínima).
        """
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.steps_per_rev = steps_per_rev
        self.max_delay = max_delay

        # Configuración de los pines GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)

    def move_continuous(self, direction=True, target_rps=1, acceleration_steps=2000):
        """
        Mueve el motor de forma continua con una aceleración suave hasta la velocidad objetivo.

        :param direction: Dirección del giro (True = horario, False = antihorario).
        :param target_rps: Velocidad objetivo en revoluciones por segundo (RPS).
        :param acceleration_steps: Número de pasos para alcanzar la velocidad objetivo.
        """
        GPIO.output(self.dir_pin, direction)
        target_delay = 1 / (target_rps * self.steps_per_rev)  # Convertir RPS a delay entre pasos

        try:
            step = 0
            while True:
                # Calcular retardo dinámico para los pasos dentro del rango de aceleración
                if step < acceleration_steps:
                    progress = step / acceleration_steps
                    step_delay = self.max_delay - progress * (self.max_delay - target_delay)
                else:
                    step_delay = target_delay  # Mantener velocidad constante

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

    @staticmethod
    def get_rps():
        """Solicita la velocidad deseada en revoluciones por segundo (RPS)."""
        while True:
            try:
                rps = float(input("Ingrese la velocidad en revoluciones por segundo (RPS): "))
                if rps > 0:
                    return rps
                else:
                    print("La velocidad debe ser mayor que 0.")
            except ValueError:
                print("Por favor, ingrese un número válido.")


# Función principal
def main():
    # Crear instancia del motor
    motor = Nema17Motor(step_pin=17, dir_pin=27)

    try:
        # Solicitar datos al usuario
        print("Configuración del movimiento continuo del motor:")
        direction = UserInputHandler.get_direction()
        target_rps = UserInputHandler.get_rps()

        print(f"Iniciando movimiento continuo con aceleración suave:")
        print(f"Dirección: {'Horario' if direction else 'Antihorario'}, Velocidad objetivo: {target_rps:.2f} RPS.")
        motor.move_continuous(direction=direction, target_rps=target_rps)

    except KeyboardInterrupt:
        print("\nMovimiento interrumpido por el usuario.")

    finally:
        motor.cleanup()
        print("GPIO limpio. Programa terminado.")


if __name__ == "__main__":
    main()
