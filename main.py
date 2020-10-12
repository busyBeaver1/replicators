import cv2, numpy, threading, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ''
from time import time
import params as pr, writer, pygame
from functions import *


mapWater = pr.map[..., 0] * pr.maxWater // 255
if pr.readFrom[0] < 0:
    world = numpy.zeros((pr.width, pr.height, nParams + pr.genomeLength + pr.privateMemory + pr.publicMemory), dtype=pr.dtype)
    world[pr.map[..., 2] > 127, 0] = 3
    world[pr.width // 2, pr.height // 4, 0] = 1
    world[pr.width // 2, pr.height // 4, 4] = 200
    world[pr.width // 2, pr.height // 4, 10:13] = (192, 192, 192)
    world[pr.width // 2, pr.height // 4, nParams:nParams+3] = (4, 0, 0)
else:
    world, i = writer.read(pr.readFrom)


#параметры клетки поля: 0 - тип|1 - свет|2 - минералы|3 - вода
#параметры микроба: 4 - енергия|5 - минералы|6 - возраст|7 - УТК|8 - расчитан|9 - направление|10 - цвет:красный|11 - цвет:зелёный|12 - цвет:синий
#тип: 0 - пустой|1 - живой|2 - мёртвый|3 - стена

screen = numpy.ndarray((pr.height + pr.infoHeight, pr.width, 3), dtype='uint8')
pygame.init()
pygame.display.set_caption('replicators')
display = pygame.display.set_mode((pr.width, pr.height + pr.infoHeight))

def addRandCells(n):
    for i in range(n):
        x = randrange(pr.width)
        y = randrange(pr.height)
        world[x, y, 0] = 1
        world[x, y, 4: 10] = [pr.cellMaxEnergy // 2, 0, 0, 0, 0, 0]
        for g in range(pr.genomeLength):
            world[x, y, g + nParams] = randrange(pr.genomeLength)


def stop():
    writer.save(world, i)
    writer.videowriter.release()
    print('время расчёта:', int(time() - t), 'секунд')
    return exit


def save():
    writer.save(world, i)
    writer.videowriter.release()
    writer.nState += 1
    writer.start()
    return 'сохранено состояние ' + str(writer.nState) + '\n'


def screenshot():
    return writer.screenshot(screen)


def info(x, y):
    s = 'тип: ' + ('пусто', 'живой микроб', 'органика', 'стена')[world[x, y, 0]] + '.\n'
    if world[x, y, 0] != 3: s += 'свойства среды: свет:' + str(world[x, y, 1]) + '; минералы:' + str(world[x, y, 2]) + '; вода:' + str(world[x, y, 3]) + '.\n'
    if world[x, y, 0] == 1:
        s += 'свойства микроба: энергия:' + str(world[x, y, 4]) + '; минералы:' + str(world[x, y, 5]) + '; возраст:' + str(world[x, y, 6]) + '; УТК:' + str(world[x, y, 7]) + '; направление:' + str(world[x, y, 9])
        if pr.typeCellVisual == 2: s += '; цвет(RGB):(' + str(world[x, y, 12]) + ', ' + str(world[x, y, 11]) + ', ' + str(world[x, y, 10]) + ')'
        s += '.\n'
    if world[x, y, 0] in (1, 2): s += 'геном: ' + str(list(world[x, y, nParams:nParams+pr.genomeLength])) + '\nпамять: ' + str(list(world[x, y, nParams+pr.genomeLength:])) + '\n'
    return s


def _input():
    global command
    command = input()


if __name__ == '__main__':
    t = time()

    writer.start()

    try: i = i
    except: i = 0
    fps = 0.

    while True:
        tik = time()
        w = getWeather(i)

        world[..., 3] = mapWater * w[1]
        minerals(world)
        light(world, w[0])

        ret = step(world)

        writer.view(world, screen)
        writer.info(screen, i / pr.stepsPerFrame / pr.fps, fps, ret[0], ret[1], w[0], w[1], w[2], i)

        surf = pygame.surfarray.make_surface(screen.transpose(1, 0, 2)[..., (2, 1, 0)])
        display.blit(surf, (0, 0))
        pygame.display.update()

        if i % pr.stepsPerFrame == 0:
            writer.videowriter.write(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop()
                exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if event.pos[1] < pr.height:
                    print(info(*event.pos))
                else:
                    print(screenshot())

        
        i += 1
        fps = 1. / (time() - tik)

        if i % pr.stepsPerSave == 0:
            print(save())
