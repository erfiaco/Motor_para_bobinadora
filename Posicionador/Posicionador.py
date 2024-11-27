import time
import RPi.GPIO as GPIO

class StepperMotor:
    def __init__(self, pins, step_delay=0.001):
        """
        Inicializa el motor paso a paso.
        :param pins: Lista de pines GPIO [A, B, C, D] en el orden correcto.
        :param step_delay: Tiempo entre pasos (ajustable para controlar la velocidad).
        """
        self.pins = pins
        self.step_delay = step_delay
        self.current_position = 0 # Posición actual (0-20)
        self.steps_per_position = 32 # Número de pasos para recorrer 0.25 mm
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
        
        

        GPIO.setmode(GPIO.BCM)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def cleanup(self):
        """Limpia los pines GPIO al finalizar."""
        GPIO.cleanup()

    def set_step(self, step):
        """Establece el estado de los pines para un paso específico. asigna a los pines (6,13,19,26) el vector [1,0,0,1]"""
        for pin, value in zip(self.pins, step):
            GPIO.output(pin, value)

    def move_to(self, target_position):
        """
        Mueve el motor a la posición objetivo.
        :param target_position: Posición objetivo (0-20).
        """
        steps_to_move = (target_position - self.current_position) * self.steps_per_position
        direction = 1 if steps_to_move > 0 else -1
        steps_to_move = abs(steps_to_move)

        for _ in range(steps_to_move):
            for step in (self.full_step_sequence if direction > 0 else reversed(self.full_step_sequence)):
                self.set_step(step)
                time.sleep(self.step_delay)

        self.current_position = target_position

    def calculate_speed(self, current_pos, next_pos, time_interval):
        """
        Calcula el tiempo entre pasos (velocidad) basado en la distancia a recorrer.
        :param current_pos: Posición actual.
        :param next_pos: Siguiente posición.
        :param time_interval: Tiempo total para el movimiento.
        """
        distance = abs(next_pos - current_pos) * self.steps_per_position
        if distance == 0:
            return self.step_delay
        return time_interval / (distance * len(self.full_step_sequence))
        
    def prueba(self):
    
        # Guarda el tiempo inicial
        start_time = time.time()
        
        while time.time() - start_time < 5:
            for steps in (self.full_step_sequence):
                GPIO.output(self.pins, steps)
                time.sleep(0.001)
    
        

    def follow_positions(self, positions, time_interval=0.5):
        """
        Sigue una lista de posiciones con velocidad adaptativa.
        :param positions: Lista de posiciones a seguir.
        :param time_interval: Tiempo disponible para cada movimiento.
        """
        for pos in positions:
            self.step_delay = self.calculate_speed(self.current_position, pos, time_interval)
            self.move_to(pos)
            time.sleep(time_interval - self.step_delay * abs(self.current_position - pos) * self.steps_per_position)

if __name__ == "__main__":
    try:
        
        # Pines GPIO de la Raspberry Pi
        motor_pins = [6, 13, 19, 26]
        motor = StepperMotor(motor_pins)
        '''
        # Lista de posiciones (input del usuario)
        positions = [5, 1, 19, 8, 2, 1, 14] # Ejemplo, reemplaza por tu lista de 100 posiciones
        motor.follow_positions(positions)
        '''
        
        motor.prueba()
        
    except KeyboardInterrupt:
        print("Ejecución interrumpida.")
    finally:
        motor.cleanup()