import pygame, random, sys, time, math
from pygame.locals import *
import RPi.GPIO as GPIO

pin_x = 15
pin_xm = 18
pin_y = 23
pin_ym = 24
pin_buzzer = 25

xs = [290, 290, 290, 290, 290]
ys = [290, 270, 250, 230, 210]

dirs = None
score = None
applepos = None
s = None
appleimage = None
f = None
clock = None
toggle = None
width = 700
block_size = 10
apple_score = 1
apple_size = block_size


def setup():
    global dirs, score, applepos, s, appleimage, img, f, clock, toggle
    dirs = 0
    score = 0
    applepos = (random.randint(block_size, width - block_size), random.randint(0, width - block_size))
    pygame.init()
    s = pygame.display.set_mode((width, width))
    pygame.display.set_caption('Snake')
    appleimage = pygame.Surface((apple_size, apple_size))
    appleimage.fill((0, 255, 0))
    img = pygame.Surface((block_size, block_size))
    img.fill((255, 255, 0))
    f = pygame.font.SysFont('Arial', 20)
    clock = pygame.time.Clock()
    toggle = False

    setup_joystick()
    setup_buzzer()
    play_melody('start')


def setup_joystick():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_x, GPIO.IN)
    GPIO.setup(pin_xm, GPIO.IN)
    GPIO.setup(pin_y, GPIO.IN)
    GPIO.setup(pin_ym, GPIO.IN)


def setup_buzzer():
    global C_notes, start_sound, point_sound, death_sound
    GPIO.setup(pin_buzzer, GPIO.OUT)
    C_notes = [123, 131, 147, 165, 175, 196, 220, 247,
               262, 294, 330, 349, 392, 440, 494,
               523, 587, 659, 698, 784, 880, 988]
    start_sound = [11, 13, 15, 13, 15, 17]
    point_sound = [7, 9, 11, 7, 9, 11]
    death_sound = [9, 7, 5]


def play_sound(note, duration):
    frequency = C_notes[note]
    period = 1.0 / frequency
    delay = period / 2
    cycles = int(duration / period)

    for i in range(cycles):
        GPIO.output(pin_buzzer, True)
        time.sleep(delay)
        GPIO.output(pin_buzzer, False)
        time.sleep(delay)


def play_melody(name):
    global C_notes, start_sound, point_sound, death_sound
    melodies = {'start': start_sound, 'point': point_sound, 'death': death_sound}
    melody = melodies[name]
    for note in melody:
        play_sound(note, 0.1)


def read_joystick():
    global toggle
    x, xm, y, ym = GPIO.input(pin_x), GPIO.input(pin_xm), GPIO.input(pin_y), GPIO.input(pin_ym)

    positions = []

    if x:
        positions.append('right')
    elif not xm:
        positions.append('left')

    if y:
        positions.append('up')
    elif not ym:
        positions.append('down')

    if len(positions) > 1:
        assert len(positions) == 2
        if toggle:
            position = positions[0]
        else:
            position = positions[1]
        toggle = not toggle
    elif len(positions) == 1:
        position = positions[0]
    else:
        return None

    position_to_direction = {'right': 1, 'left': 3, 'up': 2, 'down': 0}
    return position_to_direction[position]


def collide(x1, x2, y1, y2, w1, w2, h1, h2):
    if x1 + w1 > x2 and x1 < x2 + w2 and y1 + h1 > y2 and y1 < y2 + h2:
        return True
    else:
        return False


def die(screen, score):
    play_melody('death')
    f = pygame.font.SysFont('Arial', 30)
    t = f.render('Your score was: ' + str(score), True, (255, 255, 255))
    screen.blit(t, (10, 270))
    pygame.display.update()
    pygame.time.wait(2000)


def quit():
    GPIO.cleanup()
    sys.exit(0)


def loop():
    global xs, ys, dirs, score, applepos, pygame, s, appleimage, img, f, clock, apple_score, apple_size

    clock.tick(10 + score)
    for e in pygame.event.get():
        if e.type == QUIT:
            quit()

    new_dir = read_joystick()
    if new_dir is not None:
        if new_dir == 0 and dirs != 2:
            dirs = new_dir
        elif new_dir == 1 and dirs != 3:
            dirs = new_dir
        elif new_dir == 2 and dirs != 0:
            dirs = new_dir
        elif new_dir == 3 and dirs != 1:
            dirs = new_dir

    i = len(xs) - 1
    while i >= 2:
        if collide(xs[0], xs[i], ys[0], ys[i], block_size, block_size, block_size, block_size):
            die(s, score)
            return False
        i -= 1

    if collide(xs[0], applepos[0], ys[0], applepos[1], block_size, apple_size, block_size, apple_size):
        play_melody('point')
        score += 1
        for i in range(apple_score):
            xs.append(width)
            ys.append(width)
        apple_score = random.randint(1, 20)
        apple_size = int(math.sqrt(block_size * block_size * apple_score))
        applepos = (random.randint(apple_size, width - apple_size), random.randint(apple_size, width - apple_size))
        appleimage = pygame.Surface((apple_size, apple_size))
        appleimage.fill((0, 255, 0))

    if xs[0] < 0 or xs[0] > width - block_size or ys[0] < 0 or ys[0] > width - block_size:
        die(s, score)
        return False
    i = len(xs) - 1
    while i >= 1:
        xs[i] = xs[i - 1]
        ys[i] = ys[i - 1]
        i -= 1

    if dirs == 0:
        ys[0] += block_size
    elif dirs == 1:
        xs[0] += block_size
    elif dirs == 2:
        ys[0] -= block_size
    elif dirs == 3:
        xs[0] -= block_size
    s.fill((0, 0, 0))
    for i in range(0, len(xs)):
        s.blit(img, (xs[i], ys[i]))

    s.blit(appleimage, applepos)
    t = f.render(str(score), True, (255, 255, 255))
    s.blit(t, (10, 10))
    pygame.display.update()
    return True


if __name__ == '__main__':
    try:
        setup()
        while loop():
            pass
        quit()
    except KeyboardInterrupt:
        quit()
