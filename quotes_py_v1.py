#import requests
import ystockquote
import string
import time
import datetime
from datetime import timedelta
import tkinter
from tkinter import *
from tkinter import messagebox
import matplotlib
import matplotlib.pyplot as pyplot
import matplotlib.image as mpimg
from matplotlib.finance import date2num
import numpy
import scipy
from subprocess import call
import os
import os.path


def make_graphs(tickers,names,delt,matr,inp):
    year_days = 260.0
    if(inp[0] == 'Get quotes and show graphs' or 'Show graphs only'):
        week   = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        nm = len(matr)
        time_label = 'From ' + matr[0][0]+' to '+matr[nm-1][0] + ' (dd/mm/yyyy)'
        date_now = datetime.datetime.strptime(matr[nm-1][0], "%d/%m/%Y").date()
        wdn = date_now.weekday()
        weekday = week[wdn]
        if inp[1] == '1 month':
            span = int(year_days / 12)
        if inp[1] == '3 months':
            span = int(0.25 * year_days)
        if inp[1] == '6 months':
            span = int(0.5 * year_days)
        if inp[1] == '1 year':
            span = int(year_days)
        if inp[1] == '2 years':
            span = int(2.0 * year_days)
        if inp[1] == '3 years':
            span = int(3.0 * year_days)
        if inp[1] == '5 years':
            span = int(5.0 * year_days)
        if inp[1] == 'all':
            span = nm
        for j in range(len(tickers)):      # for each ticker ...
            y = []                         # array of prices
            t = []
            t_float = []
            v0 = 0
            for i in range(nm):           # along time line...
                try:
                    v = float(matr[i][j+1])
                    if(i==0 or v != v0):
                        y.append(matr[i][j+1])     # from data list matr
                        t.append(datetime.datetime.strptime(matr[i][0], '%d/%m/%Y'))
                        v0 = v
                        t_float.append(date2num(datetime.datetime.strptime(matr[i][0], '%d/%m/%Y')))
                except:
                    pass
            t0 = t_float[0] #starting time point
            for i in range(len(t)):
                t_float[i] = t_float[i] - t0    #relative time in days starting at zero
            trend_days = int(float(inp[2]) * year_days)   #duration of trend approximation
            n = len(y)
            start_point = max(0, n - span)
            i_start_trend = max(0, n - trend_days)
            t_date_trend = list(t)
            t_trend = list(t_float) #copy of t_float
            t_trend[0:i_start_trend] = []   #time points in days of trend duration
            y_trend = list(y)
            y_trend[0:i_start_trend] = []   #price array for trend duration
            try:
                z = numpy.polyfit(t_trend, y_trend, 1)
                p = numpy.poly1d(z)
                y_lin = []
                for i in range(len(t)):
                    y_lin.append(p(t_float[i]))
            except:
                print('no lin fit')
            t_date_trend[0:i_start_trend] = []
            y_lin[0:i_start_trend] = []


            t[0:start_point] = []
            y[0:start_point] = []

            n = len(y)
            delta = int((y[n-1]/y[n-2]-1)*100000)/1000
            down = float(inp[3][:-1]) / 100.
            up = float(inp[4][:-1]) / 100.
            x = round(y[n-1]/y_lin[len(y_lin)-1] - 1. ,  3)
            action = 'Wait ('+ str(x*100)+'% relative to trend)'
            if x >0 and x > up:
                action = 'Sell ('+ str(x*100)+'% over trend)'
            if x<0 and -x > down:
                action = 'Buy ('+ str(-x*100)+'% below trend)'
            si =''
            if(delta > 0):
                si = '+'
            fig = pyplot.figure()
            pyplot.title(tickers[j]+' ('+names[j]+') ' + weekday, color='white',fontweight='bold')
            graphtext =  'Price today: ' +str(y[n-1])  + '\n(Change today '+ si + str(delta)+ '%) \n ' + action
            pyplot.ylabel('Price',color='white',fontweight='bold',rotation = 45)
            ax = pyplot.gca()
            pyplot.text(0.95,0.95,graphtext,horizontalalignment='right',verticalalignment='top',transform = ax.transAxes,color='blue',fontweight='bold')
            pyplot.grid()
            graph = fig.add_subplot(111)
            graph.patch.set_facecolor('cyan')
            graph.tick_params(axis='x', colors='blue')
            graph.tick_params(axis='y', colors='black')
            graph.plot_date(t,y,'-',color='red',label= tickers[j])
            graph.plot_date(t_date_trend, y_lin, '--', fillstyle='none',color='blue', label='xxoooooooooooooooooo')
            pyplot.gcf().autofmt_xdate()
            fig.show()
            pyplot.savefig(tickers[j]+'.png')
        messagebox.showinfo("showinfo",'\nClose all graph windows')
        pyplot.close('all')

