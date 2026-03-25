import math
import numpy as np
from tkinter import Tk, Canvas, Button, Label, Entry

# Creating the Main Window
root = Tk(); root.title("Market Splitter App")
# Create the Canvas
(cnvsW, cnvsH) = (350, 600)
canvas = Canvas(root, width=cnvsW, height=cnvsH); canvas.pack()

# Button Locations and Values
(btnW, btnH) = (3, 1)
(bSPx, bSPy, bSPv) = (110, 43, "Split")
(bUPx, bUPy, bUPv) = (286, 10, "^")
(bDNx, bDNy, bDNv) = (286, 78, "v")
(bADx, bADy, bADv) = (257, 44, "+")
(bMNx, bMNy, bMNv) = (314, 44, "-")
(bDSx, bDSy, bDSv) = (256, 543, "D O L L A R")

# Placing the Buttons
b_sp = Button(root, text=bSPv, height=2); b_sp.place(x=bSPx, y=bSPy)
b_up = Button(root, text=bUPv, width=btnW, height=btnH); b_up.place(x=bUPx, y=bUPy)
b_dn = Button(root, text=bDNv, width=btnW, height=btnH); b_dn.place(x=bDNx, y=bDNy)
b_ad = Button(root, text=bADv, width=btnW, height=btnH); b_ad.place(x=bADx, y=bADy)
b_mn = Button(root, text=bMNv, width=btnW, height=btnH); b_mn.place(x=bMNx, y=bMNy)
b_ds = Button(root, text=bDSv); b_ds.place(x=bDSx, y=bDSy)

# Placing the Labels
(lblX19, lblV19) = (33, "- - -")
(lblY1, lblY2, lblY3, lblY4, lblY5) = (160, 200, 240, 280, 320)
(lblY6, lblY7, lblY8, lblY9) = (360, 400, 440, 480)

lbl_1 = Label(root, text=lblV19); lbl_1.place(x=lblX19, y=lblY1)
lbl_2 = Label(root, text=lblV19); lbl_2.place(x=lblX19, y=lblY2)
lbl_3 = Label(root, text=lblV19); lbl_3.place(x=lblX19, y=lblY3)
lbl_4 = Label(root, text=lblV19); lbl_4.place(x=lblX19, y=lblY4)
lbl_5 = Label(root, text=lblV19); lbl_5.place(x=lblX19, y=lblY5)
lbl_6 = Label(root, text=lblV19); lbl_6.place(x=lblX19, y=lblY6)
lbl_7 = Label(root, text=lblV19); lbl_7.place(x=lblX19, y=lblY7)
lbl_8 = Label(root, text=lblV19); lbl_8.place(x=lblX19, y=lblY8)
lbl_9 = Label(root, text=lblV19); lbl_9.place(x=lblX19, y=lblY9)
lbl_sn = Label(root, text=lblV19); lbl_sn.place(x=165, y=42)
lbl_ts = Label(root, text=lblV19); lbl_ts.place(x=165, y=10)
lbl_ipa = Label(root, text="$ $ $ $ $"); lbl_ipa.place(x=33, y=5)
lbl_high = Label(root, text="Current"); lbl_high.place(x=30, y=71)
lbl_low = Label(root, text="Strong Support"); lbl_low.place(x=160, y=71)
lbl_tick = Label(root, text="T I C K E R"); lbl_tick.place(x=100, y=530)

def validate_input(new_text):
    if new_text == "": return True
    # make sure only one decimal point is present
    if new_text.count(".") > 1: return False
    try: float(new_text); return True
    except ValueError: return False

vcmd = root.register(validate_input)

# Placing the Entry Boxes
inptAmount = Entry(root, validate="key", validatecommand=(vcmd, '%P'),
                   width=10); inptAmount.place(x=20, y=29)
inptLow = Entry(root, validate="key", validatecommand=(vcmd, '%P'),
                width=10); inptLow.place(x=159, y=93)
inptHigh = Entry(root,  validate="key", validatecommand=(vcmd, '%P'),
                 width=10); inptHigh.place(x=10, y=93)
inptTicker = Entry(root, width=10); inptTicker.place(x=90, y=550)

def pre_saver():
    if __name__ == "__saver__": saver()

def pre_getter():
    if __name__ == "__getter__": getter()

def pre_split():
    if __name__ == "__split__": split()

def pre_sn():
    if __name__ == "__sn()__": sn()

def pre_splitDollars():
    if __name__ == "__splitDollars__": splitDollars()

def pre_splitShares():
    if __name__ == "__splitShares__": splitShares()

def pre_scrollup():
    if __name__ == "__scrollup__": scrollup()

# Naming and Loading Global Variables
GV = {"Amnt": 0, "Low": 0, "High": 0, "Diff": 0,
      "Deci": 3, "stI": 1, "stJ": 1, "spSD": 1}
pre_sn()
curArr = [0, 0, 0, 0, 0, 0]
fplArr = [0, 0, 0, 0, 0, 0]
tickArr = ["", "", "", "", "", ""]
pre_scrollup()

def sn():
    global GV
    lbl_sn.config(text=str(GV["stI"]) + " / " + str(GV["stJ"]))
    lbl_ts.config(text="{:.2f}".format(float(inptAmount.get())/GV['stJ']))
    if lbl_ts == "NaN": lbl_ts.config(text="- - -")

    if GV["spSD"] == 0: b_ds.config(text="Share")
    else: b_ds.config(text="Dollar")

