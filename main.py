from tkinter import *
from tkinter import messagebox as tkmessbox
import random
from collections import *
from datetime import *
import cfg
import os


cols = 10
rows = 10
mines = 10


class MineSweeper:

    def __init__(self, tk, cols, rows, mines):

        # определение размеров поля и нахождение на клетке мины и инициализация окна
        self.isMine = False
        self.cols = cols
        self.rows = rows
        self.mines = mines
        self.ask = ask

        # import изображений
        self.textures = {
            'empty': PhotoImage(file='images/plain.gif'),
            "clicked": PhotoImage(file="images/clicked.gif"),
            "mine": PhotoImage(file="images/mine.gif"),
            "flag": PhotoImage(file="images/flag.gif"),
            "wrong": PhotoImage(file="images/wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.textures['numbers'].append(PhotoImage(file='images/tile_'+str(i)+'.gif'))

        # настройка окна игры
        self.tk = Toplevel(tk)
        self.tk.resizable(False, False)
        self.frame = Frame(self.tk)
        self.frame.grid(row=1, column=0)
        self.x = (self.tk.winfo_screenwidth() - self.tk.winfo_reqwidth()) / 2
        self.y = (self.tk.winfo_screenheight() - self.tk.winfo_reqheight()) / 2
        self.tk.wm_geometry("+%d+%d" % (self.x, self.y))
        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "mines": Label(self.frame, text="Mines: 0"),
            "flags": Label(self.frame, text="Flags: 0")
        }

        self.labels["time"].grid(row=0, column=0, columnspan=self.cols)
        self.labels["mines"].grid(row=self.rows + 1, column=0, columnspan=int(self.cols / 2))
        self.labels["flags"].grid(row=self.rows + 1, column=int(self.cols/2) - 1, columnspan=int(self.cols/2))
        # инициализация меню
        self.menubar = Menu(self.tk)
        self.tk.config(menu=self.menubar)
        self.menubar.add_command(label='Сложность', command=lambda: self.tk.destroy())
        self.menubar.add_command(label='Справка', command=helpButton)
        self.menubar.add_separator()
        self.menubar.add_command(label='Выход', command=self.quitAll)
        self.tk.iconbitmap('images/window_icon.ico')

        self.restart()  # начать игру
        self.updateTimer()  # инициализация таймера
        self.grab_focus()  # grabbing focus к дочернему окну self.tk

    def setup(self):
        # создаем необходимые переменные для игры
        self.flagCount = 0
        self.CorrectFlagCount = 0
        self.clickedCount = 0
        self.startTime = None

        # создание поля(словарь кнопок)
        self.tiles=dict({})
        self.mines = 0
        for x in range(0, self.rows):
            for y in range(0, self.cols):
                if y == 0:
                    self.tiles[x] = {}
                id = str(x) + '_' + str(y)
                isMine = False

                gfx = self.textures["empty"]

                if random.uniform(0.0, 1.0) < 0.1:
                    isMine = True

                tile = {
                    'id': id,
                    'isMine': isMine,
                    'state': cfg.STATE_DEFAULT,
                    'coords': {
                        'x': x,
                        'y': y
                    },
                    'button': Button(self.frame, image=gfx),
                    'mines': 0  # get from args
                }
                tile["button"].bind(cfg.BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(cfg.BTN_FLAG, self.onRightClickWrapper(x, y))
                tile["button"].grid(row=x + 1, column=y)  # offset by 1 row for timer
                self.tiles[x][y] = tile

                # Новый цикл найти мины поблизости и отобразить их на кнопках
        for x in range(0, self.cols):
            for y in range(0, self.rows):
                mc = 0
                for i in self.getNeighbours(x, y):
                    mc += 1 if i['isMine'] else 0
                self.tiles[x][y]['mines'] = mc

    def restart(self):
        self.setup()
        self.refreshLabels()

    def refreshLabels(self):
        self.labels['flags'].config(text='flags: ' + str(self.flagCount))
        self.labels['mines'].config(text='Mines: ' + str(self.mines))

    def gameOver(self, state):
        for x in range(0, self.cols):
            for y in range(0, self.rows):
                if self.tiles[x][y]['isMine'] == False and self.tiles[x][y]['state'] == cfg.STATE_FLAGGED:
                    self.tiles[x][y]['button'].config(image=self.textures['wrong'])
                if self.tiles[x][y]['isMine'] == True and self.tiles[x][y]['state'] != cfg.STATE_FLAGGED:
                    self.tiles[x][y]['button'].config(image=self.textures['mine'])

        self.tk.update()

        msg = "You Win! Play again?" if state else "You Lose! Play again?"
        res = tkmessbox.askyesno("Game Over", msg)
        if res:
            self.restart()
        else:
            self.tk.destroy()

    def quitAll(self):
        self.tk.destroy()
        self.ask.destroy()

    def updateTimer(self):
        ts = '00:00:00'
        if self.startTime != None:
            delta = datetime.now() - self.startTime
            ts = str(delta).split('.')[0]
            if delta.total_seconds() < 36000:
                ts = '0' + ts  # zero-pad
        self.labels['time'].config(text=ts)
        self.frame.after(100, self.updateTimer)

    def getNeighbours(self, x, y):
        neighbours = []
        coords = [
            {"x": x - 1, "y": y - 1},  # top right
            {"x": x - 1, "y": y},  # top middle
            {"x": x - 1, "y": y + 1},  # top left
            {"x": x, "y": y - 1},  # left
            {"x": x, "y": y + 1},  # right
            {"x": x + 1, "y": y - 1},  # bottom right
            {"x": x + 1, "y": y},  # bottom middle
            {"x": x + 1, "y": y + 1},  # bottom left
        ]
        for i in coords:
            try:
                neighbours.append(self.tiles[i['x']][i['y']])
            except KeyError:
                pass
        return neighbours

    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])
        pass

    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    def onClick(self, tile):
        if self.startTime == None:  # start timer
            self.startTime = datetime.now()

        if tile["isMine"] == True:
            # end game
            self.gameOver(False)
            return
        if tile["mines"] == 0:
            tile["button"].config(image=self.textures["clicked"])
            self.clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(image=self.textures["numbers"][tile["mines"]-1])
        # if not already set as clicked, change state and count
        if tile["state"] != cfg.STATE_CLICKED:
            tile["state"] = cfg.STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (self.cols * self.rows) - self.mines:
            self.gameOver(True)

    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        if tile['state'] == cfg.STATE_DEFAULT:
            tile['button'].config(image=self.textures['flag'])
            tile['state'] = cfg.STATE_FLAGGED
            tile['button'].unbind(cfg.BTN_CLICK)

            # if a mine
            if tile['isMine'] == True:
                self.CorrectFlagCount += 1
            self.flagCount += 1
            self.refreshLabels()

            # if flagged, unFlag
        elif tile['state'] == 2:
            tile['button'].config(image=self.textures['empty'])
            tile['state'] = 0
            tile['button'].bind(cfg.BTN_CLICK, self.onClickWrapper(tile['coords']['x'], tile['coords']['y']))

            # if a mine
            if tile['isMine'] == True:
                self.CorrectFlagCount -= 1
            self.flagCount -= 1
            self.refreshLabels()

    def clearSurroundingTiles(self, id):
        queue = deque([id])
        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.getNeighbours(x, y):
                self.clearTile(tile, queue)

    def clearTile(self, tile, queue):
        if tile["state"] != cfg.STATE_DEFAULT:
            return

        if tile["mines"] == 0:
            tile["button"].config(image=self.textures["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(image=self.textures["numbers"][tile["mines"]-1])

        tile["state"] = cfg.STATE_CLICKED
        self.clickedCount += 1

    def grab_focus(self):
        self.tk.grab_set()
        self.tk.focus_set()
        self.tk.wait_window()


def easyChoice():
    global cols, rows, mines
    cols = 10
    rows = 10
    mines = 10
    mm = MineSweeper(ask, cols, rows, mines)


def mediumChoice():
    global cols, rows, mines
    cols = 18
    rows = 18
    mines = 36
    mm = MineSweeper(ask, cols, rows, mines)


def hardChoice():
    global cols, rows, mines
    cols = 24
    rows = 24
    mines = 48
    mm = MineSweeper(ask, cols, rows, mines)


def preWindow():
    global ask
    ask = Tk()
    ask.title('Minesweeper v. 1.0.0')
    ask.iconbitmap('images/window_icon.ico')
    ask.resizable(False, False)
    x = (ask.winfo_screenwidth() - ask.winfo_reqwidth()) / 2
    y = (ask.winfo_screenheight() - ask.winfo_reqheight()) / 2
    ask.wm_geometry("+%d+%d" % (x, y))
    ask.configure(bg='black')

    canv = Canvas(ask, width=300, height=300, bg='#9a9a9a')
    canv.grid(row=0, column=0, rowspan=10, columnspan=7)
    canv.create_line(0, 24, 300, 24, width=5, fill='#686868')
    canv.create_rectangle(5, 5, 300, 300, width=5, outline='#686868')
    canv.create_line(0, 202, 300, 202, width=5, fill='#686868')
    info = Label(ask, text='Пожалуйста, выберите сложность', font='Arial 11', bg='#686868', fg='#ffffff',
                 width=27, justify=CENTER)
    info.grid(column=0, row=0, columnspan=7)
    easy = Button(ask, text='Легко', command=easyChoice, anchor=CENTER, font='Arial 15', width=7, background='#686868',
                  highlightbackground='#686868', fg='#ffffff', activebackground='#464646', activeforeground="#ffffff")
    easy.grid(column=0, row=6, columnspan=3)
    medium = Button(ask, text='Средне', command=mediumChoice, anchor=CENTER, font='Arial 15', width=7, background='#686868',
                    highlightbackground='#686868', fg='#ffffff', activebackground='#464646', activeforeground="#ffffff")
    medium.grid(column=2, row=6, columnspan=3)
    hard = Button(ask, text='Сложно', command=hardChoice, anchor=CENTER, font='Arial 15', width=7, background='#686868',
                  highlightbackground='#686868', fg='#ffffff', activebackground='#464646', activeforeground="#ffffff")
    hard.grid(column=4, row=6, columnspan=3)

    ask.mainloop()


def helpButton():
    path = os.path.normpath('help.txt')
    os.startfile(path)


if __name__ == "__main__":
    preWindow()
