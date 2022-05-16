import time
import random
import pyfirmata
from tkinter import *
from tkinter import filedialog
from pyfirmata import Arduino, SERVO


def callback0(*args):
    slide = slider0_var.get()
    if slide:
        slider0.set(int(slide))


def slide0(*args):
    pos0.delete(0, END)
    pos0.insert(0, str(slider0.get()))


def callback1(*args):
    slide = slider1_var.get()
    if slide:
        slider1.set(int(slide))


def slide1(*args):
    pos1.delete(0, END)
    pos1.insert(0, str(slider1.get()))


global magnet
magnet = 0
run_pos = [[magnet, 0, 0]]
recorded_pos = [[magnet, 0, 0]]


def grab():
    global run_pos
    global magnet
    if not magnet:
        label.config(text='Grabbed')
        magnet = 1
    else:
        label.config(text='Released')
        magnet = 0
    run_pos[-1][0] = magnet


def run():
    global run_pos
    run_pos = [[]]
    run_pos[0].append(magnet)
    for pos in positions:
        run_pos[0].append(int(pos.get()))


def stop():
    global stop
    global run_pos
    stop = True
    run_pos = [recorded_pos[-1]]


def record():
    global recorded_pos
    position0 = int(pos0.get())
    position1 = int(pos1.get())
    setup = [magnet, position0, position1]
    # setup = [[int(pos.get()) for pos in positions]]
    if setup != recorded_pos[-1]:
        recorded_pos.append(setup)


def play():
    global stop
    global run_pos
    stop = False
    run_pos = []
    for pos in recorded_pos:
        run_pos.append(pos)


def restart():
    for pos in positions:
        pos.delete(0, END)
        pos.insert(0, '0')


def clear():
    global magnet
    global recorded_pos
    global run_pos
    magnet = 0
    label.config(text='Released')
    recorded_pos = [[magnet, 0, 0]]
    run_pos = [[magnet, 0, 0]]
    for pos in positions:
        pos.delete(0, END)
        pos.insert(0, '0')


def random_setup():
    run_pos = []
    for pos in positions:
        b = end0
        if pos == pos1:
            b = end1
        random_setup = random.randint(0, b)
        pos.delete(0, END)
        pos.insert(0, str(random_setup))
        run_pos.append(pos.get())


def open_file():
    global run_pos
    filepath = filedialog.askopenfilename()
    file = open(filepath, "r")
    data = file.read()
    run_pos = eval(data)
    file.close()


def save_file():
    file = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    file.write(str(recorded_pos))
    file.close()


root = Tk()
root.minsize(250, 150)

button_wide = 13
entry_width = 15
label_width = 100
slider_width = 100
end0 = 180
end1 = 105

slider0_var = StringVar(value='0')
slider1_var = StringVar(value='0')

sliders_var = [slider0_var, slider1_var]
callback = [callback0, callback1]

for idx, slider_var in enumerate(sliders_var):
    slider_var.trace_add('write', callback[idx])

servo0 = Label(root, text='Servo1')
servo0.grid(row=0, column=0, sticky='ew')

servo1 = Label(root, text='Servo2')
servo1.grid(row=2, column=0, sticky='ew')

pos0 = Entry(root, textvariable=slider0_var, width=entry_width)
pos0.grid(row=1, column=1, sticky='s')

pos1 = Entry(root, textvariable=slider1_var, width=entry_width)
pos1.grid(row=3, column=1, sticky='s', pady=3)

slider0 = Scale(root, from_=0, to=end0, orient=HORIZONTAL, length=slider_width, command=slide0)
slider0.grid(row=1, column=0)

slider1 = Scale(root, from_=0, to=end1, orient=HORIZONTAL, length=slider_width, command=slide1)
slider1.grid(row=3, column=0)

run = Button(root, text='RUN', command=run, width=button_wide)
run.grid(row=6, column=0)

save = Button(root, text='RECORD', command=record, width=button_wide)
save.grid(row=6, column=1)

play = Button(root, text='PLAY', command=play, width=button_wide)
play.grid(row=7, column=0)

clear = Button(root, text='CLEAR', command=clear, width=button_wide, state=ACTIVE)
clear.grid(row=7, column=1)

random_setup = Button(root, text='RANDOM', command=random_setup, width=button_wide)
random_setup.grid(row=6, column=2, sticky='ew')

stop = Button(root, text='STOP', command=stop, width=button_wide)
stop.grid(row=7, column=2, sticky='ew')

grab = Button(root, text='GRAB/RELEASE', command=grab)
grab.grid(row=2, column=2, sticky='ew')

label = Label(root, text='Released', width=entry_width)
label.grid(row=3, column=2, sticky='s')

sliders = [slider0, slider1]
positions = [pos0, pos1]

menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Open File", command=open_file)
filemenu.add_command(label="Save File", command=save_file)

root.config(menu=menubar)

board = Arduino('COM5')
magnet_pin = 9
servo0_pin = 5
servo1_pin = 3

for pin in servo0_pin, servo1_pin:
    board.digital[pin].mode = SERVO

stop = False
sleep = 0.1
while True:
    for pos in run_pos:
        print(pos[0], pos[1], pos[2], stop)
        board.digital[magnet_pin].write(pos[0])
        board.digital[servo0_pin].write(pos[1])
        board.digital[servo1_pin].write(pos[2])

        if len(run_pos) > 1:
            sleep = 0.8
        else:
            sleep = 0.1

        if stop:
            break

        time.sleep(sleep)
        root.update()

    root.update()
