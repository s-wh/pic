from tkinter import *
from tkinter.filedialog import *
import os
from PIL import Image
import numpy as np
import cv2
import math
import time
from tkinter import messagebox
import random

#windows root.geometry('213x215')
#btn1=Button(frame,text='选择文件夹',command=askFile,width=28,height=8)

allFileNum = 0
fileList=[]
filepath=''
newfilepath=''
test=False

root=Tk()
root.title('图片处理')
root.geometry('213x215')

def askFile():
    global filepath
    filepath=askdirectory(title='上传文件',initialdir='/Users/swh/Desktop')
    printPath(filepath)

def printPath(path):
    global newfilepath
    global allFileNum
    global fileList
    files = os.listdir(path)
    for f in files:
        if (f[0] != '.'):
            fileList.append(f)
    fileList.sort()
    os.chdir(filepath)
    n=filepath.rfind('/')
    filename=filepath[n+1:]
    try:
        os.mkdir(filename)

    except:
        messagebox.showinfo('请先将旧文件夹删除', '请先将旧文件夹删除')
        return
    newfilepath = filepath + '/' + filename
    convert()


def convert():
    global filepath
    global allFileNum
    global fileList
    global newfilepath
    allFileNum=len(fileList)
    for i in range(allFileNum):
        img = Image.open(filepath + '/' + fileList[i])
        pix = img.load()
        width = img.size[0]
        height = img.size[1]
        if averagecolor(img,width,height,pix)[0]>190 \
                and averagecolor(img,width,height,pix)[1]>190 \
                and averagecolor(img,width,height,pix)[2]>190:
            blackframe(img, width, height, pix)
            paint(img, width, height, pix)
            img.save(newfilepath + '/' + fileList[i])
            rotate(newfilepath + '/' + fileList[i])
        else:
            averapaint(img, width, height, pix)
            img.save(newfilepath + '/' + fileList[i])
        change_schedule(i + 1, allFileNum)
    messagebox.showinfo('完成', '完成')

def rotate(filepath):
    global test
    img = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), 1)
    h, w = img.shape[:2]
    if w>h:
        return False
    blank = np.zeros(shape=(w, h))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sobel_x = cv2.Sobel(gray, cv2.CV_8U, 1, 0)
    sobel_y = cv2.Sobel(gray, cv2.CV_8U, 0, 1)

    ret1, thresh1 = cv2.threshold(sobel_x, 200, 255, cv2.THRESH_BINARY)
    ret2, thresh2 = cv2.threshold(sobel_y, 200, 255, cv2.THRESH_BINARY)
    # cv2.namedWindow('thresh', 0)
    # cv2.imshow('thresh', thresh)
    thresh = thresh1 + thresh2
    #cv2.imshow('thresh', thresh)
    threshold = 100
    minLineLength = 100
    maxLineGap = 100
    lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, threshold, minLineLength, maxLineGap)

    try:
        counter=0
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(blank, (x1, y1), (x2, y2),
                         (1), thickness=1)
                if test==True:
                    cv2.line(img, (x1, y1), (x2, y2),
                            (random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255)), thickness=5)
                if abs(y1-y2)>abs(x1-x2):
                    counter=counter+1
        if counter==0:
            #print(filepath)
            return True
            #textrotate(img,filepath)
        # cv2.imshow('lines',blank)
        coords = np.column_stack(np.where(blank > 0))
        angle = cv2.minAreaRect(coords)[-1]
        # print(counter)
        # if counter!=0:
        #    angle=angle/counter
        #    angle=math.atan(angle)
        if angle < -45:
            angle = angle + 90
        elif angle > 45:
            angle = angle - 90
        #print(angle)
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        if os.path.exists(filepath):
            os.remove(filepath)
        cv2.imencode(filepath, img)[1].tofile(filepath)
    except Exception as e:
        return True
        #textrotate(img,filepath)

