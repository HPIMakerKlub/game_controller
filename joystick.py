import RPi.GPIO as GPIO
import time
import sys

pin_x = 15
pin_xm = 18
pin_y = 23
pin_ym = 24
pin_press = 14


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_x, GPIO.IN)
    GPIO.setup(pin_xm, GPIO.IN)
    GPIO.setup(pin_y, GPIO.IN)
    GPIO.setup(pin_ym, GPIO.IN)
    GPIO.setup(pin_press, GPIO.IN)


def loop():
    x, xm, y, ym, press = GPIO.input(pin_x), GPIO.input(pin_xm), GPIO.input(pin_y), GPIO.input(pin_ym), GPIO.input(
        pin_press)

    if x:
        sys.stdout.write('right ')
    elif not xm:
        sys.stdout.write('left ')

    if y:
        sys.stdout.write('up ')
    elif not ym:
        sys.stdout.write('down ')

    if press:
        sys.stdout.write('pressed')

    sys.stdout.flush()
    print('')


if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
            time.sleep(0.5)
    except KeyboardInterrupt:
        GPIO.cleanup()
