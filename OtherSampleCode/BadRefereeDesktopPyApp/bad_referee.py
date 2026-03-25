import random
from tkinter import Tk, Canvas, NW, Button, Label
from PIL import Image, ImageTk
from pygame import mixer

# Initializing the Sound Mixer
mixer.init()

# Creating the Main Window
root = Tk(); root.title("Bad Referee")
# Create the Canvas
(cnvsW, cnvsH) = (300, 450)
canvas = Canvas(root, width=cnvsW, height=cnvsH)
canvas.pack()

# Placing a Button on the Form
(btnXpos, btnYpos, btnW, btnH) = (110, 10, 8, 2)
btnPlayBall = Button(root, text="PlayBall", width=btnW, height=btnH)
btnPlayBall.place(x=btnXpos, y=btnYpos)

# Load and ReSize Image File
imgFile = "Desktop_BadReferee.jpg"
(imgXpos, imgYpos, imgW, imgH) = (20, 60, 250, 200)
image = Image.open(imgFile)
image = image.resize((imgW, imgH), Image.LANCZOS)
img = ImageTk.PhotoImage(image)
# Draw image
canvas.create_image(imgXpos, imgYpos, anchor=NW, image=img)

# Placing the Label
(lblXpos, lblYpos, lblLngth) = (15, 265, 250)
lblBadRefCall = Label(root, text="- - -", wraplength=lblLngth)
lblBadRefCall.place(x=lblXpos, y=lblYpos)

# Naming the Variables
RfL = ["Psycho Ted", "Dumb Neddy", "Drunk Nelson", "Blind Lenny", "Sleepy Hecho",
       "Beligerant Barry", "Crooked Larry", "Super Thompson", "Honest Franky",
       "Goodshoes Bobby", "Mean Mattheson", "Obsessed Dingleton",
       "Obnoxious Pickleson", "Cranky Shortwall"]

PlL = ["Fatso Joe", "Turbo Freddy", "Idle Kip", "Dancey Duke", "High Nelly",
       "Sloppy Biff", "Goofy Johnson", "Juggalo Jerry", "Conniving Terrance", "Hyper Wangston"]

PtL = ["offsides", "unsportsmanlike conduct", "unnecessary roughness", "delay of game",
       "facemasking", "holding", "pass interference", "roughing the passer",
       "mowing the kicker", "punching the retriever", "illegal formation"]

DL = ["no", "5", "10", "15", "20", "30", "50"]

NdL = [" repeat first", " and its second", " and its third", " and its fourth", ", turnover on"]

def btnPlayBall_click(PlayBall):
       rf = round((len(RfL) - 1) * random.random())
       pl = round((len(PlL) - 1) * random.random())
       pt = round((len(PtL) - 1) * random.random())
       di = round((len(DL) - 1) * random.random())
       nd = round((len(NdL) - 1) * random.random())
       lblBadRefCall.config(text="Referee " + str(RfL[rf]) + " flags player " + str(PlL[pl]) + " on the play ... " \
                             + str(PtL[pt]) + ", a " + DL[di] + " yard penalty" + NdL[nd] + " down!")
       mixer.music.load('tweet.wav'); mixer.music.play()

btnPlayBall.bind("<Button-1>", btnPlayBall_click)
# note - there is a big array of button bindings such as
# <Enter> Hover In, <Leave> Hover Out <Button-3> Right Mouse

root.mainloop()