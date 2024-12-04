import RPi.GPIO as GPIO
import time
import math


class Nema17Motor:
    def __init__(self, step_pin, dir_pin, ms1_pin, ms2_pin, ms3_pin, steps_per_rev=200, max_delay=0.005):
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
        Mueve el motor con aceleración basada en una función sigmoide y microstepping dinámico.
    
        :param direction: Dirección del giro (True = horario, False = antihorario).
        :param target_rps: Velocidad objetivo en revoluciones por segundo (RPS).
        :param acceleration_steps: Número de pasos para alcanzar la velocidad objetivo.
        :param min_target_rps: Velocidad inicial mínima en RPS.
        """
        GPIO.output(self.dir_pin, direction)
        target_delay = 1 / (target_rps * self.steps_per_rev)  # Convertir RPS a delay entre pasos
        min_delay = 1 / (min_target_rps * self.steps_per_rev)  # Retardo inicial más lento
    
        # Validar que los valores sean coherentes
        if min_delay < target_delay:
            min_delay = target_delay  # Evitar inconsistencias
    
        # Parámetros de la función sigmoide
        k = 10 / acceleration_steps  # Controla qué tan rápido crece la velocidad
        t0 = acceleration_steps / 2  # Punto de inflexión de la sigmoide
    
        try:
            step = 0
            while True:
                # Calcular el progreso como una función sigmoide
                progress = 1 / (1 + math.exp(-k * (step - t0)))  # Valor sigmoide entre 0 y 1
                step_delay = max(target_delay, min_delay - progress * (min_delay - target_delay))
    
                # Ajustar dinámicamente el microstepping según la velocidad actual
                current_rps = 1 / (step_delay * self.steps_per_rev)  # Velocidad actual en RPS
                if current_rps < 0.5 * target_rps:
                    self.set_microstepping(16)  # Velocidades bajas: 1/16 de paso
                elif current_rps < 0.75 * target_rps:
                    self.set_microstepping(8)   # Velocidades medias: 1/8 de paso
                elif current_rps < 0.9 * target_rps:
                    self.set_microstepping(4)   # Velocidades altas: 1/4 de paso
                else:
                    self.set_microstepping(1)   # Velocidad máxima: paso completo
    
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
            direction = input("Ingrese la dirección (fw/bw): ").strip().lower()
            if direction in ["fw", "bw"]:
                return True if direction == "fw" else False
            else:
                print("Por favor, ingrese 'fw' o 'bw'.")

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
        #motor.move_continuous(direction=direction, target_rps=target_rps)
        motor.move_continuous(direction=direction, target_rps=target_rps, acceleration_steps=800, min_target_rps=0.2)


    except KeyboardInterrupt:
        print("\nMovimiento interrumpido por el usuario.")

    finally:
        motor.cleanup()
        print("GPIO limpio. Programa terminado.")



if __name__ == "__main__":
    main()
