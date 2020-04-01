import pandas as pd
import numpy as np
import warnings
import time
from geopy.geocoders import Nominatim
import datetime
import os
import plotly.graph_objs as go
import geopy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

###################################################################
# Initiate Program                                                #
################################################################### 

warnings.filterwarnings("ignore")
print('Current Working Directory : ',os.getcwd())
print('#'*60)
print(' Data Pre-processing Script Started {}'.format(datetime.datetime.now()))

###################################################################
# Read the files                                                  #
################################################################### 
confirmed=pd.read_csv('time_series_covid19_confirmed_global.csv')
deaths=pd.read_csv('time_series_covid19_deaths_global.csv')
recovered=pd.read_csv('time_series_covid19_recovered_global.csv')

lat_lon_data=pd.read_csv('lat_lon_data.csv')

print(' *** Data load completed *** ')

###################################################################
# Clean the Confirmed Cases File                                  #
################################################################### 
# Confirmed Cases Data - Processing
confirmed.drop(columns=['Province/State','Lat','Long'],inplace=True)
cols=list(confirmed)
cols.remove('Country/Region')
confirmed_country_group=confirmed.groupby(['Country/Region'])[cols].sum().reset_index()

print(' *** Data Pre-prossing on confirmed cases completed *** ')

###################################################################
# Clean the Recovery Cases File                                   #
################################################################### 

# Recovery Cases Data - Processing
recovered.drop(columns=['Province/State','Lat','Long'],inplace=True)
cols=list(recovered)
cols.remove('Country/Region')
recovered_country_group=recovered.groupby(['Country/Region'])[cols].sum().reset_index()

print(' *** Data Pre-processing on recovered cases completed *** ')

###################################################################
# Clean the Deaths File                                           #
###################################################################                                 

# Deaths Cases Data - Processing
deaths.drop(columns=['Province/State','Lat','Long'],inplace=True)
cols=list(deaths)
cols.remove('Country/Region')
deaths_country_group=deaths.groupby(['Country/Region'])[cols].sum().reset_index()

print(' *** Data Pre-processing on death cases completed *** ')

###################################################################
# Create the Date file                                            #
###################################################################  
# Create Date list
date_list=list(confirmed_country_group)
date_list.remove('Country/Region')

date_list_formatted=[]
for i in date_list:
    date_list_formatted.append((datetime.datetime.strptime(i, '%m/%d/%y')).date().isoformat())

max_date=max(date_list_formatted)

print(' *** Latest Date of the Data: ', max_date)
print(' *** Starting the Transformation of Data *** ')

###################################################################
# Transform Confirmed Cases Data                                  #
###################################################################  

countries_list=confirmed_country_group['Country/Region'].unique()
col_tran=list(confirmed_country_group)
col_tran.remove('Country/Region')

confirmed_cases_frame=pd.DataFrame()
for i in  countries_list:
    data_points=confirmed_country_group[confirmed_country_group['Country/Region']==i][col_tran].values
    transformed_data=pd.DataFrame(data={'Country':i,
                      'Dates':col_tran,
                    'Confirmed':data_points[0]})
    confirmed_cases_frame=confirmed_cases_frame.append(transformed_data)

confirmed_cases_frame['Dates']=pd.to_datetime(confirmed_cases_frame['Dates'],format='%m/%d/%y')
confirmed_cases_frame['Dates']=confirmed_cases_frame['Dates'].apply(lambda x:x.date())

print(' *** Transformation of confirmed_cases data completed *** ')

###################################################################
# Transform Recovered Cases Data                                  #
###################################################################  

recovered_list=recovered_country_group['Country/Region'].unique()
col_tran=list(recovered_country_group)
col_tran.remove('Country/Region')

recovered_cases_frame=pd.DataFrame()
for i in  recovered_list:
    data_points=recovered_country_group[recovered_country_group['Country/Region']==i][col_tran].values
    transformed_data=pd.DataFrame(data={'Country':i,
                      'Dates':col_tran,
                    'Recovered':data_points[0]})
    recovered_cases_frame=recovered_cases_frame.append(transformed_data)

