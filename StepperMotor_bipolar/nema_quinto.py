import RPi.GPIO as GPIO
import time

import RPi.GPIO as GPIO
import time

class Nema17Motor:
    def __init__(self, step_pin, dir_pin, ms1_pin, ms2_pin, ms3_pin, steps_per_rev=200, max_delay=0.001):
        """
        Clase para controlar un motor NEMA 17 con microstepping dinámico.

        :param step_pin: Pin GPIO para STEP.
        :param dir_pin: Pin GPIO para DIR.
        :param ms1_pin: Pin GPIO para MS1 (microstepping).
        :param ms2_pin: Pin GPIO para MS2 (microstepping).
        :param ms3_pin: Pin GPIO para MS3 (microstepping).
        :param steps_per_rev: Número de pasos por revolución.
        :param max_delay: Retardo máximo entre pasos (velocidad mínima).
        """
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.ms1_pin = ms1_pin
        self.ms2_pin = ms2_pin
        self.ms3_pin = ms3_pin
        self.steps_per_rev = steps_per_rev
        self.max_delay = max_delay

        # Configuración de los pines GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.ms1_pin, GPIO.OUT)
        GPIO.setup(self.ms2_pin, GPIO.OUT)
        GPIO.setup(self.ms3_pin, GPIO.OUT)

        # Configuración inicial: microstepping en 1/16
        self.set_microstepping(16)

    def set_microstepping(self, resolution):
        """
        Configura el nivel de microstepping en el driver A4988.

        :param resolution: Resolución deseada (1, 2, 4, 8, 16).
        """
        if resolution == 1:
            GPIO.output(self.ms1_pin, GPIO.LOW)
            GPIO.output(self.ms2_pin, GPIO.LOW)
            GPIO.output(self.ms3_pin, GPIO.LOW)
        elif resolution == 2:
            GPIO.output(self.ms1_pin, GPIO.HIGH)
            GPIO.output(self.ms2_pin, GPIO.LOW)
            GPIO.output(self.ms3_pin, GPIO.LOW)
        elif resolution == 4:
            GPIO.output(self.ms1_pin, GPIO.LOW)
            GPIO.output(self.ms2_pin, GPIO.HIGH)
            GPIO.output(self.ms3_pin, GPIO.LOW)
        elif resolution == 8:
            GPIO.output(self.ms1_pin, GPIO.HIGH)
            GPIO.output(self.ms2_pin, GPIO.HIGH)
            GPIO.output(self.ms3_pin, GPIO.LOW)
        elif resolution == 16:
            GPIO.output(self.ms1_pin, GPIO.HIGH)
            GPIO.output(self.ms2_pin, GPIO.HIGH)
            GPIO.output(self.ms3_pin, GPIO.HIGH)
        else:
            raise ValueError("Resolución no válida. Use 1, 2, 4, 8 o 16.")

    def move_continuous(self, direction=True, target_rps=1, acceleration_steps=4000, min_target_rps=0.1):
        """
        Mueve el motor con microstepping dinámico y aceleración suave.

        :param direction: Dirección del giro (True = horario, False = antihorario).
        :param target_rps: Velocidad objetivo en revoluciones por segundo (RPS).
        :param acceleration_steps: Número de pasos para alcanzar la velocidad objetivo.
        :param min_target_rps: Velocidad inicial mínima en RPS.
        """
        GPIO.output(self.dir_pin, direction)
        target_delay = 1 / (target_rps * self.steps_per_rev)  # Convertir RPS a delay entre pasos
        min_delay = 1 / (min_target_rps * self.steps_per_rev)  # Retardo inicial más lento

        try:
            step = 0
            while True:
                # Cambiar dinámicamente el microstepping durante la aceleración
                if step < acceleration_steps // 4:
                    self.set_microstepping(16)
                elif step < acceleration_steps // 2:
                    self.set_microstepping(8)
                elif step < (3 * acceleration_steps) // 4:
                    self.set_microstepping(4)
                else:
                    self.set_microstepping(1)

                # Calcular retardo dinámico
                progress = step / acceleration_steps
                step_delay = min_delay - (progress**2) * (min_delay - target_delay)

                # Generar pulso
                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(step_delay)
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(step_delay)

                step += 1

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

    # Crear instancia del motor con los pines de microstepping
    motor = Nema17Motor(step_pin=17, dir_pin=27, ms1_pin=5, ms2_pin=6, ms3_pin=13)

    try:
        # Solicitar datos al usuario
        print("Configuración del movimiento continuo del motor:")
        direction = UserInputHandler.get_direction()
        target_rps = UserInputHandler.get_rps()

        print(f"Iniciando movimiento continuo con aceleración suave y microstepping dinámico:")
        print(f"Dirección: {'Horario' if direction else 'Antihorario'}, Velocidad objetivo: {target_rps:.2f} RPS.")
        motor.move_continuous(direction=direction, target_rps=target_rps)

    except KeyboardInterrupt:
        print("\nMovimiento interrumpido por el usuario.")

    finally:
        motor.cleanup()
        print("GPIO limpio. Programa terminado.")



if __name__ == "__main__":
    main()
