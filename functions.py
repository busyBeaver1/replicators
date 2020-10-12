import params as pr
import numba, numpy
from random import randrange, random

nParams = 13
nGenes = 16

dirs = numpy.array([(0, -1, 0), (1, -1, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (-1, 1, 0), (-1, 0, 0), (-1, -1, 0)])


@numba.jit
def step(world): # запустить мир на шаг
    n = 0
    e = 0
    world[..., 8] = 0
    fx = randrange(pr.width)
    i = fx + pr.width
    while i != fx:
        i = (i + pr.prime) % pr.width
        fy = randrange(pr.height)
        j = fy + pr.height
        while j != fy:
            j = (j + pr.prime) % pr.height
            if world[i, j, 0] == 1:
                n += 1
                e += world[i, j, 6]
                go(world, i, j)
    return (n / (world.shape[0] * world.shape[1]), e // n)
    #      (доля заполнения мира                 , средний возраст)

_year = 0
for season in pr.seasons:
    _year += season[3] + season[4]

def getWeather(time):
    time %= _year
    t = 0
    for i in range(len(pr.seasons)):
        if t <= time < t + pr.seasons[i][3]:
            return pr.seasons[i][:3]
        elif time < t + pr.seasons[i][3] + pr.seasons[i][4]:
            if time < t + pr.seasons[i][3] + pr.seasons[i][4] // 2: s = i
            else: s = i + 1
            l = (pr.seasons[i][0] * (t + pr.seasons[i][3] + pr.seasons[i][4] - time) + pr.seasons[(i + 1) % len(pr.seasons)][0] * (time - t - pr.seasons[i][3])) / pr.seasons[i][4]
            w = (pr.seasons[i][1] * (t + pr.seasons[i][3] + pr.seasons[i][4] - time) + pr.seasons[(i + 1) % len(pr.seasons)][1] * (time - t - pr.seasons[i][3])) / pr.seasons[i][4]
            return (l, w, pr.seasons[s % len(pr.seasons)][2])
        t += pr.seasons[i][3] + pr.seasons[i][4]
    #      (свет, влажность, название сезона)


@numba.jit
def go(world, x, y): # запустить на шаг микроба с поля world по координатам (x, y)
    cell = world[x, y]
    
    if cell[8]: return
    cell[8] = 1
    
    cell[4] -= cell[3] * pr.kTimeEnergi // pr.maxWater
    
    if control(world, x, y) == -1: return
    
    if cell[6] == pr.maxAge: cell[0] = 2; return
    cell[6] += 1
    
    add = cell[2]
    if cell[5] + add > pr.cellMaxMinerals: add = pr.cellMaxMinerals - cell[5]
    cell[5] += add
    cell[2] -= add

    for n in range(pr.commandsPerStep):
        gene = cell[cell[7] + nParams] % nGenes
        
        if gene == 0: # безусловный переход (изменить УТК)
            cell[7] = cell[(cell[7] + 1) % pr.genomeLength + nParams]
        
        elif gene == 1: # повернуться на угол относительно бывшего направления
            cell[9] = (cell[9] + cell[(cell[7] + 1) % pr.genomeLength + nParams]) % dirs.shape[0]
            cell[7] = (cell[7] + 2) % pr.genomeLength
        
        elif gene == 2: # повернуться на угол относительно вертикали
            cell[9] = cell[(cell[7] + 1) % pr.genomeLength + nParams] % dirs.shape[0]
            cell[7] = (cell[7] + 2) % pr.genomeLength
        
        elif gene == 3: # передвинуться на один шаг
            d = dirs[(cell[9] + cell[(cell[7] + 1) % pr.genomeLength + nParams]) % dirs.shape[0]]
            x1 = x + d[0]; y1 = y + d[1]
            if 0 <= x1 < pr.width and 0 <= y1 < pr.height:
                if world[x1, y1, 0] == 0:
                    cell[7] = cell[(cell[7] + 3) % pr.genomeLength + nParams]
                    cell[4] -= (pr.maxWater - cell[3]) * pr.kGoEnergy // pr.maxWater
                    world[x1, y1, 4:] = cell[4:]
                    world[x1, y1, 0] = cell[0]
                    cell[0] = 0
                    if control(world, x1, y1) != 0: break
                    x = x1; y = y1
                    cell = world[x, y]
                else:
                    cell[7] = cell[(cell[7] + 2) % pr.genomeLength + nParams]
            else:
                cell[7] = cell[(cell[7] + 2) % pr.genomeLength + nParams]
        
        elif gene == 4: # фотосинтез
            cell[4] += cell[1]
            cell[7] = (cell[7] + 1) % pr.genomeLength
            control(world, x, y)
            break
        
        elif gene == 5: # минералы в энергию
            cell[4] += cell[5]
            cell[5] = 0
            cell[7] = (cell[7] + 1) % pr.genomeLength
            control(world, x, y)
            break
        
        elif gene == 6: # добыть минералы
            add = cell[2]
            if cell[5] + add > pr.cellMaxMinerals: add = pr.cellMaxMinerals - cell[5]
            cell[5] += add
            cell[2] -= add
            cell[7] = (cell[7] + 1) % pr.genomeLength
            break
        
        elif gene == 7: # сосчитать пустые клетки вокруг
            n = 0
            for d in dirs:
                if 0 <= x + d[0] < pr.width and 0 <= y + d[1] < pr.height:
                    n += (world[x, y, 0] == 0)
            cell[7] = cell[(cell[7] + (n >= cell[(cell[7] + 1) % pr.genomeLength + nParams] % dirs.shape[0]) + 1) % pr.genomeLength + nParams]
        
        elif gene == 8: # посмотреть, что в клетке по определённому направлению
            d = dirs[(cell[9] + cell[(cell[7] + 1) % pr.genomeLength + nParams]) % dirs.shape[0]]
            x1 = x + d[0]; y1 = y + d[1]
            n = 2
            if (not 0 <= x1 < pr.width) or (not 0 <= y1 < pr.height): n = 2
            elif world[x1, y1, 0] == 0: n = 3
            elif world[x1, y1, 0] == 1:
                dif = 0
                for g in range(pr.genomeLength):
                    dif += world[x1, y1, nParams + g] != cell[nParams + g]
                n = 4 + (dif > pr.relativeMaxDif)
            elif world[x1, y1, 0] == 2: n = 6
            cell[7] = cell[(cell[7] + n) % pr.genomeLength + nParams]
        
        elif gene == 9: # съесть то, что в клетке по определённому направлению
            d = dirs[(cell[9] + cell[(cell[7] + 1) % pr.genomeLength + nParams]) % dirs.shape[0]]
            x1 = x + d[0]; y1 = y + d[1]
            if 0 <= x1 < pr.width and 0 <= y1 < pr.height:
                if world[x1, y1, 0] == 2:
                    cell[7] = cell[(cell[7] + 3) % pr.genomeLength + nParams]
                    cell[4] += pr.organicsEnergy
                    control(world, x, y)
                    world[x1, y1, 0] = 0
                elif world[x1, y1, 0] == 1:
                    cell[7] = cell[(cell[7] + 4) % pr.genomeLength + nParams]
                    if cell[4] + world[x1, y1, 4] - pr.attackEnergy >= 0:
                        cell[4] += world[x1, y1, 4] - pr.attackEnergy
                        if pr.eatMinerals:
                            cell[5] += world[x1, y1, 5]
                            if cell[5] > pr.cellMaxMinerals: cell[5] = pr.cellMaxMinerals
                        control(world, x, y)
                        world[x1, y1, 0] = 0
                    else:
                        cell[0] = 2
                else:
                    cell[7] = cell[(cell[7] + 2) % pr.genomeLength + nParams]
            else:
                cell[7] = cell[(cell[7] + 2) % pr.genomeLength + nParams]
            break
        
        elif gene == 10: # узнать свою энергию
            cell[7] = cell[(cell[7] + (cell[4] * pr.genomeLength > cell[(cell[7] + 1) % pr.genomeLength + nParams] * pr.cellMaxEnergy) + 2) % pr.genomeLength + nParams]
        
        elif gene == 11: # узнать свет
            cell[7] = cell[(cell[7] + (cell[1] * pr.genomeLength > cell[(cell[7] + 1) % pr.genomeLength + nParams] * pr.maxLight) + 2) % pr.genomeLength + nParams]
        
        elif gene == 12: # узнать влажность
            cell[7] = cell[(cell[7] + (cell[3] * pr.genomeLength > cell[(cell[7] + 1) % pr.genomeLength + nParams] * pr.maxWater) + 2) % pr.genomeLength + nParams]
        
        elif gene == 13: # узнать возраст
            cell[7] = cell[(cell[7] + (cell[6] > cell[(cell[7] + 1) % pr.genomeLength + nParams]) + 2) % pr.genomeLength + nParams]

        elif gene == 14: # записать в свою память
            cell[nParams + pr.genomeLength + cell[(cell[7] + 1) % pr.genomeLength + nParams] % pr.privateMemory] = cell[(cell[7] + 2) % pr.genomeLength + nParams] % 2
            cell[7] = (cell[7] + 3) % pr.genomeLength + nParams
        
        elif gene == 15: # записать в публичную память
            m = nParams + pr.genomeLength + pr.privateMemory + cell[(cell[7] + 1) % pr.genomeLength + nParams] % pr.publicMemory
            v = cell[(cell[7] + 2) % pr.genomeLength + nParams] % 2
            cell[m] = v
            for x1, y1, _ in dirs:
                if 0 <= x + x1 < pr.width and 0 <= y + y1 < pr.height:
                    if world[x + x1, y + y1, 0] == 1:
                        world[x + x1, y + y1, m] = v
            cell[7] = cell[(cell[7] + 3) % pr.genomeLength + nParams]
        
        elif gene == 16: # прочитать из памяти
            cell[7] = cell[(cell[7] + 2 + cell[nParams + pr.genomeLength + cell[(cell[7] + 1) % pr.genomeLength + nParams] % (pr.privateMemory + pr.publicMemory)]) % pr.genomeLength + nParams]


@numba.jit
def control(world, x, y):
    if world[x, y, 4] < 0:
        world[x, y, 0] = 2
        return -1
    if world[x, y, 4] > pr.cellMaxEnergy:
        world[x, y, 4] = pr.cellMaxEnergy
        return replicate(world, x, y)
    return 0


@numba.jit
def replicate(world, x, y):
    c = getEmptyCell(world, x, y)
    if c[0] == -1:
        if pr.replicateDie: world[x, y, 0] = 2; return -1
        return 0
    world[x, y, 4] = (world[x, y, 4] - pr.replicateEnergy) // 2
    world[x, y, 5] //= 2
    world[c[0], c[1], 4:nParams] = world[x, y, 4:nParams]
    world[c[0], c[1], 0] = 1
    world[c[0], c[1], 6] = 0
    world[c[0], c[1], 7] = 0
    world[c[0], c[1], nParams+pr.genomeLength:] = 0
    for i in range(pr.genomeLength):
        if random() < pr.mutProb:
            world[c[0], c[1], i + nParams] = randrange(pr.genomeLength)
            n = randrange(3)
            world[c[0], c[1], 10 + n] += randrange(pr.colorChange * 2 + 1) - pr.colorChange
            if world[c[0], c[1], 10 + n] < 128: world[c[0], c[1], 10 + n] = 128
            if world[c[0], c[1], 10 + n] > 255: world[c[0], c[1], 10 + n] = 255
        else:
            world[c[0], c[1], i + nParams] = world[x, y, i + nParams]
    return 1


@numba.jit
def getEmptyCell(world, x, y):
    d = numpy.copy(dirs)
    for i in range(dirs.shape[0]):
        f = randrange(dirs.shape[0])
        while d[f, 2]: f = randrange(dirs.shape[0])
        d[f, 2] = 1
        if (not 0 <= x + d[f, 0] < pr.width) or (not 0 <= y + d[f, 1] < pr.height): continue
        if world[x + d[f, 0], y + d[f, 1], 0] == 0:
            return (x + d[f, 0], y + d[f, 1])
    return (-1, -1)


@numba.jit
def light(world, k):
    for i in range(pr.width):
        light = float(pr.maxLight) * k
        for j in range(pr.height):
            world[i, j, 1] = light
            if world[i, j, 0] == 0:
                light *= pr.lightTransp
            else:
                light *= pr.lightTranspCell


@numba.jit
def minerals(world):
    for i in range(pr.width):
        for j in range(pr.height):
            if world[i, j, 2] < world[i, j, 3]:
                world[i, j, 2] += pr.mineralsAddition
                if world[i, j, 2] > world[i, j, 3]:
                    world[i, j, 2] = world[i, j, 3]
