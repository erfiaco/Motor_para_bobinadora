import time
import RPi.GPIO as GPIO


class Posicionador:
    def __init__(self, dir_pin, step_pin):
        """
        Inicializa el motor paso a paso con un controlador A4988.
        :param dir_pin: Pin GPIO para la dirección.
        :param step_pin: Pin GPIO para los pulsos de paso.
        :param total_time: Tiempo total para el movimiento (en segundos).
        """
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.total_time = total_time

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

    def cleanup(self):
        """Limpia los pines GPIO al finalizar."""
        GPIO.cleanup()

    def move(self):
        """
        Mueve el motor generando pulsos en el pin STEP.
        :param steps: Número de pasos a realizar.
        :param direction: Dirección del movimiento (GPIO.HIGH o GPIO.LOW).
        """
        


        # Configuración inicial
        min_delay = 0.0001  # Delay entre pasos
        current_p = 0  # Posición inicial del motor
        posiciones = [18, 9, 6, 2, 13, 14, 12, 3, 10, 7]  # Ejemplo de posiciones lineales

        # Bucle para recorrer las posiciones del vector
        for pos in posiciones:
            current_t = time.time()  # Tiempo al inicio de este movimiento

            # Determinar la dirección del motor
            if pos > current_p:
                multi_steps = abs(pos - current_p)  # Pasos necesarios
                GPIO.output(self.step_dir, GPIO.HIGH)  # Girar hacia adelante
            elif pos < current_p:
                multi_steps = abs(pos - current_p)
                GPIO.output(self.step_dir, GPIO.LOW)  # Girar hacia atrás
            else:
                continue  # Si la posición es la misma, no hacer nada

        # Generar pulsos para alcanzar la nueva posición
        for _ in range(multi_steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(min_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(min_delay)

        # Actualizar la posición actual
        current_p = pos

        # Esperar hasta completar 1 segundo desde el inicio de este movimiento
        elapsed_time = time.time() - current_t
        if elapsed_time < 1:
            time.sleep(1 - elapsed_time)  # Esperar el tiempo restante

            
            

        
      

if __name__ == "__main__":
    try:
        # Pines GPIO para el controlador A4988
        dir_pin = 5  # Pin de dirección
        step_pin = 6  # Pin de paso (STEP)

        # Inicializa el motor
        motor = Posicionador(dir_pin, step_pin)

        
        motor.move()
        
    except KeyboardInterrupt:
        print("Ejecución interrumpida.")
    finally:
        motor.cleanup()
