import atexit
import time
import RPi.GPIO as GPIO
import math
from threading import Thread
import LCD_I2C_classe as LCD



class StepperMotor:
    """
    Clase para controlar un motor paso a paso bipolar con un controlador como DRV8825 o A4988.
    """
    def __init__(self, step_pin, dir_pin, speed):
        """
        Inicializa el motor paso a paso.
        :param step_pin: Pin GPIO para la señal de paso (STEP).
        :param dir_pin: Pin GPIO para la direccion (DIR).
        :param steps_per_revolution: Numero de pasos por revolucion.
        :param speed: Velocidad inicial del motor (en revoluciones por segundo).
        """
        self.step_pin = step_pin 
        self.dir_pin = dir_pin
        self.steps_per_revolution = 200
        self.speed = speed  # En revoluciones por segundo
        self.current_speed = 0
        self.state_changes = 0
        self.setup()
        self.running = False  # Bandera para controlar el bucle del motor
        
       

    def setup(self):
        """
        Configura los pines GPIO.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.output(self.step_pin, GPIO.LOW)
        GPIO.output(self.dir_pin, GPIO.LOW)
        
    def medir_velocidad(self, duration=1.0):
        """
        Mide la velocidad del motor en revoluciones por segundo (RPS).
        """
        initial_state_changes = self.state_changes # Registrar el estado inicial
        time.sleep(duration) # Esperar el tiempo definido
        final_state_changes = self.state_changes # Registrar el estado final

        steps = final_state_changes - initial_state_changes
        revolutions = steps / self.steps_per_revolution
        rps = revolutions / duration
        return rps

    def calculate_delays(self):
        """
        Calcula un vector con los valores de delay para ajustar la velocidad gradualmente.
        :param steps: Numero de pasos para alcanzar la velocidad deseada.
        :return: Lista de valores de delay.
        """
        min_delay = 0.001
        
        self.delays = []  # Lista para almacenar los valores de delay
        for _ in range(1000):
            # Factor de incremento proporcional
            factor = _ / 101  # Escala entre 0 y 1
            # Calcular el delay
            delay = factor * (1 / (self.speed * self.steps_per_revolution))

            # Guardar el delay en la lista
            self.delays.append(delay)

        return delays   

    

    def move(self, direction, speed):
        """
        Mueve el motor en la direccion especificada indefinidamente.
        :param direction: 'fw' o 'bw'.
        """
        target_speed = self.speed
        #self.set_speed(0)  # Iniciar desde velocidad 0
        current_speed = 0
        
        #Gestiona el sentido del movimiento
        if direction == "fw":  
            GPIO.output(self.dir_pin, GPIO.HIGH)
        elif direction == "bw":
            GPIO.output(self.dir_pin, GPIO.LOW)
        else:
            raise ValueError("Direccion invalida. Usa 'fw' o 'bw'.")
        
            
        self.running = True
        i = 0
            while self.running:
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.delays[i] / 2)  # Usar delay correspondiente
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.delays[i] / 2)  # Usar delay correspondiente
            self.state_changes += 1

            # Incrementar `i` solo si aún no ha alcanzado el último índice
            if i < len(self.delays) - 1:  # Último índice es len(self.delays) - 1
                i += 1
            else:
                i = len(self.delays) - 1  # Mantener el índice en el máximo


    def stop(self):
        """
        Detiene el motor apagando las señales.
        """
        self.running = False
        GPIO.output(self.step_pin, GPIO.LOW)

    def cleanup(self):
        """
        Limpia la configuracion de GPIO.
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
        self.running = True
        self.medicion_activa = False
        #self.velocidades = []
        self.lcd = LCD.LCD_I2C()

    def obtener_datos_usuario(self):
        """
        Solicita al usuario la velocidad y el sentido de movimiento.
        """
        while True:
            try:
                self.motor.speed = float(input("Introduce la velocidad (debe ser un numero positivo): "))
                if self.motor.speed <= 0:
                    print("La velocidad debe ser mayor que 0. Intentalo de nuevo.")
                    continue

                direction = input("Introduce el sentido ('fw' o 'bw'): ").strip().lower()
                if direction not in ["fw", "bw"]:
                    print("Por favor, introduce un sentido valido ('fw' o 'bw').")
                    continue

                return direction
            except ValueError:
                print("Entrada no valida. Asegurate de introducir un numero para la velocidad.")

    def ajustar_velocidad(self):
        """
        Permite cambiar la velocidad del motor dinamicamente mientras esta en funcionamiento.
        """
        while self.running:
            try:
                new_speed = float(input("Introduce la nueva velocidad (mayor que 0): "))
                if new_speed > 0:
                    self.motor.set_speed(new_speed)
                else:
                    print("La velocidad debe ser mayor que 0.")
            except ValueError:
                print("Entrada no valida. Introduce un numero valido.")
            except KeyboardInterrupt:
                print("\nDeteniendo ajuste de velocidad...")
                self.running = False
                break

    def medir_continuamente(self, interval):
        """
        Metodo ejecutado en un hilo para medir la velocidad continuamente.
        :param interval: Intervalo de tiempo entre mediciones.
        """
        while self.medicion_activa:
            rps = self.motor.medir_velocidad(duration=interval)
            self.velocidades.append(rps)
            self.lcd.write(f"Velocidad: {rps:.2f} RPS", 1)
            time.sleep(2)
            self.lcd.clear()

    def iniciar_medicion_continua(self, interval=1.0):
        """
        Inicia un hilo separado para medir la velocidad del motor continuamente.
        """
        self.medicion_activa = True
        self.hilo_medicion = Thread(target=self.medir_continuamente, args=(interval,))
        self.hilo_medicion.daemon = True
        self.hilo_medicion.start()

    def detener_medicion_continua(self):
        """
        Detiene el hilo de medicion continua.
        """
        self.medicion_activa = False
        if hasattr(self, 'hilo_medicion') and self.hilo_medicion.is_alive():
            self.hilo_medicion.join()
        print("Medicion continua detenida.")

    def ejecutar(self):
        """
        Logica principal para obtener datos del usuario y ejecutar el motor.
        """
        try:
            direction = self.obtener_datos_usuario()
            print(f"Ejecutando motor: Velocidad = {self.motor.speed}, Sentido = {direction}")
            self.iniciar_medicion_continua(interval=1.0)
            speed_thread = Thread(target=self.ajustar_velocidad)
            speed_thread.start()
            self.motor.move(direction, self.motor.speed)
            speed_thread.join()
            self.detener_medicion_continua()
            self.lcd.clear()
            self.lcd.write(f"Vel final: {self.velocidades}", 1)
            time.sleep(2)
            self.lcd.clear()

        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario.")
        finally:
            self.motor.stop()
            self.motor.cleanup()


# Ejemplo de uso
if __name__ == "__main__":
    step_pin = 17  # Pin STEP
    dir_pin = 27   # Pin DIR
    steps_per_revolution = 200

    motor = StepperMotor(step_pin, dir_pin, steps_per_revolution, speed=1.0)
    control = MotorControl(motor)
    control.ejecutar()
