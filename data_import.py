# -*- coding: utf-8 -*-
""""
basic data import script to make plots in python.
for a guide on how to install python and packages, see
https://github.com/stefanfluck/palmpy/blob/master/docs/palmpy-documentation.md#python-environment

"""

import pandas as pd

#%% create a data frame for your sensor data
tempfile = r'C:/Users/fluf/Desktop/Sensirion_MyAmbience_SHT40_Gadget_5CCC_2022-04-22T13-08-53.813128.edf' #note the / and the r'' structure.

df = pd.read_csv(tempfile, sep='\t', skiprows=9, encoding = "ISO-8859-1")
df['T'] = df['T'].astype(float)

# df['T'].plot()

df.columns #check names of your columns
df.columns = ['epoch','datetime','temp','rh'] #rename columns
df.datetime.dtype #check if datetime column is a timestamp. it's not yet (its an object now)
df['datetime'] = pd.to_datetime(df.datetime) #turn it into timestamp
df.set_index(df.datetime, inplace=True) #set it as an index instead of 0,1,2,3...
df = df.drop(columns='datetime') #drop the one you just promoted to index

df = df.resample('2s').ffill().dropna() #make the timestamp exact to the second
df = df.asfreq('1s') #increase resolution of the dataframe to 1s
df = df.interpolate('linear') #interpolate the missing values now.


#%% import your drone telemetry data, same way

logfile = r''

drone = pd.read_csv(...)


#%% merge the two dataframes on the index using either pd.join, pd.merge or pd.concat.
# I would suggest looking into pd.join first. you want to join your two dataframes on the index.


#%% plotting
import matplotlib.pyplot as plt

df['2022-04-22 12:55:40':'2022-04-22 12:59:30'].temp.plot() #simple

fig = plt.figure()
ax = fig.gca()
df['2022-04-22 12:55:40':'2022-04-22 12:59:30'].temp.plot(ax=ax)
ax.set_ylim([13.7,19.7])
ax.set_title('testitest')
ax.set_ylabel('temperatur')
ax.set_xlabel('time')
ax.grid()