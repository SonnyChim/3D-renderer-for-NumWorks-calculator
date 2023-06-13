import numpy as np
import cv2 as cv
import triangle
import time

def project(px,py,pz,sx1,sy1,sz1,sx2,sy2,sz2,imgres):
    if sx1 != sx2:
        raise ValueError
    if px >= 0:
        return None
    distancecam = -px
    distancescrn = px-sx1
    dheight = py
    pixely = (dheight/distancecam)*distancescrn + py
    screenpixelx = int((sy1-pixely)*(imgres[0]/(sy1-sy2)))
    dheight = pz
    pixelz = (dheight/distancecam)*distancescrn + pz
    screenpixely = int((sz1+pixelz)*(imgres[1]/(sz1-sz2)))
    return screenpixelx,screenpixely

def drawtri(img,tricoords,scrncoords,imgres,color):
    tricoords2d = tuple(project(tricoords[i][0],tricoords[i][1],tricoords[i][2],scrncoords[0][0],scrncoords[0][1],scrncoords[0][2],scrncoords[1][0],scrncoords[1][1],scrncoords[1][2],imgres) for i in range(3))
    if not all(tricoords2d):
        return None
    triangle.triangle(img,tricoords2d[0][0],tricoords2d[0][1],tricoords2d[1][0],tricoords2d[1][1],tricoords2d[2][0],tricoords2d[2][1],color)

def randtris3d():
    import random
    imgres = (320,222)
    img = np.full((imgres[1],imgres[0],3),255,np.uint8)
    scrncoords = ((-100,-50,-35),(-100,50,35))
    while cv.waitKey(1) != ord("q"):
        tricoords3d = tuple((random.randrange(-300,-100),random.randrange(-100, 100),random.randrange(-100, 100)) for i in range(3))
        print(tricoords3d)
        color = tuple(random.randrange(256) for i in range(3))
        drawtri(img,tricoords3d,scrncoords,imgres,color)
        cv.imshow("image",img)

def rotatingtri():
    import math
    # imgres = (1080,720)
    imgres = (320,222)
    img = np.full((imgres[1],imgres[0],3),255,np.uint8)
    tricoords3d = ((-150, 0 , 30),(-150,-50,-30),(-150,50,-30))
    scrncoords = ((-100,-50,-35),(-100,50,35))
    angles = [0,180]
    math.sin(math.radians(180))
    while cv.waitKey(1)!= ord("q"):
        img = np.full((imgres[1],imgres[0],3),255,np.uint8)
        tricoords3d = ((-150, 0 , 30),(-150 + 50 * math.sin(math.radians(angles[1])),50 * math.cos(math.radians(angles[1])),-30),(-150 + 50 * math.sin(math.radians(angles[0])),50 * math.cos(math.radians(angles[0])),-30))
        drawtri(img, tricoords3d, scrncoords,imgres,(128,128,128))
        cv.imshow("rotating triangle",img)
        angles[0] += 1
        angles[1] += 1

def ordertrisbydistance(tricoords):
    distances = ((tuple(point[0]*point[0]+point[1]*point[1]+point[2]*point[2] for point in coords[0:3]),i) for i,coords in enumerate(tricoords))
    # print(tuple(distances[0]))
    distancessorted = sorted(((min(coords[0]),coords[0][0]+coords[0][1]+coords[0][2],coords[1]) for coords in distances) , reverse=True)
    # print(distancessorted)
    # distances = sorted(((min(point[0]*point[0]+point[1]*point[1]+point[2]*point[2] for point in coords[0:3]),i) for i,coords in enumerate(tricoords)), reverse=True)
    return (tricoords[distance[2]] for distance in distancessorted)

def drawscene(img, tricoords, scrncoords,imgres):
    for tri in ordertrisbydistance(tricoords):
        drawtri(img,tri[0:3],scrncoords,imgres,tri[3])

def rotatingpyramid(sleep_time = 0,speed = 1,sides = 4):
    import math
    imgres = (1280,888)
    imgres = (320,222)
    scrncoords = ((-100,-50,-35),(-100,50,35))
    
    angles = [0,360/sides]
    math.sin(math.radians(180))
    while cv.waitKey(1) != ord("q"):
        img = np.full((imgres[1],imgres[0],3),255,np.uint8)
        tricoords = tuple(((-150, 0 , 30),(-150 + 50 * math.sin(math.radians(angles[0] + angles[1] + angles[1] * j)),50 * math.cos(math.radians(angles[0] + angles[1] + angles[1] * j)),-30),(-150 + 50 * math.sin(math.radians(angles[0] + angles[1] * j)),50 * math.cos(math.radians(angles[0] + angles[1] * j)),-30),tuple(256 - 128 * ((angles[0] + angles[1] * j + 180) % 360) / 360 for i in range(3))) for j in range(math.floor(sides)))
        drawscene(img,tricoords,scrncoords,imgres)
        cv.imshow("rotating pyramid",img)
        angles[0] += speed
        # sides = angles[0]/50 + 1
        angles[1] = 360/sides
        time.sleep(sleep_time)

