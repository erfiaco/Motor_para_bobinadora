import time
import RPi.GPIO as GPIO
import LCD_I2C_classe as LCD

lcd = LCD.LCD_I2C()

lcd.write("Hello",1)
time.sleep(2)
lcd.clear()






