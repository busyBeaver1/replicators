import numpy, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ''
from time import time
import params as pr, writer, pygame
from functions import *


mapWater = pr.map[..., 0] * pr.maxWater // 255
if pr.readFrom[0] < 0:
    world = numpy.zeros((pr.width, pr.height, nParams + pr.genomeLength + pr.privateMemory + pr.publicMemory), dtype=pr.dtype)
    world[pr.map[..., 2] > 127, 0] = 3
    world[(*pr.firstMicrobeCoord, 0)] = 1
    world[(*pr.firstMicrobeCoord, 4)] = 200
    world[(*pr.firstMicrobeCoord,)][10:13] = (192, 192, 192)
    world[(*pr.firstMicrobeCoord,)][nParams: nParams + pr.genomeLength] = pr.firstMicrobeGenome
else:
    world, i = writer.read(pr.readFrom)


#параметры клетки поля: 0 - тип|1 - свет|2 - минералы|3 - вода
#cell params: 0 - type|1 - light|2 - minerals|3 - water

#параметры микроба: 4 - энергия|5 - минералы|6 - возраст|7 - УТК|8 - расчитан|9 - направление|10 - цвет:красный|11 - цвет:зелёный|12 - цвет:синий
#microbe perams: 4 - energy|5 - minerals|6 - age|7 - program counter|8 - is calculated on this timestep|10 - color:red|11 - color:green|12 - color:blue

#тип клетки: 0 - пустой|1 - микроб|2 - органика|3 - стена
#cell type: 0 - empty|1 - microbe|2 - organics|3 - obstacle

screen = numpy.ndarray((pr.height + pr.infoHeight, pr.width, 3), dtype='uint8')
pygame.init()
pygame.display.set_caption('replicators')
pygame.display.set_icon(pygame.image.load('icon.png'))
display = pygame.display.set_mode((int(pr.width * pr.viewScale), int((pr.height + pr.infoHeight) * pr.viewScale)),)

def addRandCells(n):
    for i in range(n):
        x = randrange(pr.width)
        y = randrange(pr.height)
        world[x, y, 0] = 1
        world[x, y, 4: 10] = [pr.microbeMaxEnergy // 2, 0, 0, 0, 0, 0]
        for g in range(pr.genomeLength):
            world[x, y, g + nParams] = randrange(pr.genomeLength)


def stop():
    writer.save(world, i)
    writer.videowriter.release()
    if pr.lang == 'rus': print('время расчёта:', int(time() - t), 'секунд')
    if pr.lang == 'eng': print('simulating time:', int(time() - t), 'seconds')
    return exit


def save():
    writer.save(world, i)
    writer.videowriter.release()
    writer.nState += 1
    writer.start()
    if pr.lang == 'rus': print('сохранено состояние ' + str(writer.nState) + '\n')
    if pr.lang == 'eng': print('state ' + str(writer.nState) + ' saved\n')
    return writer.nState


def screenshot():
    return writer.screenshot(screen)


def info_rus(x, y):
    s = 'тип: ' + ('пусто', 'живой микроб', 'органика', 'стена')[world[x, y, 0]] + '.\n'
    if world[x, y, 0] != 3: s += 'свойства среды: свет:' + str(world[x, y, 1]) + '; минералы:' + str(world[x, y, 2]) + '; вода:' + str(world[x, y, 3]) + '.\n'
    if world[x, y, 0] == 1:
        s += 'свойства микроба: энергия:' + str(world[x, y, 4]) + '; минералы:' + str(world[x, y, 5]) + '; возраст:' + str(world[x, y, 6]) + '; УТК:' + str(world[x, y, 7]) + '; направление:' + str(world[x, y, 9])
        if pr.typeMicrobeVisual == 2: s += '; цвет(RGB):(' + str(world[x, y, 12]) + ', ' + str(world[x, y, 11]) + ', ' + str(world[x, y, 10]) + ')'
        s += '.\n'
    if world[x, y, 0] in (1, 2): s += 'геном: ' + str(list(world[x, y, nParams:nParams+pr.genomeLength])) + '\nпамять: ' + str(list(world[x, y, nParams+pr.genomeLength:])) + '\n'
    return s


def info_eng(x, y):
    s = 'type: ' + ('empty', 'alive microbe', 'organics', 'obstacle')[world[x, y, 0]] + '.\n'
    if world[x, y, 0] != 3: s += 'environment properties: light:' + str(world[x, y, 1]) + '; minerals:' + str(world[x, y, 2]) + '; water:' + str(world[x, y, 3]) + '.\n'
    if world[x, y, 0] == 1:
        s += 'microbe properties: energy:' + str(world[x, y, 4]) + '; minerals:' + str(world[x, y, 5]) + '; age:' + str(world[x, y, 6]) + '; program counter:' + str(world[x, y, 7]) + '; rotation:' + str(world[x, y, 9])
        if pr.typeMicrobeVisual == 2: s += '; color(RGB):(' + str(world[x, y, 12]) + ', ' + str(world[x, y, 11]) + ', ' + str(world[x, y, 10]) + ')'
        s += '.\n'
    if world[x, y, 0] in (1, 2): s += 'genome: ' + str(list(world[x, y, nParams:nParams+pr.genomeLength])) + '\nmemory: ' + str(list(world[x, y, nParams+pr.genomeLength:])) + '\n'
    return s


def info(x, y):
    if pr.lang == 'rus': return info_rus(x, y)
    if pr.lang == 'eng': return info_eng(x, y)


if __name__ == '__main__':
    t = time()

    writer.start()

    try: i = i
    except: i = 0
    fps = 0.
    tt = 0
    while True:
        tik = time()
        w = getWeather(i)

        world[..., 3] = mapWater * w[1]
        minerals(world)
        light(world, w[0])
        ret = step(world)

        if i % pr.stepsPerFrame == 0:
            writer.view(world, screen)
            writer.info(screen, i / pr.stepsPerVideoFrame / pr.fps, fps, ret[0], ret[1], w[0], w[1], w[2], i)

            surf = pygame.surfarray.make_surface(writer.scale_image(screen, pr.viewScale).transpose(1, 0, 2)[..., (2, 1, 0)])
            display.blit(surf, (0, 0))
            pygame.display.update()
            pass

        if i % pr.stepsPerVideoFrame == 0:
            writer.videowriter.write(writer.scale_image(screen, pr.videoScale))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop()
                exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if int(event.pos[1] / pr.viewScale) < pr.height:
                    print(info(int(event.pos[0] / pr.viewScale), int(event.pos[1] / pr.viewScale)))
                else:
                    screenshot()

        i += 1
        fps = 1. / (time() - tik)

        if i % pr.stepsPerSave == 0:
            save()