def textrotate(img,filepath):
    h, w = img.shape[:2]
    newimg=img

    for y in range(200):
        for x in range(300):
            newimg[h - 1 - y, x]=(255, 255, 255)
            newimg[h - 1 - y, w - 1 - x] = (255, 255, 255)
    gray = cv2.cvtColor(newimg, cv2.COLOR_BGR2GRAY)
    grayNot = cv2.bitwise_not(gray)
    thresh = cv2.threshold(grayNot, 100, 255, cv2.THRESH_BINARY, )[1]

    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = angle + 90
    elif angle > 45:
        angle = angle - 90
    #print(angle)
    if abs(angle) >=3:
        angle=0
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    if os.path.exists(filepath):
        os.remove(filepath)
    cv2.imencode(filepath, img)[1].tofile(filepath)

def averagecolor(img,width,height,pix):
    h1 = int(height / 4)
    h2 = int(height / 2)
    h3 = int(3 * height / 4)
    color1sum=0
    color2sum = 0
    color3sum = 0
    blackpixel=0
    for i in range(width):
        if pix[i, h1][0]<50 and pix[i, h1][1]<50 and pix[i, h1][2]<50:
            blackpixel=blackpixel+1
        else:
            color1sum = color1sum + pix[i, h1][0]
            color2sum = color2sum + pix[i, h1][1]
            color3sum = color3sum + pix[i, h1][2]
        if pix[i, h2][0]<50 and pix[i, h2][1]<50 and pix[i, h2][2]<50:
            blackpixel=blackpixel+1
        else:
            color1sum = color1sum + pix[i, h2][0]
            color2sum = color2sum + pix[i, h2][1]
            color3sum = color3sum + pix[i, h2][2]
        if pix[i, h3][0]<50 and pix[i, h3][1]<50 and pix[i, h3][2]<50:
            blackpixel=blackpixel+1
        else:
            color1sum = color1sum + pix[i, h3][0]
            color2sum = color2sum + pix[i, h3][1]
            color3sum = color3sum + pix[i, h3][2]
    color1sum = int(color1sum / (3 * width-blackpixel))
    color2sum = int(color2sum / (3 * width-blackpixel))
    color3sum = int(color3sum / (3 * width-blackpixel))
    return (color1sum,color2sum,color3sum)

def blackframe(img,width,height,pix):
    for i in range(width):
        for j in range(12):
            pix[i,j]=(0,0,0)

    for j in range(height):
        for i in range(12):
            pix[i,j]=(0,0,0)
            pix[width-1-i,j]=(0,0,0)
    for i in range(width):
        for j in range(8):
            pix[i,height-1-j]=(0,0,0)

def paint(img,width,height,pix):
    for i in range(width):
        for j in range(height-3):
            if white(pix[i,j]) and white(pix[i,j+1]) and white(pix[i,j+2]):
                break
        for k in range(j+1):
            pix[i, k] = Color(pix,i, j+2,True,width,height)

    for i in range(width):
        for j in range(height-3):
            if white(pix[i,height-1-j]) and white(pix[i,height-1-j-1]) and white(pix[i,height-1-j-2]):
                break
        for k in range(j + 1):
            pix[i, height - 1 - k] = Color(pix,i, height - 1 - j-2,True,width,height)

    for j in range(height):
        for i in range(width-3):
            if white(pix[i, j]) and white(pix[i+1, j]) and white(pix[i+2, j]):
                break
        for k in range(i+1):
            pix[k, j] = Color(pix,i+2, j,False,width,height)

    for j in range(height):
        for i in range(width-3):
            if white(pix[width-1-i, j]) and white(pix[width-1-i-1, j]) and white(pix[width-1-i-2, j]):
                break
        for k in range(i + 1):
            pix[width - 1 - k, j] = Color(pix,width - 1 - i-2, j,False,width,height)

