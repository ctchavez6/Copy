import os
import sys
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize


# These two lines are error handling
old_err_state = np.seterr(divide='raise')
ignored_states = np.seterr(**old_err_state)

# Save current directory to a variable
start_dir = os.getcwd()
quit_string = "\nTo quit, type 'q' or 'quit', then press Enter: " # Option to quit
print("Welcome to create r matrix from csv.py")
user_input = input("To proceed and select an r_matrices_stats file, press Enter." + quit_string)

if user_input.lower() in ["quit", "q"]:
    sys.exit()


filename_r_matrices_stats = askopenfilename(
    title='Pick a r_matrices_stats_file')  # show an "Open" dialog box and return the path to the selected file

df = pd.read_csv(filepath_or_buffer=filename_r_matrices_stats)

x = df.loc[:, 'X'].values
y = df.loc[:, 'Y'].values

n = len(x)                          #the number of data
mean = sum(x*y)/n                   #note this correction
sigma = sum(y*(x-mean)**2)/n        #note this correction

def gaus(x,a,x0,sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

params,params_covariance = optimize.curve_fit(gaus,x,y,p0=[80,200,51])
#print(params)
waist = params[0]/(np.e)**2
#print(waist)

def find_roots(x,y):
    s = np.abs(np.diff(np.sign(y))).astype(bool)
    return x[:-1][s] + np.diff(x)[s]/(np.abs(y[1:][s]/y[:-1][s])+1)
fit = gaus(x,params[0],params[1],params[2])
z = find_roots(x,fit-waist)
#print(z)

plt.figure(figsize = (6,4))
plt.scatter(x,y,label = 'gaussian')
plt.plot(x,fit,c='red')
plt.plot(z, np.zeros(len(z))+waist, marker="o", ls="", ms=4, color= 'orange')
plt.savefig(str(input("name: "))+".png")
plt.show()
print("Diameter is: ", (z[1]-z[0]), "pixels")