def chain(*iterables):
    for iterable in iterables:
        yield from iterable

def displayobject(obj,mtl = None, depth = 300, rotate = False, rotationspeed = 1, linearcolor = False, image_resolution = (320,222)):
    # .obj file
    # scale: 100
    # forward axis: y
    # up axis: z

    if not type(obj) == str:
        obj = obj.read()
    # image_resolution = (320,222)
    image_resolution = (1280,888)
    # image_resolution = (640,444)
    scrncoords = ((-100,-50,-35),(-100,50,35))
    coordlist = tuple((tuple(float(i) for i in text.split(" ")[1:4])) for text in obj.split("\n") if text and text[0] == "v")
    faces = ((tuple(int(i) for i in text.split(" ")[1:4])) for text in obj.split("\n") if text and text[0] == "f")
    tricoords = tuple(tuple(coordlist[i - 1] for i in face) for face in faces)

    del coordlist

    if mtl:
        mtl = mtl.read()
        if linearcolor:
            materials = (tuple(int(round((float(val)**0.4545)*255)) for val in col.split(" ")[1:4]) for col in mtl.split("\n") if col[0:2] == "Kd")
        else:
            materials = (tuple(int(round(float(val)*255)) for val in col.split(" ")[1:4]) for col in mtl.split("\n") if col[0:2] == "Kd")
        mtlranges = []
        for i,value in enumerate(obj.split("\n")):
            if value[0:6] == "usemtl":
                mtlranges.append(i)
            if not value:
                mtlranges.append(i)
        # for i,value in enumerate(obj.split("\n")):
        #     if value[0:6] == "usemtl":
        #         mtlranges.append((i,value.split(" ")[1]))
        #     if not value:
        #         mtlranges.append((i,""))
        
        colors = tuple(chain(*(tuple(material for _ in range(mtlranges[i+1]-mtlranges[i]-1)) for i,material in enumerate(materials))))

        del materials,mtlranges
    else:
        colors = tuple(tuple(sum(x)//4+128 for x in zip(*tri)) for tri in tricoords)
    
    del obj,mtl

    if rotate:
        import math
        distances = tuple(tuple(math.sqrt(coord[0] * coord[0] + coord[1] * coord[1]) for coord in tri) for tri in tricoords)
        # print(distances)
        angles = tuple(tuple(math.atan(coord[0]/coord[1]) if coord[1] > 0 else math.pi/2 if coord[1] == 0 else math.atan(coord[0]/coord[1]) + math.pi for coord in tri) for tri in tricoords)
        # print(angles)
        # return
        angle = 0
        while cv.waitKey(1) != ord("q"):
            tricoordsrotated = (tuple((distances[i][j] * math.sin(math.radians(angle) + angles[i][j]) - depth,distances[i][j] * math.cos(math.radians(angle) + angles[i][j]),coord[2]) for j,coord in enumerate(tri)) for i,tri in enumerate(tricoords))
            tricoordscolored = tuple((tri[0][0],tri[0][1],tri[0][2],tri[1]) for tri in zip(tricoordsrotated,colors))
            img = np.full((image_resolution[1],image_resolution[0],3),255,np.uint8)
            drawscene(img,tricoordscolored,scrncoords,image_resolution)
            cv.imshow("image",img)
            angle += rotationspeed
        # cv.waitKey()
    else:
        tricoordsrotated = (tuple((coord[0] - depth,coord[1],coord[2]) for coord in tri) for tri in tricoords)
        tricoordscolored = tuple((tri[0][0],tri[0][1],tri[0][2],tri[1]) for tri in zip(tricoordsrotated,colors))
        img = np.full((image_resolution[1],image_resolution[0],3),255,np.uint8)
        drawscene(img,tricoordscolored,scrncoords,image_resolution)
        cv.imshow("image",img)
        # cv.waitKey()


def main():
    imgres = (320,222)
    img = np.full((imgres[1],imgres[0],3),255,np.uint8)
    tricoords3d = ((-141,-173,26),(-165,-14,-17),(-162,30,19))
    scrncoords = ((-100,-50,-35),(-100,50,35))
    color = (0,0,0)
    # print(*tricoords3d[0],*scrncoords[0],*scrncoords[1])
    # tricoords2d = tuple(project(*tricoords3d[i],*scrncoords[0],*scrncoords[1],imgres) for i in range(3))
    # print(tricoords2d)
    # triangle.triangle(img,*tricoords2d[0],*tricoords2d[1],*tricoords2d[2],(0,0,0))

    # print(ordertrisbydistance((((-150, 0 , 30),(-150,-50,-30),(-150,50,-30),(128,128,128)),((-141,-173,26),(-165,-14,-17),(-162,30,19),(128,128,128)),((-150, 0 , 30),(-150,-50,-30),(-150,50,-30),(128,128,128)))))
    # drawtri(img,tricoords3d,scrncoords,imgres,color)
    # randtris3d()
    # rotatingtri()
    # rotatingpyramid()
    # drawscene(img,(((-150, 0 , 30),(-150,-50,-30),(-150,50,-30),(3,128,5)),((-141,-173,26),(-165,-14,-17),(-162,30,19),(128,62,23)),((-150, 0 , 30),(-150,-50,-30),(-150,50,-30),(75,32,128))),scrncoords,imgres) 
    # cv.imshow("image",img)
    # cv.waitKey()
    icosahedron = "v 0 -100 0 \nv -72 -44 -52 \nv 27 -44 -85 \nv 89 -44 0 \nv 27 -44 85 \nv -72 -44 52 \nv -27 44 -85 \nv 72 44 -52 \nv 72 44 52 \nv -27 44 85 \nv -89 44 0 \nv 0 100 0 \ns 0\nf 1 2 3\nf 2 1 6\nf 1 3 4\nf 1 4 5\nf 1 5 6\nf 2 6 11\nf 3 2 7\nf 4 3 8\nf 5 4 9\nf 6 5 10\nf 2 11 7\nf 3 7 8\nf 4 8 9\nf 5 9 10\nf 6 10 11\nf 7 11 12\nf 8 7 12\nf 9 8 12\nf 10 9 12\nf 11 10 12"
    monkey3 = "v 57 54 5\nv 57 -54 5\nv 62 -34 -3\nv 62 34 -3\nv 64 15 5\nv 64 -15 5\nv 66 -6 24\nv 66 6 24\nv 80 29 36\nv 64 15 43\nv 64 -15 43\nv 61 -35 51\nv 80 -29 36\nv 76 -46 30\nv 54 46 41\nv 57 -54 43\nv 56 63 24\nv 56 -63 24\nv 76 46 30\nv 80 -31 11\nv 80 32 11\nv 79 0 -18\nv -88 16 42\nv -42 17 -35\nv 53 22 -18\nv 57 -35 -92\nv 56 56 -8\nv 63 80 40\nv 76 -27 40\nv 75 30 47\nv 75 0 -19\nv 74 0 -14\nv 80 8 -13\nv 58 -59 -5\nv 63 -81 38\nv 85 -24 64\nv 85 25 65\nv 80 -0 37\nv 79 -9 -11\nv 57 34 -95\nv 75 13 -24\nv 77 -10 -28\nv 70 9 -79\nv 69 -8 -84\nv 75 -41 38\nv 69 -55 26\nv 71 -41 8\nv 76 19 30\nv 76 -19 29\nv 80 32 39\nv 75 22 13\nv 69 41 6\nv 68 53 19\nv 67 54 30\nv 75 -21 13\nv 63 -0 43\nv 70 -25 77\nv 70 25 77\nv 47 -45 52\nv 34 -80 8\nv 50 -23 -21\nv 40 78 10\nv 18 -34 96\nv -77 -1 -7\nv -45 -84 40\nv 34 -21 -41\nv 40 -28 -94\nv 40 32 -91\nv 29 16 -44\nv -49 18 93\nv -38 -71 69\nv 15 46 90\nv 47 46 52\nv 32 -75 40\nv 31 75 41\nv -36 86 47\nv -47 -41 -15\nv -13 67 -7\nv -46 -125 -0\nv -35 -114 49\nv -44 121 31\nv -42 116 2\nv -19 86 34\nv -29 85 -0\nv -43 -114 4\nv -44 -121 31\nv -35 -98 30\nv -32 -83 4\nv -30 79 10\nv -13 -70 -7\nv -19 -85 36\nv -35 98 29\nv -50 -130 46\nv -55 122 48\nv -43 131 44\nv -54 122 -0\nv -32 -77 -12\nv -37 69 -6\ns 0\nf 19 21 17\nf 20 14 18\nf 21 4 1\nf 3 20 2\nf 8 5 21\nf 21 9 8\nf 13 20 7\nf 13 7 11\nf 13 11 12\nf 19 15 9\nf 14 12 16\nf 17 15 19\nf 21 19 9\nf 13 14 20\nf 25 27 33\nf 34 61 39\nf 28 53 62\nf 36 57 35\nf 38 37 58\nf 30 38 48\nf 29 38 36\nf 35 29 36\nf 28 30 54\nf 34 46 35\nf 33 27 51\nf 51 55 33\nf 48 55 51\nf 40 44 26\nf 41 43 40\nf 44 42 26\nf 41 44 43\nf 22 32 31\nf 22 32 39\nf 33 42 41\nf 32 33 55\nf 39 32 55\nf 27 53 52\nf 46 34 47\nf 29 46 45\nf 48 50 30\nf 38 58 56\nf 57 38 56\nf 28 73 58\nf 35 59 74\nf 62 75 28\nf 69 68 67\nf 69 67 66\nf 40 67 68\nf 40 68 69\nf 67 26 66\nf 66 24 69\nf 71 63 70\nf 65 70 23\nf 72 75 76\nf 74 63 71\nf 73 63 56\nf 56 58 73\nf 57 56 59\nf 83 76 75\nf 71 91 74\nf 24 78 69\nf 61 90 77\nf 62 69 78\nf 98 23 76\nf 97 65 77\nf 65 64 77\nf 80 93 86\nf 81 82 95\nf 86 79 85\nf 82 84 78\nf 92 95 83\nf 87 80 86\nf 62 78 83\nf 91 88 90\nf 91 80 88\nf 60 91 90\nf 89 92 83\nf 84 92 89\nf 82 92 84\nf 87 85 88\nf 92 82 81\nf 82 98 96\nf 95 94 83\nf 91 65 93\nf 96 76 94\nf 79 93 97\nf 94 95 96\nf 17 21 1\nf 2 20 18\nf 4 21 5\nf 6 20 3\nf 7 20 6\nf 9 10 8\nf 9 15 10\nf 14 13 12\nf 18 14 16\nf 25 41 40\nf 26 42 61\nf 27 62 53\nf 35 60 34\nf 58 37 28\nf 38 57 36\nf 30 37 38\nf 28 37 30\nf 35 46 29\nf 53 28 54\nf 39 55 34\nf 38 29 49\nf 48 38 55\nf 55 38 49\nf 43 44 40\nf 41 42 44\nf 22 33 32\nf 39 33 22\nf 42 33 39\nf 25 33 41\nf 42 39 61\nf 51 27 52\nf 47 34 55\nf 30 50 54\nf 28 75 73\nf 35 57 59\nf 60 35 74\nf 61 34 60\nf 67 40 26\nf 25 40 69\nf 66 26 61\nf 25 62 27\nf 98 24 64\nf 77 64 24\nf 66 77 24\nf 23 98 64\nf 65 23 64\nf 63 72 70\nf 65 71 70\nf 23 70 76\nf 70 72 76\nf 72 73 75\nf 74 59 63\nf 73 72 63\nf 59 56 63\nf 62 83 75\nf 74 91 60\nf 71 65 91\nf 77 66 61\nf 61 60 90\nf 62 25 69\nf 77 90 97\nf 24 98 78\nf 86 93 79\nf 90 85 79\nf 92 81 95\nf 89 78 84\nf 83 78 89\nf 88 80 87\nf 85 90 88\nf 87 86 85\nf 82 78 98\nf 97 90 79\nf 82 96 95\nf 80 91 93\nf 83 94 76\nf 96 98 76\nf 97 93 65"
    # displayobject(monkey3,depth=400,rotate=True)
    # displayobject(icosahedron,rotate=True)
    # displayobject(icosahedron)
    # print(icosahedron)
    obj = open("C:/Users/Sonny/Documents/test.obj","rt",newline="\n")
    spherecolor = open("C:/Users/Sonny/Documents/sphere color.obj")
    spheremtl = open("C:/Users/Sonny/Documents/sphere color.mtl")
    rat = open("C:/Users/Sonny/Documents/rat.obj")
    ratcolored = open("C:/Users/Sonny/Documents/ratcolored.obj")
    ratmtl = open("C:/Users/Sonny/Documents/ratcolored.mtl")
    # print(obj)
    # displayobject(obj,depth=400,rotate=True)
    # displayobject(spherecolor,spheremtl,rotate=True)
    # displayobject(rat,depth=400,rotate=True)
    # testobj = open("C:/Users/Sonny/Documents/xtcvbu.obj")
    # testmtl = open("C:/Users/Sonny/Documents/xtcvbu.mtl")
    displayobject(ratcolored,ratmtl,rotate=True,rotationspeed=10,linearcolor=True)
    # displayobject(testobj,testmtl,linearcolor=True)
    skull = open("C:/Users/Sonny/Documents/skull.obj")
    # displayobject(skull,rotate=True,depth=600,rotationspeed=5)/

    # cv.waitKey()
    

if __name__ == "__main__":
    main()