This is a simulation of evolution. Detailed description is in Replicators_description_eng.docx file (it will be added later) or in Replicators_description_rus.docx file (it is written in Russian) and here: https://www.youtube.com/playlist?list=PLOAbO557-ElocHFFmgSa2SwQOpSmzVUoN

The program runs on Python 3.
For the program to work, you need to install the OpenCV, Pygame and Numba libraries.

To start the program, run the main.py file using the "python main.py" command or "python3 main.py", depending on how Python is installed.
In the params.py file you can customize settings.

To stop the program correctly, close its window.
The saved videos and pictures will be in the "output" folder.

Management:
To get information about the cell, click on it.
Clicking on the field with additional information will create a screenshot.

How maps work:
Maps are located in the "maps" folder. The name of the map file to use is specified in the settings. On the map, the blue color indicates water, and the red color indicates obstacles.

How saving works:
Each program launch (each world) has a number. It affects the names of the saved files. For example, the video file name is arranged as follows: world-< launch number>_video-< video piece number>.avi. The number of world is specified in the settings (the nWorld parameter).
Saving occurs automatically after the number of steps specified in the settings (the stepsPerSave parameter, if less than zero, then do not save), and after stopping program. The state of the world is being saved to the "cache" folder and a file with a piece of video is being released, after which the recording of the next piece begins.
To use the saved state, change the "readFrom" parameter. The first number in it is the number of the world of which the state was saved (if this number is less than zero, the state is not read, but a new world is created). The second number is the number of state to be read (the piece of video from which you need to start recalculating). If the second number is less than zero, then the last saved state of that world is taken.
If the state files take up too much memory, then they can be deleted from the "cache" folder (all files except N) the world number is stored in N, so do not delete it, otherwise there will be an error.

############################################################

Это симуляция зволюции. Подробное описание в файле Replicators_description_rus.docx и здесь: https://www.youtube.com/playlist?list=PLOAbO557-ElocHFFmgSa2SwQOpSmzVUoN

Программа работает на Python 3.
Для работы программы необходимо установить библиотеки OpenCV, Pygame и Numba.

Чтобы запустить программу, запустите файл main.py с помощью команды "python main.py" или "python3 main.py", в зависимости от того, как установлен Python.
В файле params.py можно поменять настройки.

Чтобы правильно остановить программу, закройте её окно.
Cохранённые видео и картинки будут в папке output.

Управление:
Чтобы получить инфомацию о клетке, нажмите не неё. Нажатие на поле с дополнительной информацией приведёт к созданию снимка экрана.

Как работают карты:
Карты лежат в папке maps. Имя файла карты, которую надо использовать, указывается в настройках. На карте синий цвет указывает влажность, а красный - наличие стены.

Как работает сохранение:
У каждого запуска программы (у каждого мира) есть номер. Он влияет на названия сохраняемых файлов. Например, имя файла видео устроено так: world-<номер запуска>_video-<номер куска видео>.avi. Номер запуска указывается в настройках (параметр nWorld).
Сохранение происходит автоматически через число шагов, указанное в настройках (параметр stepsPerSave, если меньше ноля, то не сохранять), а также после остановки. Cостояние мира сохраняется в папку cache и высвобождается файл с куском видео, после чего начинается запись следующего куска.
Чтобы использовать сохранённое состояние, измените параметр readFrom. Первое число в нём - это номер запуска, при котором было сохранено состояние (если число меньше ноля, то состояние не считывается, а создаётся новый мир). Второе число - это номер состояния (куска видео, с которого нужно начать перерассчитывать). Если второе число меньше ноля, то берётся последнее сохранённое в том запуске состояние.
Если файлы состояний занимают слишком много памяти, то их можно удалять из папки cache (все файлы кроме N) в N сохраняется номер запуска, его удалять не надо, иначе будет ошибка.


#################### links ####################

GitHub repository - https://github.com/busyBeaver1/replicators
NotABug repository - https://notabug.org/busyBeaver/replicators
