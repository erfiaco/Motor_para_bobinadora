import time
import RPi.GPIO as GPIO

class BipolarMotor:
    def __init__(self, step_pin, dir_pin):
        """
        Inicializa el motor paso a paso con un controlador bipolar.
        :param step_pin: Pin GPIO para los pulsos de paso.
        :param dir_pin: Pin GPIO para la dirección.
        """
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.output(self.step_pin, GPIO.LOW)
        GPIO.output(self.dir_pin, GPIO.LOW)

    def move_steps(self, steps, direction, delay=0.001):
        """
        Mueve el motor un número específico de pasos en una dirección dada.
        :param steps: Número de pasos a mover.
        :param direction: Dirección del movimiento ('right' o 'left').
        :param delay: Tiempo de espera entre pasos (segundos).
        """
        
        # Establece la dirección
        if direction == 0:
            GPIO.output(self.dir_pin, GPIO.HIGH)
        elif direction == 1:
            GPIO.output(self.dir_pin, GPIO.LOW)
        else:
            raise ValueError("Dirección no válida. Usa 'right' o 'left'.")
        
        # Genera los pulsos de paso
        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(delay / 2)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(delay / 2)
    
    
    def generate_steps_matrix(self, positions):
        """
        Genera una matriz con el número de pasos necesarios y la dirección para alcanzar
        cada posición objetivo desde la posición actual.
    
        :param positions: Lista de posiciones en el eje X.
        :return: Lista de listas (matriz) con pasos y direcciones.
        """
        current_position = 0
        steps_matrix = []

        for target_position in positions:
            steps = abs(target_position - current_position)
            direction = 1 if target_position > current_position else 0
            steps_matrix.append([steps, direction])
            current_position = target_position  # Actualiza la posición actual
    
        return steps_matrix

    
    
    def cleanup(self):
        """Limpia los pines GPIO."""
        GPIO.output(self.step_pin, GPIO.LOW)
        GPIO.output(self.dir_pin, GPIO.LOW)
        GPIO.cleanup()

if __name__ == "__main__":
    # Pines GPIO
    STEP_PIN = 17  # Pin de paso
    DIR_PIN = 27   # Pin de dirección

    # Inicializa el motor
    motor = BipolarMotor(STEP_PIN, DIR_PIN)

    try:
        # Vector de movimientos: [(pasos, dirección)]
        positions = [400, 50, 50, 1, 30, 5, 2]
        
        movements = motor.generate_steps_matrix(positions)
        

        # Ejecutar los movimientos en el vector
        for steps, direction in movements:
            print(f"Moviendo {steps} pasos hacia {direction}...")
            current_t = time.time()
            motor.move_steps(steps, direction)
            elapsed_time = time.time() - current_t
            time.sleep(1 - elapsed_time)  # Esperar el tiempo restante
            

    except KeyboardInterrupt:
        print("Ejecución interrumpida.")
    finally:
        motor.cleanup()
        print("Pines GPIO limpiados. Programa terminado.")
