import params as pr, cv2, numba, numpy

nWorld = pr.nWorld
if nWorld < 0:
    f = open('./cache/N')
    nWorld = int(f.read())
    f.close()
    f = open('./cache/N', 'w')
    f.write(str(nWorld + 1))
    f.close()
print('номер запуска: ' + str(nWorld) + '\n')

nScreenshot = 0
nState = 0


def read(v):
    from functions import nParams
    nWorld = v[0]
    assert nWorld >= 0
    nState = v[1]
    if nState < 0:
        f = open('cache/N' + str(nWorld), 'r')
        nState = int(f.read())
        f.close()
    f = open('cache/state_world-' + str(nWorld) + '-' + str(nState) + '_world', 'rb')
    world = numpy.array(numpy.frombuffer(f.read(), dtype=pr.dtype).reshape(pr.width, pr.height, nParams + pr.genomeLength + pr.privateMemory + pr.publicMemory))
    f.close()
    f = open('cache/state_world-' + str(nWorld) + '-' + str(nState) + '_i')
    i = int(f.read())
    f.close()
    return world, i


def start():
    global videowriter
    videowriter = cv2.VideoWriter('./output/world-' + str(nWorld) + '_video-' + str(nState) + '.avi', cv2.VideoWriter_fourcc(*'DIVX'), pr.fps, (pr.width, pr.height + pr.infoHeight))


def screenshot(screen):
    global nScreenshot
    fname = './output/world-' + str(nWorld) + '_screenshot-' + str(nScreenshot) + '.png'
    nScreenshot += 1
    cv2.imwrite(fname, screen)
    return 'saved as "' + fname + '"\n'


@numba.jit
def view(world, screen):
    for i in range(pr.width):
        for j in range(pr.height):
            screen[j, i] = getColor(world[i, j])


@numba.jit
def getColor(dot):
    if dot[0] == 0:
        return (dot[3] * 127 // pr.maxWater, dot[2] * 127 // pr.maxWater, dot[1] * 127 // pr.maxLight)
    elif dot[0] == 1:
        if pr.typeCellVisual == 1: return (128 + dot[5] * 127 // pr.cellMaxMinerals, 128 + dot[4] * 127 // pr.cellMaxEnergy, 255 - 127 * pr.kVisualAge // (dot[6] + pr.kVisualAge))
        elif pr.typeCellVisual == 2: return (dot[10], dot[11], dot[12])
    elif dot[0] == 2:
        return (127, 127, 127)
    else:
        return (0, 80, 160)


def info(screen, ln, fps, kPopulate, midAge, light, water, season, step):
    screen[pr.height:] = 0
    n = 4
    h = pr.height + pr.infoHeight // 2
    cv2.putText(screen, 'video time (sec): ' + str(ln)[:str(ln).index('.')+3], (pr.infoHeight // 2, pr.height + int(pr.infoHeight * .4))                                      , pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'fps: ' + str(fps)[:str(fps).index('.')+3]           , (pr.infoHeight // 2, pr.height + int(pr.infoHeight * .8))                                      , pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'populate: ' + str(int(kPopulate * 100.)) + '%'      , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n, pr.height + int(pr.infoHeight * .4))    , pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'mid age: ' + str(midAge)                            , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n, pr.height + int(pr.infoHeight * .8))    , pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'light: ' + str(int(light * 100.)) + '%'             , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n * 2, pr.height + int(pr.infoHeight * .4)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'water: ' + str(int(water * 100.)) + '%'             , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n * 2, pr.height + int(pr.infoHeight * .8)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'season: ' + season                                  , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n * 3, pr.height + int(pr.infoHeight * .4)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'step: ' + str(step)                                 , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n * 3, pr.height + int(pr.infoHeight * .8)), pr.textFont, pr.textScale, (255, 255, 255))


def save(world, i):
    f = open('cache/state_world-' + str(nWorld) + '-' + str(nState) + '_world', 'wb')
    f.write(world.tobytes())
    f.close()
    f = open('cache/state_world-' + str(nWorld) + '-' + str(nState) + '_i', 'w')
    f.write(str(i))
    f.close()
    f = open('cache/N' + str(nWorld), 'w')
    f.write(str(nState))
    f.close()
