'''Empezamos a trabajar por clases'''

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
        self.setup()

    def setup(self):
        """
        Configura los pines GPIO.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.en, self.in1, self.in2], GPIO.OUT)

    def endavant(self, t):
        """
        Activa el motor en dirección hacia adelante durante `t` segundos.
        """
        GPIO.output(self.en, GPIO.HIGH)
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        time.sleep(t)

    def stop(self, t):
        """
        Detiene el motor durante `t` segundos.
        """
        GPIO.output(self.en, GPIO.LOW)
        time.sleep(t)

    def cleanup(self):
        """
        Limpia los pines GPIO.
        """
        GPIO.cleanup()


class ProgramaMotor:
    def __init__(self):
        """
        Inicializa el motor con los pines correspondientes.
        """
        self.motor = MotorDC(en=4, in1=17, in2=27)

    def obtener_datos_usuario(self):
        """
        Obtiene el tiempo de funcionamiento del motor del usuario.
        """
        try:
            t = float(input("Introduce el tiempo en segundos para el movimiento: "))
            return t
        except ValueError:
            print("Por favor, introduce un número válido.")
            return self.obtener_datos_usuario()

    def ejecutar(self):
        """
        Controla el flujo principal del programa.
        """
        try:
            t = self.obtener_datos_usuario()
            self.motor.endavant(t)
            self.motor.stop(2)  # Tiempo de parada
        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario.")
        finally:
            self.motor.cleanup()
            print("Limpieza de GPIO completada.")


if __name__ == "__main__":
    programa = ProgramaMotor()
    programa.ejecutar()