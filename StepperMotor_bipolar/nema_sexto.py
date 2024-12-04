import RPi.GPIO as GPIO
import time
import math
from threading import Thread
import LCD_I2C_classe as LCD


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
        self.state_changes = 0  # Contador de pasos generados

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
                self.state_changes += 1  # Incrementar el contador de pasos
                time.sleep(step_delay)
    
                step += 1
    
        except KeyboardInterrupt:
            print("\nMovimiento interrumpido por el usuario.")
    
    def medir_velocidad(self, duration=1.0):
        """
        Mide la velocidad del motor en revoluciones por segundo (RPS).
        :param duration: Duración en segundos para medir la velocidad.
        :return: Velocidad en RPS.
        """
        initial_state_changes = self.state_changes  # Registrar el estado inicial
        time.sleep(duration)  # Esperar el tiempo definido
        final_state_changes = self.state_changes  # Registrar el estado final

        # Calcular el número de pasos realizados
        steps = (final_state_changes - initial_state_changes) // 2  # Cada paso tiene dos cambios de estado

        # Calcular revoluciones por segundo (RPS)
        revolutions = steps / self.steps_per_rev
        rps = revolutions / duration

        return rps
    
    def cleanup(self):
        """Limpia los pines GPIO."""
        GPIO.cleanup()


from threading import Thread
import time

class UserInputHandler:
    def __init__(self, motor, lcd=LCD):
        """
        Clase para manejar la interacción con el usuario y medir velocidades continuamente.
        :param motor: Instancia de la clase Nema17Motor.
        :param lcd: Instancia opcional de un controlador de LCD para mostrar información.
        """
        self.motor = motor
        self.lcd = LCD.LCD_I2C()  # LCD opcional para mostrar datos
        self.medicion_activa = False  # Estado de medición continua
        self.velocidades = []  # Almacén de velocidades medidas

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

    def medir_continuamente(self, interval):
        """
        Método ejecutado en un hilo para medir la velocidad continuamente.
        :param interval: Intervalo de tiempo entre mediciones.
        """
        while self.medicion_activa:
            rps = self.motor.medir_velocidad(duration=interval)
            self.velocidades.append(rps)

            if self.lcd:
                self.lcd.write(f"Velocidad: {rps:.2f} RPS", 1)  # Mostrar en LCD (si está disponible)
                time.sleep(2)
                self.lcd.clear()
            else:
                print(f"Velocidad medida: {rps:.2f} RPS")  # Mostrar en consola como alternativa

            time.sleep(interval)

    def iniciar_medicion_continua(self, interval=1.0):
        """
        Inicia un hilo separado para medir la velocidad del motor continuamente.
        :param interval: Intervalo de tiempo entre mediciones.
        """
        if self.medicion_activa:
            print("La medición continua ya está activa.")
            return

        self.medicion_activa = True
        self.hilo_medicion = Thread(target=self.medir_continuamente, args=(interval,))
        self.hilo_medicion.daemon = True  # Finaliza automáticamente con el programa principal
        self.hilo_medicion.start()
        print("Medición continua iniciada.")

    def detener_medicion_continua(self):
        """
        Detiene el hilo de medición continua.
        """
        self.medicion_activa = False
        if hasattr(self, 'hilo_medicion') and self.hilo_medicion.is_alive():
            self.hilo_medicion.join()
        print("Medición continua detenida.")
        
    def ejecutar(self):
        """
        Lógica principal para obtener datos del usuario y ejecutar el motor.
        """
        try:
             # Solicitar datos al usuario
            print("Configuración del movimiento continuo del motor:")
            direction = UserInputHandler.get_direction()
            target_rps = UserInputHandler.get_rps()
        
            print(f"Ejecutando motor: Velocidad = {self.motor.speed}, Sentido = {direction}")
            
                       
            # Iniciar la medición continua
            self.iniciar_medicion_continua(interval=1.0)
            
            # Crear un hilo para ajustar la velocidad dinámicamente
            '''
            speed_thread = Thread(target=self.ajustar_velocidad)
            speed_thread.start()
            '''
            
            # Iniciar el movimiento del motor
            self.motor.move_continuous(direction=direction, target_rps=target_rps, acceleration_steps=800, min_target_rps=0.2)
            
            # Detener la medición continua
            self.detener_medicion_continua() 
            
            
                
            
            '''
            # Esperar a que el hilo de ajuste de velocidad termine
            speed_thread.join()
            '''
            
            # Detener la medición continua
            self.detener_medicion_continua()
            
            # Mostrar las mediciones finales
            self.lcd.clear()
            self.lcd.write(f"Vel final: {self.velocidades}",1)
            time.sleep(2)
            self.lcd.clear()
            
        except KeyboardInterrupt:
            print("\nMovimiento interrumpido por el usuario.")

        finally:
            motor.cleanup()
            print("GPIO limpio. Programa terminado.")







if __name__ == "__main__":
    
    # Crear instancia del motor con los pines de microstepping
    motor = Nema17Motor(step_pin=17, dir_pin=27, ms1_pin=5, ms2_pin=6, ms3_pin=13)
    control = UserInputHandler(motor, lcd = lcd)
    control.ejecutar()
