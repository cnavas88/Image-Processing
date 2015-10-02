# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal
"""
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import misc
def obrirImatge(img):
    imatge=misc.imread(img)
    #print (imatge[115][0][1])
    #plt.imshow(imatge)
    return imatge
#obrirImatge("cat.png")
def gaussian(sigma):
    masksize=6*sigma+1 
    Igaussian=[[masksize]*masksize for x in range(masksize)]
    x0=float(masksize)/2.0
    y0=float(masksize)/2.0
    for x in range (0, masksize):
        for y in range (0, masksize):
            esquer=(((x-x0)**2)/(2*(sigma**2)))
            dret=(((y-y0)**2)/(2*(sigma**2)))
            suma=esquer+dret
            Igaussian[x][y]=math.exp(-suma)

            #Igaussian[x][y]=math.exp(-(((pow((x-x0),2))/2*pow(sigma,2))+((pow((y-y0),2))/2*pow(sigma,2))))
    Imatge=obrirImatge("cat.png")
    #plt.imshow(Imatge)
    A=1/np.sum(Igaussian)
    for x in range (0, masksize):
        for y in range (0, masksize):
            Igaussian[x][y]=A*Igaussian[x][y]
    print (Imatge[11][111][0])
    #plt.imshow(Igaussian)
    #plt.imshow(Imatge)
    print ("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
    for x in range (0, masksize):
        for y in range (0, masksize):
            
            Imatge[x][y][0]=Imatge[x][y][0]*Igaussian[x][y]
            Imatge[x][y][1]=Imatge[x][y][1]*Igaussian[x][y]
            Imatge[x][y][2]=Imatge[x][y][2]*Igaussian[x][y]
    print (Imatge[11][111][0])
    plt.imshow(Imatge)
    #print (np.min(Igaussian))
gaussian(9)

