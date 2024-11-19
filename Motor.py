import RPi.GPIO as GPIO
import time

EN = 4
IN1 = 17
IN2 = 27

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([EN, IN1, IN2], GPIO.OUT)

def endavant(t):
    GPIO.output(EN, GPIO.HIGH)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    time.sleep(t)

def stop(t):
    GPIO.output(EN, GPIO.LOW)
    time.sleep(t)

def obtener_datos_usuario():
    """
    Función para recopilar datos del usuario.
    Puede extenderse en el futuro si necesitas más información.
    """
    try:
        t = float(input("Introduce el tiempo en segundos para el movimiento: "))
        # Si deseas más información, puedes añadirla aquí.
        # Ejemplo:
        # velocidad = float(input("Introduce la velocidad del motor (0.0 a 1.0): "))
        return t
    except ValueError:
        print("Por favor, introduce un número válido.")
        return obtener_datos_usuario()

def main():
    try:
        setup()
        t = obtener_datos_usuario()
        endavant(t)
        stop(2)  # Tiempo de parada
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
    finally:
        GPIO.cleanup()
        print("Limpieza de GPIO completada.")

if __name__ == "__main__":
    main()


'''
Porqué has añadido las útimas dos lineas?
ChatGPT Plus
ChatGPT
Las últimas dos líneas del código son estas:

python
Copiar código
if __name__ == "__main__":
    main()
Estas líneas cumplen una función importante en la estructura del programa en Python. Aquí te explico su propósito y por qué es una buena práctica incluirlas:

1. ¿Qué hacen estas líneas?
if __name__ == "__main__":
Esta línea verifica si el archivo se está ejecutando como programa principal o si está siendo importado como módulo en otro programa.

Si ejecutas este archivo directamente (por ejemplo, con python3 archivo.py), el valor de __name__ será "__main__", y el código dentro del bloque se ejecutará (en este caso, la función main()).
Si este archivo es importado desde otro script, el valor de __name__ no será "__main__", y el bloque no se ejecutará automáticamente.
main()
Llama a la función principal del programa, que contiene el flujo de ejecución.

2. ¿Por qué es útil?
Reutilización de código: Si en el futuro decides importar este archivo como módulo en otro programa, el código dentro de main() no se ejecutará automáticamente. Esto evita comportamientos no deseados.
Por ejemplo, podrías importar funciones como setup() o endavant() desde este archivo en otro proyecto, sin que el programa principal (el flujo en main) se ejecute.
Claridad y organización: Separa el flujo principal (main()) del resto del código. Esto hace que el programa sea más fácil de leer y mantener.
Mejor práctica en Python: Es un estándar recomendado para scripts en Python, especialmente en proyectos que podrían evolucionar o ser reutilizados.
3. ¿Qué pasa si no las añades?
Si no incluyes estas líneas y el código se ejecuta directamente, funcionará correctamente.
Pero si alguien importa tu archivo en otro programa, el código completo (incluido setup(), endavant(), y demás) se ejecutará automáticamente, lo que puede causar errores o comportamientos inesperados.
Ejemplo práctico
Supón que tienes el archivo DCMotor.py con tu código. Si alguien lo importa en otro programa:

python
Copiar código
from DCMotor import setup, endavant

setup()
endavant(5)
Sin if __name__ == "__main__":, todo el flujo de tu programa (incluyendo la interacción con el usuario y la ejecución de main()) se ejecutará automáticamente cuando se importe, lo cual no es deseado.

Conclusión
Añadir estas dos líneas hace que tu programa sea más modular, reutilizable y acorde a las buenas prácticas de Python. Aunque no es obligatorio para scripts simples, es una excelente práctica para proyectos más grandes o código que podría ser reutilizado en el futuro.
'''