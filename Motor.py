import RPi.GPIO as GPIO
import time

class MotorDC:
    def __init__(self, en, in1, in2):
        """
        Inicializa los pines del motor.
        """
        self.en = en
        self.in1 = in1
        self.in2 = in2
        self.pwm = None
        self.setup()

    def setup(self):
        """
        Configura los pines GPIO y el PWM para control de velocidad.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.en, self.in1, self.in2], GPIO.OUT)
        self.pwm = GPIO.PWM(self.en, 100)  # Frecuencia del PWM: 100 Hz
        self.pwm.start(0)  # Inicializamos con duty cycle de 0 (motor apagado)

    def encender_motor(self, sentido, t):
        """
        Activa el motor en el sentido especificado con velocidad gradual.
        Parámetros:
            sentido: 'horario' o 'antihorario'
            t: Tiempo en segundos que el motor debe activarse
        """
        if sentido == "horario":
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)
        elif sentido == "antihorario":
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
        else:
            print("Sentido no válido. Usa 'horario' o 'antihorario'.")
            return

        # Incrementar la velocidad gradualmente
        for duty_cycle in range(0, 101, 5):  # Incrementa de 0 a 100 en pasos de 5
            self.pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # Tiempo entre incrementos

        time.sleep(t)  # Mantiene la velocidad máxima durante el tiempo `t`

    def stop(self, t):
        """
        Detiene el motor gradualmente.
        """
        # Reducir la velocidad gradualmente
        for duty_cycle in range(100, -1, -5):  # De 100 a 0 en pasos de -5
            self.pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.1)  # Tiempo entre decrementos

        time.sleep(t)  # Pausa después de detener el motor

    def cleanup(self):
        """
        Limpia los pines GPIO.
        """
        self.pwm.stop()
        GPIO.cleanup()


class ProgramaMotor:
    def __init__(self):
        """
        Inicializa el motor con los pines correspondientes.
        """
        self.motor = MotorDC(en=4, in1=17, in2=27)

    def obtener_datos_usuario(self):
        """
        Obtiene los datos del usuario: tiempo de movimiento y sentido de giro.
        """
        try:
            t = float(input("Introduce el tiempo en segundos para el movimiento: "))
            sentido = input("Introduce el sentido ('horario' o 'antihorario'): ").strip().lower()
            if sentido not in ["horario", "antihorario"]:
                print("Por favor, introduce un sentido válido ('horario' o 'antihorario').")
                return self.obtener_datos_usuario()
            return t, sentido
        except ValueError:
            print("Por favor, introduce un número válido.")
            return self.obtener_datos_usuario()

    def ejecutar(self):
        """
        Controla el flujo principal del programa.
        """
        try:
            t, sentido = self.obtener_datos_usuario()
            self.motor.encender_motor(sentido, t)
            self.motor.stop(2)  # Tiempo de parada
        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario.")
        finally:
            self.motor.cleanup()
            print("Limpieza de GPIO completada.")


if __name__ == "__main__":
    programa = ProgramaMotor()
    programa.ejecutar()