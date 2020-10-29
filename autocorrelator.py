# Copyright © 2020 Pasechnikov Vyacheslav. All rights reserved.

__author__ = "Pasechnikov Vyacheslav"
__copyright__ = "Copyright 2020"
__version__ = "1.0.0"
__maintainer__ = "Pasechnikov Vyacheslav"
__status__ = "Development"

import tkinter as tk
from tkinter import Entry, Button, Radiobutton, Label
from tkinter import Menu, filedialog, messagebox, END
import librosa
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib import backend_bases
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


matplotlib.use('TkAgg')

filename = ''
current_file = ''

original = np.array([])

slider_len = 0
slider_res = 0
slider_interval = 0


def start_open_file():
    global filename

    ftypes = [('WAV file', '*.wav'), ('All files', '*')]
    dlg = filedialog.Open(filetypes = ftypes)
    filename = dlg.show()

    def ask():
        ansver = messagebox.askyesno('Warning', 'This action will close the application. Are you really sure?')
        return ansver

    if filename == '':
        ansver = ask()
        if ansver:
            quit()
        else:
            start_open_file()

    return filename

def is_integer(num):
    try:
        int(num)
        return True
    except ValueError:
        return False

def my_corr(lags):
    global original

    corr_val = np.array([])

    for i in range(1,lags+1):
        a = 0

        r_corr = np.array([original[j+i] if (j+i < original.size) else 0 for j in range(original.size)])

        for k in range(original.size):
            a += r_corr[k]*original[k]
        corr_val = np.append(corr_val, a)

    y = corr_val/corr_val.max(axis=0)

    return y

def main():
    global original
    global current_file

    start_screen = tk.Tk()
    start_screen.title('')
    start_screen.geometry(newGeometry='1x1')
    start_screen.iconbitmap('icon.ico')

    #==================================================
    filename = str(start_open_file())
    current_file = filename

    start_screen.destroy()

    original, sr = librosa.load(filename)

    lags_new = 1
    lags_old = 1

    max_lag = int(original.size/4)

    label_text = f'Lags - {lags_new} Max lag - {max_lag}'


    correlated = librosa.autocorrelate(original, max_size=lags_new)


    correlated = correlated/correlated.max(axis=0)


    #===================================================

    root = tk.Tk()

    #------------------------------------------------------------------------------
    def update():
        global filename
        global lags_new
        global original
        global max_lag
        global current_file

        if current_file != filename:
            original, sr = librosa.load(filename)
            current_file = filename

            max_lag = int(original.size/4)

            ax1.clear()
            ax1.set(ylabel='Original')
            ax1.plot(original, 'b--')

        correlated = librosa.autocorrelate(original, max_size=lags_new)
        correlated = correlated/correlated.max(axis=0)



        lag_label['text']= f'Lags - {lags_new} Max lag - {max_lag}'

        if rad_butt.get() == 1:
            i = my_corr(lags_new)
            ax3.clear()
            ax3.set(ylabel='My_ACF')
            ax3.stem(i,linefmt='r-',markerfmt='')
        elif rad_butt.get() == 0:
            ax3.clear()
            ax3.set(ylabel='My_ACF')


        ax2.clear()
        ax2.set(ylabel='ACF')
        ax2.stem(correlated,linefmt='g-',markerfmt='')


        canv.get_tk_widget().grid(row=0)
        canv.draw()


    def button_update():
        global lags_new
        global lags_old
        global filename
        global max_lag
        global current_file

        max_lag = int(original.size/4)

        if is_integer(entry_box.get()):
            lags_new = int(entry_box.get())
        else:
            lags_new = 1

        if lags_new == 0:
            lags_new = 1

        if (lags_new == lags_old) and (current_file == filename):
            update()
            entry_box.delete(0, END)
            pass

        if (lags_new) != (lags_old):
            if lags_new > max_lag:
                lags_new = max_lag
                update()
                entry_box.delete(0, END)
                pass
            lags_old = lags_new
            update()
            entry_box.delete(0, END)



    def format_coord(x=None,y=None):
        return ''

    def quit():
        root.destroy()

    def open_file():
        global filename
        global lags_new

        ftypes = [('WAC file', '*.wav'), ('All files', '*')]
        dlg = filedialog.Open(filetypes = ftypes)
        filename_ = dlg.show()

        if (filename_ == '') or (filename_ == filename):
            pass
        else:
            filename = filename_
            lags_new = 1
            update()


    def about():
        about_ = messagebox.showinfo('Autocorrelator',message=' Autocorrelator\n Version 1.0\n Pasechnikov Vyacheslav, 2020')

    def enter_click(event):
        button_update()


    #------------------------------------------------------------------------------

    mainmenu = Menu(root)
    root.config(menu=mainmenu)

    filemenu = Menu(mainmenu,tearoff=0)
    mainmenu.add_cascade(label='File', menu=filemenu)

    filemenu.add_command(label='Open file', command=open_file)
    filemenu.add_command(label='Exit',command=quit)

    helpmenu = Menu(mainmenu,tearoff=0)
    mainmenu.add_cascade(label='Help', menu=helpmenu)

    helpmenu.add_command(label='About',command=about)




    #------------------------------------------------------------------------------

    root.title('Autocorrelator')
    root.resizable(width=False,height=False)

    fig = Figure()


    fig.set_size_inches(15,6)


    ax1 = fig.add_subplot(3,1,1)
    ax1.set(ylabel='Original')
    ax1.plot(original, 'b--')

    ax1.format_coord = format_coord

    ax2 = fig.add_subplot(3,1,2)
    ax2.set(ylabel='ACF')
    ax2.stem(correlated,linefmt='g-',markerfmt='')

    ax2.format_coord = format_coord

    ax3 = fig.add_subplot(3,1,3)
    ax3.set(ylabel='My_ACF')

    rad_butt = tk.BooleanVar()
    rad_butt.set(0)


    ax3.format_coord = format_coord

    pos1 = ax2.get_position()

    toolbar_frame = tk.Frame(root)

    backend_bases.NavigationToolbar2.toolitems = [t for t in backend_bases.NavigationToolbar2.toolitems if t[0] in ('Back', 'Forward', 'Pan', 'Zoom', 'Save')]


    canv = FigureCanvasTkAgg(fig, root)
    toolbar = NavigationToolbar2Tk(canv, toolbar_frame)
    canv.get_tk_widget().grid(row=0)

    toolbar_frame.grid(row=1)

    slider_len = int(original.size / 4)
    slider_interval = int(slider_len / 10)
    slider_res = int(slider_interval / 2)

    lag_label = Label(text=label_text)
    button = Button(text='Set lag value', command=button_update)
    entry_box = Entry(width=10)
    rad_butt_ON = Radiobutton(text='My_ACF ON', variable=rad_butt, value=1)
    rad_butt_OFF = Radiobutton(text='My_ACF OFF', variable=rad_butt, value=0)

    entry_box.insert(0, str(lags_new))

    entry_box.grid(row=2, column=0)
    button.grid(row=3, column=0)
    rad_butt_ON.place(relx=0.1, rely=0.9)
    rad_butt_OFF.place(relx=0.1, rely=0.95)
    lag_label.place(relx=0.1, rely=0.01)

    root.bind('<Return>',func=enter_click)

    root.iconbitmap('icon.ico')
    root.mainloop()


if __name__ == '__main__':
    lags_new = 1
    lags_old = 1
    main()
