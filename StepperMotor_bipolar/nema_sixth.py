import RPi.GPIO as GPIO
import time

# Configuración de pines GPIO
DIR_PIN = 20       # Pin de dirección
STEP_PIN = 21      # Pin de paso
ENABLE_PIN = 16    # Pin para habilitar el driver (opcional)
MS1_PIN = 5        # Pin de microstepping MS1
MS2_PIN = 6        # Pin de microstepping MS2
MS3_PIN = 13       # Pin de microstepping MS3

# Configuración del motor
STEPS_PER_REV = 200  # Pasos completos por revolución (sin microstepping)
MICROSTEP_RESOLUTION = 16  # Microstepping 1/16
TOTAL_STEPS = STEPS_PER_REV * MICROSTEP_RESOLUTION  # Pasos totales para una revolución

# Configurar GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(ENABLE_PIN, GPIO.OUT)
GPIO.setup(MS1_PIN, GPIO.OUT)
GPIO.setup(MS2_PIN, GPIO.OUT)
GPIO.setup(MS3_PIN, GPIO.OUT)

# Configuración inicial
GPIO.output(ENABLE_PIN, GPIO.LOW)  # Habilitar el driver
GPIO.output(DIR_PIN, GPIO.HIGH)   # Dirección del motor (HIGH o LOW)

# Configurar microstepping a 1/16 de paso
GPIO.output(MS1_PIN, GPIO.HIGH)
GPIO.output(MS2_PIN, GPIO.HIGH)
GPIO.output(MS3_PIN, GPIO.HIGH)

# Función para arranque suave
def smooth_start(steps, max_delay, min_delay, acceleration_steps):
    """
    Arranque suave para el motor NEMA 17.
    :param steps: Número total de pasos a realizar.
    :param max_delay: Retardo inicial entre pasos (en segundos).
    :param min_delay: Retardo mínimo entre pasos (para máxima velocidad).
    :param acceleration_steps: Número de pasos durante la aceleración.
    """
    delay = max_delay
    delay_decrement = (max_delay - min_delay) / acceleration_steps

    for step in range(steps):
        # Generar un pulso para un paso
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay)

        # Reducir el retardo durante la aceleración
        if step < acceleration_steps and delay > min_delay:
            delay -= delay_decrement

try:
    # Parámetros del arranque suave
    max_delay = 0.005  # Retardo inicial (en segundos)
    min_delay = 0.001  # Retardo mínimo (para máxima velocidad)
    acceleration_steps = 100  # Pasos para completar la aceleración

    print("Motor girando suavemente con arranque progresivo...")
    smooth_start(TOTAL_STEPS, max_delay, min_delay, acceleration_steps)
    print("Rotación completa con arranque suave finalizada.")

finally:
    # Limpiar GPIO al salir
    GPIO.output(ENABLE_PIN, GPIO.HIGH)  # Deshabilitar el driver
    GPIO.cleanup()
