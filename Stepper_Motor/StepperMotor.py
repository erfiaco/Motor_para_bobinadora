import atexit
import time
import RPi.GPIO as GPIO
import math
from threading import Thread



class StepperSequences:
    """
    Clase para gestionar las secuencias de pasos del motor.
    """
    def __init__(self):
        self.full_step_sequence = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1],
        ]
        self.wave_drive_sequence = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]

    def get_sequence(self, mode):
        """
        Devuelve la secuencia correspondiente al modo.
        :param mode: Modo de secuencia ('full_step' o 'wave_drive').
        """
        if mode == "full_step":
            return self.full_step_sequence
        elif mode == "wave_drive":
            return self.wave_drive_sequence
        else:
            raise ValueError(f"Modo desconocido: {mode}")


class StepperMotor:
    """
    Clase para controlar un motor paso a paso.
    """
    def __init__(self, pins, sequences, speed=1.0):
        """
        Inicializa el motor paso a paso.
        :param pins: Lista de pines GPIO conectados al motor.
        :param sequences: Instancia de la clase StepperSequences.
        :param speed: Velocidad inicial del motor.
        """
        self.pins = pins
        self.sequences = sequences
        self.speed = speed
        self.current_mode = "full_step"  # Modo inicial
        self.setup()

    def setup(self):
        """
        Configura los pines GPIO.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pins, GPIO.OUT)
        GPIO.output(self.pins, GPIO.LOW)

    def set_speed(self, new_speed, steps=50):
        """
        Cambia la velocidad gradualmente con un aumento logarítmico.
        :param new_speed: Nueva velocidad objetivo.
        :param steps: Número de pasos para la transición de velocidad.
        """
        if new_speed == self.speed:
            return

        log_start = math.log(1)  # Evitar log(0)
        log_end = math.log(steps + 1)
        for step in range(1, steps + 1):
            factor = (math.log(step + 1) - log_start) / (log_end - log_start)
            self.speed = self.speed + factor * (new_speed - self.speed)
            time.sleep(0.01)
            if self.speed > 3.0:
                self.current_mode = "wave_drive"
            else:
                self.current_mode = "full_step"
        self.speed = new_speed

    def move(self, direction, duration):
        """
        Mueve el motor en la dirección especificada durante un tiempo dado.
        El motor acelera gradualmente con un incremento logarítmico.
        """
        target_speed = self.speed
        self.set_speed(0)  # Iniciar desde velocidad 0
        sequence = self.sequences.get_sequence(self.current_mode)

        # Aumentar gradualmente hasta la velocidad objetivo
        steps = 100  # Número de pasos para incrementar la velocidad
        log_start = math.log(1)  # Evitar log(0)
        log_end = (math.log(steps + 1))/math.log(101)
        current_speed = 0
        start_time = time.time()

        while time.time() - start_time < duration:
            delay = 0.001 / current_speed if current_speed > 0 else 0.1
            steps_sequence = sequence if direction == "forward" else reversed(sequence)
            for step in steps_sequence:
                for pin, value in zip(self.pins, step):
                    GPIO.output(pin, value)
                time.sleep(delay)

            # Incrementar velocidad logarítmicamente
            if current_speed < target_speed:
                step = int((time.time() - start_time) / duration * steps) + 1
                #factor = (math.log(step + 1) - log_start) / (log_end - log_start) #Logaritmico
                factor = (1/(1+math.exp(-0.1*(step-50))))/(1/(1+math.exp(-0.1*(50)))) #Sigmoide
                current_speed = factor * target_speed
                current_speed = min(current_speed, target_speed)  # Limitar al máximo

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



class MotorControl:
    """
    Clase para gestionar el control del motor.
    """
    def __init__(self, motor):
        """
        Inicializa el controlador del motor.
        :param motor: Instancia de la clase StepperMotor.
        """
        self.motor = motor
        self.running = True  # Bandera para controlar el bucle

    def obtener_datos_usuario(self):
        """
        Solicita al usuario la velocidad y el sentido de movimiento.
        """
        while True:
            try:
                self.motor.speed = float(input("Introduce la velocidad (debe ser un número positivo): "))
                if self.motor.speed <= 0:
                    print("La velocidad debe ser mayor que 0. Inténtalo de nuevo.")
                    continue

                direction = input("Introduce el sentido ('forward' o 'backward'): ").strip().lower()
                if direction not in ["forward", "backward"]:
                    print("Por favor, introduce un sentido válido ('forward' o 'backward').")
                    continue

                return direction
            except ValueError:
                print("Entrada no válida. Asegúrate de introducir un número para la velocidad.")

    def ajustar_velocidad(self):
        """
        Permite cambiar la velocidad del motor dinámicamente mientras está en funcionamiento.
        """
        while self.running:
            try:
                new_speed = float(input("Introduce la nueva velocidad (mayor que 0): "))
                if new_speed > 0:
                    self.motor.set_speed(new_speed)
                else:
                    print("La velocidad debe ser mayor que 0.")
            except ValueError:
                print("Entrada no válida. Introduce un número válido.")
            except KeyboardInterrupt:
                print("\nDeteniendo ajuste de velocidad...")
                self.running = False
                break

    def ejecutar(self):
        """
        Lógica principal para obtener datos del usuario y ejecutar el motor.
        """
        try:
            direction = self.obtener_datos_usuario()
            print(f"Ejecutando motor: Velocidad = {self.motor.speed}, Sentido = {direction}")
            
            # Crear un hilo para ajustar la velocidad dinámicamente
            
            speed_thread = Thread(target=self.ajustar_velocidad)
            speed_thread.start()

            # Iniciar el movimiento del motor
            self.motor.move(direction, duration=20)
            
            # Esperar a que el hilo termine
            speed_thread.join()
            self.motor.stop()

        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario.")
            self.running = False
            self.motor.stop()
        finally:
            self.motor.cleanup()




# Ejemplo de uso
if __name__ == "__main__":
    # Configuración inicial
    pins = [4, 17, 27, 22]
    sequences = StepperSequences()
    motor = StepperMotor(pins, sequences, speed=1.0)
    control = MotorControl(motor)
    

    # Ejecutar el control
    control.ejecutar()