recovered_cases_frame['Dates']=pd.to_datetime(recovered_cases_frame['Dates'],format='%m/%d/%y')
recovered_cases_frame['Dates']=recovered_cases_frame['Dates'].apply(lambda x:x.date())

print(' *** Transformation of recovered_cases data completed *** ')

###################################################################
# Transform Deaths Cases Data                                     #
###################################################################  

deaths_list=deaths_country_group['Country/Region'].unique()
col_tran=list(deaths_country_group)
col_tran.remove('Country/Region')

deaths_cases_frame=pd.DataFrame()
for i in  deaths_list:
    data_points=deaths_country_group[deaths_country_group['Country/Region']==i][col_tran].values
    transformed_data=pd.DataFrame(data={'Country':i,
                      'Dates':col_tran,
                    'Deaths':data_points[0]})
    deaths_cases_frame=deaths_cases_frame.append(transformed_data)

deaths_cases_frame['Dates']=pd.to_datetime(deaths_cases_frame['Dates'],format='%m/%d/%y')
deaths_cases_frame['Dates']=deaths_cases_frame['Dates'].apply(lambda x:x.date())

print(' *** Transformation of deaths_cases data completed *** ')

print(' *** Transformation of datasets completed *** ')

###################################################################
# Create Latest Data                                              #
################################################################### 

deaths_max_date=deaths_cases_frame[deaths_cases_frame['Dates']==deaths_cases_frame['Dates'].max()]
recovered_max_date=recovered_cases_frame[recovered_cases_frame['Dates']==recovered_cases_frame['Dates'].max()]
confirmed_max_date=confirmed_cases_frame[confirmed_cases_frame['Dates']==confirmed_cases_frame['Dates'].max()]

confirmed_max_date['Dates']=pd.to_datetime(confirmed_max_date['Dates'],format='%Y-%m-%d')

###################################################################
# Set up Latitudes and Longitudes                                 #
###################################################################  

"""
print(' *** Inititating Geo Py to set up Latitutes and Logitudes *** ')
country_list=confirmed_cases_frame['Country'].unique()

def do_geocode(x):
    geopy = Nominatim()
    try:
        return geopy.geocode(x)
    except GeocoderTimedOut:
        return do_geocode(x)

vals=[]
keys=[]

start_time=datetime.datetime.now()
print(' *** Geo Py code Starting *** ')

for i in country_list:
    location=do_geocode(i)
    keys.append(i)
    vals.append([location.latitude,location.longitude])

print(' *** Geo Py code Ended. total elapsed time {} *** '.format(start_time-datetime.datetime.now()))

dictionary=dict(zip(keys,vals))
def latitude_extractor(x):
    return dictionary[x][0]
def longitude_extractor(x):
    return dictionary[x][1]

confirmed_cases_frame['latitude']=confirmed_cases_frame['Country'].map(latitude_extractor)
confirmed_cases_frame['longitudes']=confirmed_cases_frame['Country'].map(longitude_extractor)

print(' *** Geo Py coding ended successfully. Saving the Files *** ')
"""
lat_lon_data.drop(columns=['Unnamed: 0'],inplace=True)
confirmed_max_date=confirmed_max_date.merge(lat_lon_data,on='Country')


###################################################################
# Save Files                                                      #
################################################################### 
# Save all the files 
# Save Confirmed, Received and Death cases  (# Plots - 1,2,3 and 5 - Time line curves)

confirmed_cases_frame.to_csv('pre_processed_confirmed_cases.csv')
recovered_cases_frame.to_csv('pre_processed_recovered_cases.csv')
deaths_cases_frame.to_csv('pre_processed_deaths_cases.csv')

# Save Confirmed, Received and Death cases for Max date  (# Plot 4 and 6 - Map)

confirmed_max_date.to_csv('pre_processed_confirmed_max_date.csv')
recovered_max_date.to_csv('pre_processed_recovered_max_date.csv')
deaths_max_date.to_csv('pre_processed_deaths_max_date.csv')

print(' All the Files Saved. Program Ended Successfully *** ')

print('#'*60)