def stocks_splits(datafile, tickers,names,matr):
    print('Opening the stocks split information file')
    try:
        f = open('stocks_splits.csv', 'r')
    except:
        tkinter.messagebox.showinfo("showinfo", "File " + 'stocks_splits.csv'+ ' is not available')
    print('Creating lists of tics, dates and split factors')
    tics = []
    sdates =[]
    sfactor =[]
    line = "_"
    while (len(line) >0):
        line = f.readline().strip()  # stripping end symbol/n
        if len(line) == 0 :
            tkinter.messagebox.showinfo("showinfo", "File " + 'stocks_splits.csv' + ' is empty (no stock splits to register)')
            return 0
        line_split = line.split(',')
        if len(line_split) > 1:
            tics.append(line_split[0])
            sdates.append(line_split[1])
            sfactor.append(float(line_split[3])/float(line_split[2]))
    f.close()
    print('Registering stock splits in '+ datafile + ' for',tics)
    f = open('stocks_splits_registered.csv', 'a')
    for k in range(len(tics)):
        f.write(tics[k]+','+sdates[k]+','+str(sfactor[k])+'\n')
    f.close()
    print('Deleting all split information from split info file')
    f = open('stocks_splits.csv', 'w')
    f.close()

    for s in range(len(tics)):
        split_tic_number = tickers.index(tics[s])
#        print(s,tics[s],tickers.index(tics[s]),split_tic_number)
        date_s = datetime.datetime.strptime(sdates[s], '%d/%m/%Y')
#        print(s,tics[s],date_s.strftime('%d/%m/%Y'))
        date_num = -1
        for j in range(len(matr)):
            date_j = datetime.datetime.strptime(matr[j][0], '%d/%m/%Y')
            if date_j >= date_s:
                date_num = j
                break
        print(s,date_num,tics[s])
#        print(s,date_s.strftime('%d/%m/%y'),matr[date_num][0])
        if date_num >0:
            for j in range(date_num):
               # print(s,j, matr[j][0],tickers[split_tic_number], matr[j][split_tic_number+1],sfactor[s])
                try:
                    matr[j][split_tic_number+1] = str( float(matr[j][split_tic_number+1]) * float(sfactor[s]) )
                #    print('-',j,matr[j][0], tickers[split_tic_number], matr[j][split_tic_number+1])
                except:
                    print(matr[j][0], tickers[split_tic_number],'!', matr[j][split_tic_number + 1],'!')

    print('Rewriting '+datafile+' with corrections due to stock splits')
    f = open(datafile, 'w')
    for k in range(len(tickers)):
        f.write(tickers[k]+','+names[k]+'\n')
    f.write('#\n')
    for j in range(len(matr)):
        f.write(matr[j][0])
        for k in range(len(tickers)):
            f.write(','+matr[j][k+1])
        f.write('\n')
    f.close()
    msg = 'Stock splits registered in '+ datafile + ' for '
    for k in range(len(tics)):
        msg = msg + tics[k]+', '
    messagebox.showinfo("showinfo",msg)
    return 0

def main(inp):
    if inp[0] != 'Do nothing':
        date = time.strftime("%d/%m/%Y")   # getting present date
        datafile = str( inp[len(inp)-1])
        try:
            f = open(datafile,"r")         # opening historical data
        except IOError:
            tkinter.messagebox.showinfo("showinfo",'The file '+datafile+' is missing')
            return(0)
        line="_"
        tickers = []
        names = []
        matr = []
        num_lines = 0
        count = 0
        while 'TRUE':
            line = f.readline()
            if '#' in line:
                break
            tick,nam = line.strip().split(',')
            tickers.append(tick)
            names.append(nam)
        while 'TRUE':
            line = f.readline()
            if not line:
                break
            if(len(line)>1):
                tokens = line.strip().split(',')           # csv are split to list
                matr.append(tokens)        # loading historicalprices to matr
        f.close()

        if (inp[5] == 'Yes'):
            stocks_splits(datafile, tickers,names,matr)

        print('tickers = ',tickers)

        if inp[0] != 'Show graphs only':
            prices = []
            for i in range(0,len(tickers)):        # for every ticker
                try:
                    if '_' in tickers[i]:
                        tic = tickers[i].split('_')
                        tickers[i] = tic[0]+ tic[1] + '=X'
                    prices.append(ystockquote.get_price(tickers[i]))      # getting price from yahoo financial
        #            ystockquote.get_all('TD')   # gets all information
                except ValueError:
                    prices.append('NA')
            q = []                                # list containing present date and all prices today
            q.append(date)
            for k in range(len(prices)):
                q.append(prices[k])
            matr.append(q)                        # appending today's prices to matr
            f = open(datafile,"a")      # opening data file for appending to it the latest data
            f.write('\n'+q[0])              # next line... first item of 'q'
            for k in range(1,len(q)):
                f.write(', ' + str(q[k]))   # writing to file
            f.close()
            messagebox.showinfo("showinfo",'\nNew prices added to data file')
        dates = []
        delt = []
        date0 = datetime.datetime.strptime(matr[0][0], "%d/%m/%Y").date()     # the oldest date in file
        for i in range(0,len(matr)):
            if(not matr[i][0]==''):
                dates.append(matr[i][0])          # loading all dates to 'dates'
                date_now = datetime.datetime.strptime(matr[i][0], "%d/%m/%Y").date()   # converting data string to data format
                delt.append((date_now - date0).days)                                   # difference in days (converting to days)
                for j in range(1,len(matr[i])):
                    try:
                        matr[i][j] = float(matr[i][j])      # converting string to float
                    except ValueError:
                        matr[i][j] = 'NA'


        if inp[0] ==  'Get quotes and show graphs' or inp[0] == 'Show graphs only':
            make_graphs(tickers,names,delt,matr,inp)        # graphs

        messagebox.showinfo("showinfo",'\nYou may continue or quit')
