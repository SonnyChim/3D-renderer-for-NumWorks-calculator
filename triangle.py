import numpy as np
import cv2 as cv

def triangle(img,x1,y1,x2,y2,x3,y3,col):
    if x1 < x2:
        if x2 < x3:
            coords = ((x1,y1),(x2,y2),(x3,y3))
        else:
            if x1 < x3:
                coords = ((x1,y1),(x3,y3),(x2,y2))
            else:
                coords = ((x3,y3),(x1,y1),(x2,y2))
    else:
        if x1 < x3:
            coords = ((x2,y2),(x1,y1),(x3,y3))
        else:
            if x2 < x3:
                coords = ((x2,y2),(x3,y3),(x1,y1))
            else:
                coords = ((x3,y3),(x2,y2),(x1,y1))

    try:
        pointing_up = (coords[1][1]-coords[0][1])/(coords[1][0]-coords[0][0])*(coords[2][0]-coords[0][0])+coords[0][1] < coords[2][1]
    except ZeroDivisionError:
        pointing_up = coords[1][1] < coords[0][1]
    try:
        m1 = (coords[1][1]-coords[0][1])/(coords[1][0]-coords[0][0])
    except ZeroDivisionError:
        m1 = 0
    try:
        m2 = (coords[2][1]-coords[1][1])/(coords[2][0]-coords[1][0])
    except ZeroDivisionError:
        m2 = 0
    try:
        m3 = (coords[2][1]-coords[0][1])/(coords[2][0]-coords[0][0])
    except ZeroDivisionError:
        m3 = 0

    col = col[::-1]

    if pointing_up:
        for i in range(coords[1][0]-coords[0][0]):
            if 0 <= coords[0][0] + i < img.shape[1] and int(m3 * i + coords[0][1]) >= 0:
                img[max(int(m1 * i + coords[0][1]),0):int(m3 * i + coords[0][1]),coords[0][0] + i] = col
        for i,j in zip(range(coords[1][0]-coords[0][0], coords[2][0]-coords[0][0]),range(coords[2][0]-coords[0][0])):
            if 0 <= coords[0][0] + i < img.shape[1] and int(m3 * i + coords[0][1]) >= 0:
                img[max(int(m2 * j + coords[1][1]),0):int(m3 * i + coords[0][1]),coords[0][0] + i] = col
    else:
        for i in range(coords[1][0]-coords[0][0]):
            if 0 <= coords[0][0] + i < img.shape[1] and int(m1 * i + coords[0][1]) >= 0:
                img[max(int(m3 * i + coords[0][1]),0):int(m1 * i + coords[0][1]),coords[0][0] + i] = col
        for i,j in zip(range(coords[1][0]-coords[0][0], coords[2][0]-coords[0][0]),range(coords[2][0]-coords[0][0])):
            if 0 <= coords[0][0] + i < img.shape[1] and int(m2 * j + coords[1][1]) >= 0:
                img[max(int(m3 * i + coords[0][1]),0):int(m2 * j + coords[1][1]),coords[0][0] + i] = col

def randtris(img,x,y):
    import random
    while cv.waitKey(1) != ord("q"):
        triangle(img,random.randrange(x),random.randrange(y),random.randrange(x),random.randrange(y),random.randrange(x),random.randrange(y),(random.randrange(256),random.randrange(256),random.randrange(256)))
        cv.imshow("image",img)

def main():
    x,y = 320,222
    img = np.full((y,x,3),255,dtype=np.uint8)
    # triangle(img,100,100,140,130,130,110,(0,0,0))
    triangle(img, 232, -52, 132, 43, 19, 73,(0,0,0))
    # randtris(img,x,y)
    cv.imshow("image",img)
    cv.waitKey()

if __name__ == "__main__":
    main()