#!/usr/bin/env python3
import os
import tkinter
from tkinter import *
from tkinter import messagebox
import string
import imp

# This code creates GUI for a program in Python
# It requires the configuration file named 'gui.conf' structured as follows:
# The first line is the program name:         someprogram.py
# Each next line contains the variable name and its value or array of values comma-separated:
#                                             name_parameter1, value_ofParameter1
#                                             name_parameter2, value1_ofParameter2, value2_ofparameter2, etc.
# The order of parameters has to correspond to the order of variables in the main program someprogram.py
# User makes choices of values of variables and starts the main program by pressing the 'RUN' button
# The list of parameters 'par_val' is created and is used in the program someprogram.py
# ATTENTION! The program someprogram.py MUST have the function 'main(par_val)'

file_conf = 'gui.conf'

# importing the main program code as a module to access objects and functions 
try:
    f = open(file_conf, 'r')
except:
    tkinter.messagebox.showinfo("showinfo", "File "+file_conf+' is not available')

line="_"
while (line != ''):
    line = f.readline().strip()        #stripping end symbol/n
    line_split = line.split(',')
    if(len(line_split) == 1 and '.py' in line_split[0]):     #file name *.py is supposed to be in a separate line 
        source_file = line_split[0]
        print('The main program code:   ' + source_file)
f.close()        
imp.load_source('source_module',source_file)
from source_module import *

par_name = []
par_val  = []

#reading gui configuration file to get parameter names and parameter initial values (or list of values for drop-down menu items)
def read_conf(file_conf):
    try:
        f = open(file_conf, 'r')
    except:
        tkinter.messagebox.showinfo('showinfo', "File "+file_conf+' is not available')
    line='_'
    k = 0
    while (line != ''):
        line = f.readline().strip()        #stripping end symbol/n
        line_split = line.split(',')
        n = len(line_split)
        if(n>1):         # to avoid line with the code file name (all other lines have at least two items: parameter name and value(s)
            par_name.append(line_split[0])    # parameter name
            pars = []                         # array of values (one or more)
            for j in range(1,n):
                pars.append(line_split[j])
            par_val.append(pars)              # adding value items to the name
    f.close()

# is executed by the button RUN
def run():
    inp = []
    for i in range(0,k):
        inp.append(par[i].get())     # convert tkinter value of par[] and adding it to the list 'inp'
    main(inp)                        # calling the function main() in the model code 'source_file'
    print('saving ', source_file,' ',par_name,' ',inp,' to ', file_conf)
    f = open(file_conf, 'w')         # opening configuration file to update parameters
    f.write(source_file+'\n')
    for i in range(0,len(par_name)):
        f.write(par_name[i])
        for j in range(0,len(par_val[i])):
            if(len(par_val[i]) > 1):
                f.write(','+par_val[i][j])
            if(len(par_val[i]) == 1):
                f.write(','+ inp[i])
        f.write('\n')
    f.close()

read_conf(file_conf)         # reading configuration file 

# creating menu
root = Tk()
root.title(source_file)
    
n_menu = len(par_name)
par = []
k = 0
for i in range(0,n_menu):
    if(len(par_val[i]) == 1):       # menu items with value which can be manually entered
        Label(root, text= par_name[k],borderwidth=1 ).grid(row=k,column=0)
        par.append(StringVar())
        par[k].set(par_val[k][0])
        w = Entry(root,textvariable= par[k], bd =5,bg='snow',fg='maroon')#,width=20)
        w.grid(row=k,column=1)
    if(len(par_val[i]) > 1):        # menu items with a set of values in the drop-down list
        Label(root, text= par_name[k],borderwidth=1 ).grid(row=k,column=0)
        par.append(StringVar())
        types = par_val[k]
        par[k].set(types[0])
        w = OptionMenu(root, par[k], *types)
        w.config(width = 30)
        w.grid(row=k,column=1)
    k = k + 1
Button(root,fg='yellow', bg='slate blue',text='Run',command = lambda: run()).grid(row=k + 1, columnspan=2,sticky= E+W)
Button(root, fg='snow',bg='light blue', text='Quit',command = root.destroy).grid(row=k + 2,columnspan=2,sticky= E+W)
root.mainloop()

