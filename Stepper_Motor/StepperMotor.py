import time
import RPi.GPIO as GPIO


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
        Cambia la velocidad gradualmente y ajusta el modo de secuencia si es necesario.
        """
        if new_speed == self.speed:
            return

        speed_diff = (new_speed - self.speed) / steps
        for _ in range(steps):
            self.speed += speed_diff
            time.sleep(0.01)
            if self.speed > 3.0:
                self.current_mode = "wave_drive"
            else:
                self.current_mode = "full_step"
        self.speed = new_speed

    def move(self, direction, duration):
        """
        Mueve el motor en la dirección especificada durante un tiempo dado.
        El motor acelera gradualmente desde velocidad 0.
        """
        target_speed = self.speed
        self.set_speed(0)  # Iniciar desde velocidad 0
        sequence = self.sequences.get_sequence(self.current_mode)

        # Aumentar gradualmente hasta la velocidad objetivo
        steps = 50  # Número de pasos para incrementar la velocidad
        speed_increment = target_speed / steps
        current_speed = 0
        start_time = time.time()

        while time.time() - start_time < duration:
            delay = 0.001 / current_speed if current_speed > 0 else 0.1
            steps_sequence = sequence if direction == "forward" else reversed(sequence)
            for step in steps_sequence:
                for pin, value in zip(self.pins, step):
                    GPIO.output(pin, value)
                time.sleep(delay)

            # Incrementar velocidad gradualmente
            if current_speed < target_speed:
                current_speed += speed_increment
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

    def obtener_datos_usuario(self):
        """
        Solicita al usuario la velocidad y el sentido de movimiento.
        """
        while True:
            try:
                self.motor.speed = float(input("Introduce la velocidad (debe ser un número positivo): "))
                if self.motor.speed < 0:
                    print("La velocidad no puede ser negativa. Inténtalo de nuevo.")
                    continue

                direction = input("Introduce el sentido ('forward' o 'backward'): ").strip().lower()
                if direction not in ["forward", "backward"]:
                    print("Por favor, introduce un sentido válido ('forward' o 'backward').")
                    continue

                return direction
            except ValueError:
                print("Entrada no válida. Asegúrate de introducir un número para la velocidad.")

    def ejecutar(self):
        """
        Lógica principal para obtener datos del usuario y ejecutar el motor.
        """
        try:
            direction = self.obtener_datos_usuario()
            print(f"Ejecutando motor: Velocidad = {self.motor.speed}, Sentido = {direction}")
            self.motor.set_speed(self.motor.speed)
            self.motor.move(direction, duration=20)
            self.motor.stop()
        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario.")
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