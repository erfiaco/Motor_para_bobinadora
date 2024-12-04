import atexit
import time
import RPi.GPIO as GPIO
import math
from threading import Thread
import LCD_I2C_classe as LCD
from threading import Lock
import sys
import select



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
        self.steps_per_revolution = steps_per_revolution
        self.speed = speed  # En revoluciones por segundo
        self.current_speed = 0
        self.state_changes = 0
        self.setup()
        self.running = False  # Bandera para controlar el bucle del motor
        self.lock = Lock()
        
       

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
        with self.lock:
            
            min_delay = 0.01
            target_delay = 1 / (self.steps_per_revolution * self.speed)
            steps = 400  # Número de pasos para el cambio lineal
        
            self.delays = []  # Lista para almacenar los valores de delay

            '''
            midpoint = steps / 2  # Punto medio de la sigmoide
            k = 0.1  # Constante que controla la pendiente
            sigmoid_value = 1 / (1 + math.exp(-k * (i - midpoint)))
            '''
            
            # Bucle para calcular y usar el delay interpolado
            for i in range(steps):
                # Calcular el delay actual redondeado a 5 decimales
                current_delay = round(min_delay + i * (target_delay - min_delay) / (steps - 1), 5) #funcion lineal

                '''
                
                current_delay = round(min_delay + (target_delay - min_delay) * (1 - sigmoid_value), 5)

                '''
                
                # Guardar el delay en la lista
                self.delays.append(current_delay)   

    

    def move(self, direction, speed):
        """
        Mueve el motor en la direccion especificada indefinidamente.
        
        """
        
        
        #Gestiona el sentido del movimiento
        if direction == "fw":  
            GPIO.output(self.dir_pin, GPIO.HIGH)
        elif direction == "bw":
            GPIO.output(self.dir_pin, GPIO.LOW)
        else:
            raise ValueError("Direccion invalida. Usa 'fw' o 'bw'.")
        
        self.calculate_delays()    
        self.running = True
        i = 0
        
        while self.running:
            with self.lock:
                current_delay = self.delays[i]
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(current_delay / 2)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(current_delay / 2)
            self.state_changes += 1

            if i < len(self.delays) - 1:
                i += 1

    
    def set_speed(self, new_speed):
        with self.lock:
            self.speed = new_speed
            self.calculate_delays()        

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
        self.velocidades = []
        self.lcd = LCD.LCD_I2C()

    def escuchar_comandos(self):
        """
        Escucha comandos del usuario y ejecuta acciones correspondientes.
        """
        while self.running:
            try:
                print("Presiona 'v' para cambiar la velocidad o 'Ctrl+C' para salir.")
                i, _, _ = select.select([sys.stdin], [], [], 0.5)  # Esperar entrada durante 0.5 segundos
                if i:
                    comando = sys.stdin.readline().strip()
                    if comando == "v":
                        self.ajustar_velocidad()
            except KeyboardInterrupt:
                print("Saliendo del modo de escucha...")
                self.running = False
                break
    
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
        Permite cambiar la velocidad del motor dinámicamente mientras está en funcionamiento.
        """
        try:
            new_speed = float(input("Introduce la nueva velocidad (mayor que 0): "))
            if new_speed > 0:
                self.motor.set_speed(new_speed)
                print(f"Velocidad ajustada a: {new_speed} RPS")
            else:
                print("La velocidad debe ser mayor que 0.")
        except ValueError:
            print("Entrada no válida. Introduce un número válido.")

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
            

            comando_thread = Thread(target=self.escuchar_comandos)
            comando_thread.daemon = True
            comando_thread.start()
            
            self.motor.move(direction, self.motor.speed)
            
            self.detener_medicion_continua()
            self.lcd.clear()
            self.lcd.write(f"Vel final: {self.velocidades}", 1)
            time.sleep(2)
            self.lcd.clear()

        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario.")
        finally:
            self.running = False
            self.motor.stop()
            self.detener_medicion_continua()
            
            self.motor.cleanup()
            self.lcd.clear()
            


# Ejemplo de uso
if __name__ == "__main__":
    step_pin = 17  # Pin STEP
    dir_pin = 27   # Pin DIR
    steps_per_revolution = 200

    motor = StepperMotor(step_pin, dir_pin, steps_per_revolution, speed=1.0)
    control = MotorControl(motor)
    control.ejecutar()
