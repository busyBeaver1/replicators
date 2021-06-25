import params as pr, cv2, numba, numpy, os

nWorld = pr.nWorld
if nWorld < 0:
    f = open(os.path.dirname(os.path.abspath(__file__)) + '/cache/N')
    nWorld = int(f.read())
    f.close()
    f = open(os.path.dirname(os.path.abspath(__file__)) + '/cache/N', 'w')
    f.write(str(nWorld + 1))
    f.close()
if pr.lang == 'rus': print('номер запуска: ' + str(nWorld) + '\n')
if pr.lang == 'eng': print('world number: ' + str(nWorld) + '\n')

nScreenshot = 0
nState = 0


def read(v):
    from functions import nParams
    nWorld = v[0]
    assert nWorld >= 0
    nState = v[1]
    if nState < 0:
        f = open(os.path.dirname(os.path.abspath(__file__)) + '/cache/N' + str(nWorld), 'r')
        nState = int(f.read())
        f.close()
    f = open(os.path.dirname(os.path.abspath(__file__)) + '/cache/state_world-' + str(nWorld) + '-' + str(nState) + '_world', 'rb')
    world = numpy.array(numpy.frombuffer(f.read(), dtype=pr.dtype).reshape(pr.width, pr.height, nParams + pr.genomeLength + pr.privateMemory + pr.publicMemory))
    f.close()
    f = open(os.path.dirname(os.path.abspath(__file__)) + '/cache/state_world-' + str(nWorld) + '-' + str(nState) + '_i')
    i = int(f.read())
    f.close()
    return world, i


def start():
    global videowriter
    videowriter = cv2.VideoWriter(os.path.dirname(os.path.abspath(__file__)) + '/output/world-' + str(nWorld) + '_video-' + str(nState) + '.' + pr.videoFormat, cv2.VideoWriter_fourcc(*pr.videoCodec), pr.fps, (pr.width, pr.height + pr.infoHeight))
    # если здесь произойдёт ошибка, попробуйте изменить параметр videoCodec на 'H264' или на какой-то другой кодек. | if some error occurred here, try changing videoCodec param to 'H264' or to some other codec.


def screenshot(screen):
    global nScreenshot
    fname = os.path.dirname(os.path.abspath(__file__)) + '/output/world-' + str(nWorld) + '_screenshot-' + str(nScreenshot) + '.png'
    nScreenshot += 1
    cv2.imwrite(fname, screen)
    if pr.lang == 'rus': print('скиншот сохранён в "' + fname + '"\n')
    if pr.lang == 'eng': print('screenshot saved to "' + fname + '"\n')
    return fname


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
        if pr.typeMicrobeVisual == 1: return (128 + dot[5] * 127 // pr.microbeMaxMinerals, 128 + dot[4] * 127 // pr.microbeMaxEnergy, 255 - 127 * pr.kVisualAge // (dot[6] + pr.kVisualAge))
        elif pr.typeMicrobeVisual == 2: return (dot[10], dot[11], dot[12])
    elif dot[0] == 2:
        return (127, 127, 127)
    elif dot[0] == 3:
        return (0, 80, 160)
    else: raise ValueError


def info(screen, ln, sps, kPopulate, avAge, light, water, season, step):
    screen[pr.height:] = 0
    n = 4
    cv2.putText(screen, 'video time, sec: ' + str(ln)[:str(ln).index('.')+3], (pr.infoHeight // 2                                      , pr.height + int(pr.infoHeight * .4)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'steps per sec: ' + str(sps)[:str(sps).index('.')+3], (pr.infoHeight // 2                                      , pr.height + int(pr.infoHeight * .8)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'populate: ' + str(int(kPopulate * 100.)) + '%'     , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n    , pr.height + int(pr.infoHeight * .4)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'average age: ' + str(avAge)                        , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n    , pr.height + int(pr.infoHeight * .8)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'light: ' + str(int(light * 100.)) + '%'            , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n * 2, pr.height + int(pr.infoHeight * .4)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'water: ' + str(int(water * 100.)) + '%'            , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n * 2, pr.height + int(pr.infoHeight * .8)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'season: ' + season                                 , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n * 3, pr.height + int(pr.infoHeight * .4)), pr.textFont, pr.textScale, (255, 255, 255))
    cv2.putText(screen, 'timestep: ' + str(step)                            , (pr.infoHeight // 2 + (pr.width - pr.infoHeight) // n * 3, pr.height + int(pr.infoHeight * .8)), pr.textFont, pr.textScale, (255, 255, 255))


def save(world, i):
    f = open(os.path.dirname(os.path.abspath(__file__)) + '/cache/state_world-' + str(nWorld) + '-' + str(nState) + '_world', 'wb')
    f.write(world.tobytes())
    f.close()
    f = open(os.path.dirname(os.path.abspath(__file__)) + '/cache/state_world-' + str(nWorld) + '-' + str(nState) + '_i', 'w')
    f.write(str(i))
    f.close()
    f = open(os.path.dirname(os.path.abspath(__file__)) + '/cache/N' + str(nWorld), 'w')
    f.write(str(nState))
    f.close()