def averapaint(img,width,height,pix):
    for i in range(width):
        for j in range(height-3):
            if notblack(pix[i,j]) and notblack(pix[i,j+1]) and notblack(pix[i,j+2]) and \
                    notblack(pix[i,j+3]) and notblack(pix[i,j+4]) and notblack(pix[i,j+5]):
                break
        for k in range(j+1):
            pix[i, k] = pix[i, j+2]

    for i in range(width):
        for j in range(height-3):
            if notblack(pix[i,height-1-j]) and notblack(pix[i,height-1-j-1]) and notblack(pix[i,height-1-j-2]) \
                    and notblack(pix[i,height-1-j-3]) and notblack(pix[i,height-1-j-4]) and notblack(pix[i,height-1-j-5]):
                break
        for k in range(j + 1):
            pix[i, height - 1 - k] = pix[i, height - 1 - j-2]

    for j in range(height):
        for i in range(width-3):
            if notblack(pix[i, j]) and notblack(pix[i+1, j]) and notblack(pix[i+2, j]) and\
                notblack(pix[i+3, j]) and notblack(pix[i+4, j]) and notblack(pix[i+5, j]):
                break
        for k in range(i+1):
            pix[k, j] = pix[i+2, j]

    for j in range(height):
        for i in range(width-3):
            if notblack(pix[width-1-i, j]) and notblack(pix[width-1-i-1, j]) and notblack(pix[width-1-i-2, j]) and\
                    notblack(pix[width-1-i-3, j]) and notblack(pix[width-1-i-4, j]) and notblack(pix[width-1-i-5, j]):
                break
        for k in range(i + 1):
            pix[width - 1 - k, j] = pix[width - 1 - i-2, j]

def notblack(color):
    if color[0]<50 and color[1]<50 and color[2]<50:
        return False
    else:
        return True

def white(color):
    if color[0]>200 and color[1]>200 and color[2]>200:
        return True
    else:
        return False

def Color(pix,x,y,row,width,height):
    if row:
        if nocolor(pix[x,y]) :
            return pix[x,y]
        else:
            for i in range(width):
                if x-i>=0 and nocolor(pix[x-i,y]) and white(pix[x-i,y]):
                    return pix[x-i,y]
                if x + i <= width-1 and nocolor(pix[x + i, y])and white(pix[x+i,y]):
                    return pix[x + i, y]
            return pix[x,y]

    else:
        if nocolor(pix[x, y]):
            return pix[x, y]
        else:
            for i in range(height):
                if y - i >= 0 and nocolor(pix[x, y-i]) and white(pix[x , y-i]):
                    return pix[x, y-i]
                if y + i <= height - 1 and nocolor(pix[x, y+i]) and white(pix[x, y+i]):
                    return pix[x, y+i]
            return pix[x, y]

def nocolor(color):
    if abs(color[0]-color[1])<13 and abs(color[0]-color[2])<13 and abs(color[1]-color[2])<13 :
        return True
    else:
        return False

def change_schedule(now_schedule, all_schedule):
    canvas.coords(fill_rec, (5, 5, 6 + (now_schedule / all_schedule) * 200, 25))
    root.update()
    x.set(str(round(now_schedule / all_schedule * 100, 2)) + '%')
    if round(now_schedule / all_schedule * 100, 2) == 100.00:
        x.set("完成")

def testornot():
    global test
    messagebox.showinfo('仅供测试使用', '处理后的图片仅供测试使用，\n若要还原请重新打开软件')
    test=True
def createContextMenu(event):
    contextMenu.post(event.x_root, event.y_root)

frame = Frame(root).grid(row=0, column=0)
canvas = Canvas(frame, width=210, height=30, bg="white")
canvas.grid(row=1, column=0)
btn1=Button(frame,text='选择文件夹',command=askFile,width=28,height=8)
btn1.grid(row=0,column=0)

contextMenu = Menu(frame)
contextMenu.add_command(label="测试", command=testornot)
root.bind("<Button-3>",createContextMenu)

x = StringVar()
out_rec = canvas.create_rectangle(5, 5, 205, 25, outline="black", width=1)
fill_rec = canvas.create_rectangle(5, 5, 5, 25, outline="", width=0, fill="black")
Label(frame, textvariable=x).grid(row=2, column=0)

root.mainloop()