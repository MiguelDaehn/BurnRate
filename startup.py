import numpy as np
import matplotlib.pyplot as plt
from numpy import sin,cos,tan,arcsin,arccos,arctan,pi
import pandas as pd
from icecream import ic
import time
from scipy.optimize import curve_fit

def err(x1,x2):
    if x1 ==0:
        return 0
    return abs((x1-x2)/x1)

def main():
    return 0

def pl(x,y,lx='',ly='',tit='',x0f=[0,None],y0f=[0,None]):
    plt.plot(x,y)
    plt.scatter(x,y,marker='*',color='red')
    plt.grid(True)
    plt.ylabel(ly)
    plt.xlabel(lx)
    plt.title(tit)
    plt.ylim(y0f[0],y0f[1])
    plt.xlim(x0f[0],x0f[1])
    plt.legend()
    plt.show()
    return

if __name__ == '__main__':
    main()
