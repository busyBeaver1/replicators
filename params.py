import cv2

dtype = 'int32'

map = cv2.imread('maps/map4.png').transpose(1, 0, 2).astype(dtype) # 'maps/map4.png' - имя файла картинки с картой
                                                                   # 'maps/map4.png' - name of file with map image 
width, height = map.shape[:2]
seasons = [(.6, 1., 'spring', 8000, 3000), (1., .6, 'summer', 12000, 3000), (.6, .8, 'autumn', 8000, 3000), (.3, .15, 'winter', 18000, 3000)]
          # сезоны. Структура сезона: (доля света (от максимального), доля влажности, название, длительность, длительность плавного перехода условий к следующему сезону)
          # seasons. Season structure: (percentage of light (of maximal), percentage of water, name, duration, duration of smooth transition to the next season)
maxLight = 120 # максимальный свет (сверху) | maximal light (on the top of the world)
lightTranspMicrobe = .994 # коэффициент прозрачности микроба | transparency coefficient of cell with a microbe on it
lightTransp = .997 # коэффициент прозрачности пустой клетки | transparency coefficient of empty cell
maxWater = 120 # максимальная влажность на поле | maximal water level

genomeLength = 80 # количество чисел в геноме микроба | number of numbers (genes) in genome
firstMicrobeCoord = (width // 2, height // 4) # координаты первого микроба (x, y) | first microbe coordinates (x, y)
firstMicrobeGenome = [4, 0, 0] # начало генома первого микроба | starting of first microbe's genome
firstMicrobeGenome += [0 for _ in range(genomeLength - len(firstMicrobeGenome))] # эта строка дописывает к геному первого микроба столько нолей, чтобы он стал длиной genomeLength
                                                                                 # this line adds zeros to first microbe's genome to make its length equal to genomeLength 
microbeMaxMinerals = 400 # максимальное количество минералов микроба | maximal amount of microbe's minerals
microbeMaxEnergy = 1400 # максимальная энергия микроба (при достижении её микробы размножается) | maximal microbe energy (after reaching it microbes replicate)
mineralsAddition = 20 # скорость добавления минералов на клетке если их меньше чем влажность | speed of adding minerals on cell if there is less minerals than water
kTimeEnergy = 20 # коэффициент убавления энергии за один (временной) ход (вычисляется как kTimeEnergy * влажность / maxWater)
                 # coefficient of energy loss over each timestep (loss is counted as kTimeEnergy * water / maxWater)
mutProb = 0.003 # вероятность мутации (для отдельного гена) | mutation probability (for 1 number in genome)
replicateEnergy = 200 # энергия, отнимающияся при размножении | energy loss wile replicating
kGoEnergy = 35 # коэффициент убавления энергии за передвижение (вычисляется как kGoEnergy * (maxWater - влажность) / maxWater) | energy lossing in move. Loss is counted as kGoEnergy * (maxWater - water) / maxWater
relativeMaxDif = 2 # максимальная разница геномов двух микробов, при которой они считаются родственниками | maximale difference between microbe genomes to count them as relatives
organicsEnergy = 200 # энергия от съедания органики | energy of eating 1 organics cell
attackEnergy = 320 # энергия, отнимающияся при атаке микроба | energy loosing in attack
kMineralsIntake = 3 # коэффициент автоматического "вбирания" минералов (вычисляется как минералы / kMineralsIntake) | coefficient of automatic "intaking" minerals. Intaking is calculated as minerals / kMineralsIntake
replicateDie = True # умереть, если энергия > microbeMaxEnergy, но размножиться невозможно т. к. микроб окружён | die if energy > microbeMaxEnergy and there is no empty cell around, so replicating is impossible
maxAge = -1 # максимальный возраст (при достижении его микроб умрёт) если меньше 0, то возраст неограничен | maximal age (microbe will die after reaching it), if less than 0 - age is not limited
commandsPerStep = 4 # максимальное число незавершаюших команд | maximal number of not finalising commands
privateMemory = 3 # биты своей памяти микроба | bits of microbe's "own" memory
publicMemory = 3 # биты "публичной" памяти микроба | bits of "public" microbe's memory
eatMinerals = False # если один микроб съел другого, перейдут ли к нему минералы, или только энергия.
                    # if one microbe eat other, will it have his minerals, or energy only

prime = 1000000000039
nWorld = -1 # номер запуска программы (для имён файлов). Если меньше 0 - то используется следующий после предидущего запуска.
            # world number (for file names). If less than 0 - next number after previous world number
readFrom = (-1, -1) # откуда считать состояние мира, первое число - номер запуска (если меньше 0, то созадать новый мир), второе число - номер сохранённого состояния (если меньше ноля, то последнее)
                    # where to get start world state, first number - saved world number (if less than 0 - make new world), second number - saved state number (if less than 0 - last saved state)
stepsPerSave = 144000 # через сколько шагов сохранять состояние (если меньше 0, то не сохранять вообще) | how many steps will be done before saving world state (if less than 0 - no saves)

viewScale = 1. # маштаб предпросмотра (во сколько раз будет растянуто изображение) | preview scale
fps = 30. # fps видео | video fps
videoCodec = 'DIVX' # Название кодека видео для передачи в функцию OpenCV cv2.VideoWriter_fourcc | name of video codec to give it to OpenCV's cv2.VideoWriter_fourcc function
videoFormat = 'avi' # формат видео | video format
stepsPerVideoFrame = 16 # через сколько шагов кадр записывается в видео | how many steps will be done before writing new frame to video file
stepsPerFrame = 1 # через сколько шагов кадр бодет нарисован | how many steps will be done before drawing new frame
typeMicrobeVisual = 1 # способ отображения микробов, 1 или 2 | method of viewing microbes, 1 or 2
colorChange = 6 # скорость мутирования цвета (для 2-го способа отображения микробов) | speed of color mutating (for 2-nd method of viewing microbes)
kVisualAge = 150 # от этого параметра зависит скорость покраснения клетки от возроста (для 1-го способа отображения микробов) | speed of microbe getting red with age (for 1-st method of viewing microbes)
infoHeight = 60 # высота поля с дополнительной информацией (в пикселях) | height of the field with additional information (in pixels)
textScale = 1.2 # размер текста | text scale
textFont = cv2.FONT_HERSHEY_PLAIN # шрифт | font
lang = 'eng' # язык | language
             # варианты|variants: 'rus', 'eng'
