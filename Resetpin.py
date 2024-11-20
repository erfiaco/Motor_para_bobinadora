import RPi.GPIO as GPIO

# Configuración del pin 17
GPIO.setmode(GPIO.BCM)  # Usando numeración BCM
#GPIO.setup(17, GPIO.OUT)  # Configurar el pin 17 como salida
GPIO.output(17, GPIO.LOW)  # Apagar el pin 17

# Limpieza de configuración
GPIO.cleanup()