def scrollup():
    global GV
    pre_saver()
    if GV["stI"] < GV["stJ"]: GV["stI"] += 1
    sn(); pre_getter(); pre_split()

def scrolldown():
    global GV
    pre_saver()
    if GV["stI"] > 1: GV["stI"] -= 1
    sn(); pre_getter(); pre_split()

def saver():
    global GV, curArr, fplArr, tickArr
    curArr[GV["stI"] - 1] = int(inptHigh.get())
    fplArr[GV["stI"] - 1] = int(inptLow.get())
    tickArr[GV["stI"] - 1] = inptTicker.get()

def getter():
    global GV, inptHigh, inptLow, inptTicker
    inptHigh = curArr[GV["stI"] - 1]
    inptLow = fplArr[GV["stI"] - 1]
    inptTicker = tickArr[GV["stI"] - 1]

def split():
    global GV
    if GV["spSD"] == 1: pre_splitDollars()
    else: pre_splitShares()

def bumper():
    global GV, curArr, fplArr, tickArr
    for k in range(GV["stI"] - 1, 4, -1):
        curArr[k] = curArr[k - 1]; fplArr[k] = fplArr[k - 1]
        tickArr[k] = tickArr[k - 1]; curArr[GV["stI"] - 1] = 0
        fplArr[GV["stI"] - 1] = 0; tickArr[GV["stI"] - 1] = ""

def eraser():
    global GV, curArr, fplArr, tickArr
    for k in range(GV["stI"] - 1, 4):
        curArr[k] = curArr[k + 1]
        fplArr[k] = fplArr[k + 1]
        tickArr[k] = tickArr[k + 1]
        curArr[4] = 0; fplArr[4] = 0; tickArr[4] = ""

def b_ds_onclick(event_ds):
    global GV
    if GV['spSD'] == 0: GV['spSD'] = 1
    else: GV['spSD'] = 0; sn(); split()

def b_up_onclick(event_up): scrollup()
def b_dn_onclick(event_dn): scrolldown()

def b_ad_onclick(event_ad):
    global GV
    if GV["stJ"] < 6: GV["stJ"] += 1
    bumper(); sn(); saver(); scrollup()

def b_mn_onclick(event_mn):
    global GV
    scrolldown()
    if GV["stJ"] > 1: GV["stJ"] -= 1
    eraser(); sn(); split()

def b_sp_onclick(event_sp): split()

def splitShares():
    global GV, curArr, fplArr, tickArr
    iamnt = float(inptAmount.get())

    GV[float("Amnt")] = float(iamnt/(4711.6 * GV["stJ"]))

    am_arr = [2978.5*GV["Amnt"], 1095.8*GV["Amnt"], 403.2*GV["Amnt"],
              148.3*GV["Amnt"], 54.6*GV["Amnt"], 20.1*GV["Amnt"],
              7.4*GV["Amnt"], 2.7*GV["Amnt"], 1.0*GV["Amnt"]]

    low = float(inptLow.get())
    high = float(inptHigh.get())
    diff = high-low

    in_arr = [low+0.065*diff, low+0.188*diff, low+0.311*diff, low+0.434*diff,
              low+0.557*diff, low+0.680*diff, low+0.803*diff, low+0.926*diff, low+1.049*diff]

    deci = int(5-math.log(diff))
    deci = min(deci, 4)

    for i in range(7, 0, -1):
        if am_arr[i] < in_arr[i]:
            am_arr[i-1] = am_arr[i] + am_arr[i-1]
            am_arr[i] = 0

    labels = [lbl_1, lbl_2, lbl_3, lbl_4, lbl_5, lbl_6, lbl_7, lbl_8, lbl_9]
    for i in range(8, -1, -1):
        if am_arr[i] != 0 and diff > 0:
            labels[i].config(text=f"{round(in_arr[i], deci)} +' ... ' + "
                                  f"{round(am_arr[i]/in_arr[i], 0)} + 'S H A R E S'")
        else: labels[i].config(text="- - -")

    sn()

def splitDollars():
    global GV, curArr, fplArr, tickArr
    GV[float('Amnt')] = float(inptAmount.get())/(4711.6 * GV['stJ'])

    am_arr = np.array([2978.5, 1095.8, 403.2, 148.3, 54.6, 20.1, 7.4, 2.7, 1.0]) * GV['Amnt']

    # Assuming inLow, inHigh have been defined previously
    low = float(inptLow.get())
    high = float(inptHigh.get())
    diff = high - low

    in_arr = np.array([low + i*diff for i in np.arange(0.065, 1.114, 0.123)])

    deci = int(5-math.log(diff))
    deci = min(deci, 4)

    for i in range(8, 0, -1):
        if am_arr[i] < 10: am_arr[i-1] += am_arr[i]; am_arr[i] = 0

    labels = [lbl_1, lbl_2, lbl_3, lbl_4, lbl_5, lbl_6, lbl_7, lbl_8, lbl_9]

    for i in range(8, -1, -1):
        labels[i].config(text=f"@ {round(in_arr[i], deci)} ... $ {round(am_arr[i], 2)}")
        if am_arr[i] == 0 or diff <= 0: labels[i].config(text="- - -")

    sn()

b_sp.bind("<Button-1>", b_sp_onclick)
b_up.bind("<Button-1>", b_up_onclick)
b_dn.bind("<Button-1>", b_dn_onclick)
b_ad.bind("<Button-1>", b_ad_onclick)
b_mn.bind("<Button-1>", b_mn_onclick)
b_ds.bind("<Button-1>", b_ds_onclick)

root.mainloop()
